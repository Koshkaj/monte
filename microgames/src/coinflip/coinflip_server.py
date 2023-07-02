import redis
import hashlib
import secrets
import time
import json
from . import utils
from . import coinflip_pb2
from . import coinflip_pb2_grpc
from balance_client import balance_client_pb2
import asyncio


class CoinFlip(coinflip_pb2_grpc.CoinflipServicer):
    def __init__(self, balance_stub, redis_ecp_pool, mongo_conn):
        self.redis_client = redis.Redis(connection_pool=redis_ecp_pool)
        self.mongo_client = mongo_conn
        self.balance_client = balance_stub

    async def _save_game_async(self, data: dict):
        db = self.mongo_client["coinflip"]
        collection = db["games"]
        collection.insert_one(data)

    async def _send_grpc_commit_request(self, coinflip_round: int, loser: dict, winner: dict):
        winner = balance_client_pb2.UserBetInfo(user_id=winner['user_id'], amount=winner['amount'])
        loser = balance_client_pb2.UserBetInfo(user_id=loser['user_id'], amount=loser['amount'])
        grpc_request = balance_client_pb2.CommitBettersCoinflipRequest(winner=winner, loser=loser)

        result = self.balance_client.CommitBettersCoinflip(grpc_request)
        if not result.success:
            print(result.error) # Log

        for res in result.data:
            self.redis_client.publish(f"notifications:{res.user_id}", json.dumps({"balance": res.balance, "xp": res.xp}))

        self.redis_client.delete(f"coinflip_round:{coinflip_round}")

    def game_result(self, private_seed: str, public_seed: str, round_id: str):
        hash_input = f"{private_seed}-{public_seed}-{round_id}"
        hash_output = hashlib.sha256(hash_input.encode()).hexdigest()
        return (int(hash_output[:8], 16) % 2) + 1

    async def flip_coin(self, coinflip_round: int, data: dict, loser, winner): # es ari realurad animaciis momenti
        save_task = asyncio.create_task(self._save_game_async({**data}))
        db_sync_task = asyncio.create_task(self._send_grpc_commit_request(coinflip_round, loser, winner))

        await asyncio.gather(save_task, db_sync_task, asyncio.sleep(2.5))

    def CreateGame(self, request, context):
        # Validate side
        if not (request.side in (1, 2)):
            return coinflip_pb2.StandardResponse(
                success=False,
                error="invalid_side"
            )
        validate_bet_response = self.balance_client.ValidateToken(
            request=balance_client_pb2.TokenValidateRequest(token=request.token,
                                                            bet_amount=request.bet_amount)
        )
        if not validate_bet_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=validate_bet_response.error
            )
        # Chamovaklot balansi

        user_id = validate_bet_response.data

        confirm_bet_response = self.balance_client.ConfirmBet(
            request=balance_client_pb2.ConfirmBetRequest(token=request.token,
                                                         bet_amount=request.bet_amount))
        if not confirm_bet_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=confirm_bet_response.error
            )

        current_round = int(self.redis_client.get("CURRENT_COINFLIP_ROUND"))
        private_seed = secrets.token_hex(16)
        hashed_private_seed = hashlib.sha256(private_seed.encode()).hexdigest()
        data = {
            "id": current_round,
            "creator": user_id,
            "bet_amount": request.bet_amount,
            "side": request.side,
            "private_seed": private_seed,
            "hashed_private_seed": hashed_private_seed,
            "created_at": int(time.time())
        }
        for key, value in data.items():
            self.redis_client.hset(f"coinflip_round:{current_round}", key, value)

        # Increment current round for next caller
        self.redis_client.incr("CURRENT_COINFLIP_ROUND")
        self.redis_client.publish("intr/coinflip", json.dumps({**data, "private_seed": None, "event": "created"})) #  intr/coinflip

        self.redis_client.publish(f"notifications:{confirm_bet_response.data.user_id}",
                                  json.dumps({"balance": confirm_bet_response.data.balance,
                                              "xp": confirm_bet_response.data.xp}))

        return coinflip_pb2.StandardResponse(
                success=True,
                data=json.dumps({**data, "private_seed": None}),
                error=f"null"
            )

    async def AcceptChallenge(self, request, context):
        token_validate_response = self.balance_client.ValidateToken(request=balance_client_pb2.TokenValidateRequest(token=request.token))
        if not token_validate_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=token_validate_response.error
            )

        coinflip_created_round = self.redis_client.hgetall(f"coinflip_round:{request.round_id}")
        # Security tokeni ro shemowmdes validuroba !!!
        if not coinflip_created_round:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=f"invalid_round"
            )

        creator = coinflip_created_round.get("creator")
        challenger_user_id = token_validate_response.data
        if not creator or creator == challenger_user_id:
            # shenive tamasshi rover shexvide magis validacia
            return coinflip_pb2.StandardResponse(
                success=False,
                error=f"invalid_challenge"
            )

        # Balance chamovachrat challengers tu aq magdeni.
        bet_amount = int(coinflip_created_round.get("bet_amount"))
        confirm_bet_response = self.balance_client.ConfirmBet(
            request=balance_client_pb2.ConfirmBetRequest(token=request.token,
                                                         bet_amount=bet_amount)
        )
        if not confirm_bet_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=confirm_bet_response.error
            )

        eos_block, public_seed = await utils.get_public_seed()
        round_id = request.round_id
        challenger_user_data = {
            "challenger_user_id": challenger_user_id,
            "challenger_side": "1" if coinflip_created_round["side"] != "1" else "2",
            "challenger_token": request.token,
        }
        challenge_data = {
            "id": request.round_id,
            "challenger": json.dumps(challenger_user_data),
            # "public_seed": public_seed,
            "hashed_private_seed": coinflip_created_round["hashed_private_seed"],
            "eos_block": eos_block,
            "challenged_at": int(time.time()),

        }

        game_result = self.game_result(private_seed=coinflip_created_round["private_seed"],
                                       public_seed=public_seed,
                                       round_id=round_id)
        result_data = {**coinflip_created_round,
                       **challenge_data,
                       "public_seed": public_seed,
                       "private_seed": coinflip_created_round["private_seed"],
                       "game_result": game_result}

        self.redis_client.publish("intr/coinflip", json.dumps({**challenge_data, "event": "challenge"}))

        winner = {"amount": int(bet_amount) * 2}  # TODO SAKOMISIO
        loser = {"amount": bet_amount}

        if str(game_result) == challenger_user_data["challenger_side"]:
            # challengerma moigo
            winner["user_id"] = challenger_user_id
            loser["user_id"] = creator
        else:
            winner["user_id"] = creator
            loser["user_id"] = challenger_user_id

        # 3 wami timeout aqedan ...
        # am timeoutis dros unda moxdes shemdegi ragac
        # 1. davaseivot tamashi bazashi
        # 2. gavasuptaod redisi am tamashisgan
        # 3. davaseivot balansebi dbshi
        # 4. timeoutis mere gavushvat result
        await self.flip_coin(coinflip_round=request.round_id,
                             data=result_data,
                             loser=loser,
                             winner=winner)

        self.redis_client.publish("intr/coinflip", json.dumps({**result_data, "event": "result"}))

        return coinflip_pb2.StandardResponse(
            success=True,
            data=json.dumps(result_data),
            error=f"null"
        )

    def CancelGame(self, request, context):
        token_validate_response = self.balance_client.ValidateToken(request=balance_client_pb2.TokenValidateRequest(token=request.token))
        if not token_validate_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=token_validate_response.error
            )
        coinflip_created_round = self.redis_client.hgetall(f"coinflip_round:{request.round_id}")
        creator = coinflip_created_round.get("creator")
        if not creator or token_validate_response.data != creator:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=f"invalid_round"
            )
        confirm_bet_response = self.balance_client.ConfirmBet(
            request=balance_client_pb2.ConfirmBetRequest(token=request.token,
                                                         bet_amount=int(coinflip_created_round["bet_amount"]),
                                                         refund=True))
        if not confirm_bet_response.success:
            return coinflip_pb2.StandardResponse(
                success=False,
                error=confirm_bet_response.error
            )
        data = confirm_bet_response.data
        self.redis_client.publish("intr/coinflip", json.dumps({**coinflip_created_round, "event": "cancel"}))
        self.redis_client.publish(f"notifications:{data.user_id}", json.dumps({"balance": data.balance, "xp": data.xp}))
        self.redis_client.delete(f"coinflip_round:{request.round_id}")
        return coinflip_pb2.StandardResponse(
            success=True,
            data=json.dumps({"round_id": request.round_id}),
            error=f"null"
        )
