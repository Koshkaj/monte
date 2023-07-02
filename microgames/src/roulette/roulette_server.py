import grpc
import json
from . import roulette_pb2
from . import roulette_pb2_grpc
from balance_client import balance_client_pb2
import redis


# Todo : redisis userma ro marto icodes incrementi current_roulette_round ze da coinflip_round ze
# ACL SETUSER current_round_user -PASSWORD mypassword
# ACL SETUSER current_round_user +@read $CURRENT_ROUND_ID
# ACL SETUSER current_round_user +@write INCR $CURRENT_ROUND_ID


class RouletteService(roulette_pb2_grpc.RouletteServicer):
    def __init__(self, balance_stub, redis_ecp_pool):
        self.balance_client = balance_stub
        self.redis_client = redis.Redis(connection_pool=redis_ecp_pool)

    def GetState(self, request, context):
        current_round_id = self.redis_client.get("CURRENT_ROULETTE_ROUND")
        bet_data = list(self.redis_client.smembers(f"roulette_round:{current_round_id}_bets"))
        bet_counts = self.redis_client.hgetall(f"roulette_round:{current_round_id}_count")
        bet_amounts = self.redis_client.hgetall(f"roulette_round:{current_round_id}_amount")
        previous_100_rolls = self.redis_client.lrange("ROULETTE_LAST_100", 0, -1)

        bets = {"ct": [], "t": [], "zero": []}

        for item in bet_data:
            item_data = json.loads(item)
            bets[item_data["side"]].append(item_data)

        timer = self.redis_client.pttl(f"roulette_round:{current_round_id}_timer")
        if timer == -2:
            timer = 0

        data = {
            "event": "roulette/init",
            "round": current_round_id,
            "rolls": previous_100_rolls,
            "bets": bets,
            "count": bet_counts,
            "amount": bet_amounts,
            "timer": timer
        }
        return roulette_pb2.StandardResponse(
            success=True,
            data=json.dumps(data),
            error="null"
        )

    def PlaceBet(self, request, context):
        if request.coin not in ("ct", "t", "zero"):
            return roulette_pb2.StandardResponse(
                success=False,
                error=f"invalid_coin"
            )

        current_round_id = self.redis_client.get("CURRENT_ROULETTE_ROUND")
        bet_multiplier = self.redis_client.get(f"roulette_round:{request.round_id}_bet_multiplier")
        if current_round_id != request.round_id and not (bet_multiplier in ("2", "14")): # Exlandeli raundi unda iyos da dadeba unda sheilebodes am raundze
            return roulette_pb2.StandardResponse(
                success=False,
                error=f"invalid_round"
            )

        # amowmebs tokenis validurobas da bet is validurobas ertdroulad (balance unda iyos meti an toli betis)
        validate_bet_response = self.balance_client.ValidateToken(
            request=balance_client_pb2.TokenValidateRequest(token=request.token,
                                                            bet_amount=request.amount)
        )
        if not validate_bet_response.success:
            return roulette_pb2.StandardResponse(
                success=False,
                error=validate_bet_response.error
            )
        user_id = validate_bet_response.data

        confirm_bet_response = self.balance_client.ConfirmBet(
            request=balance_client_pb2.ConfirmBetRequest(token=request.token,
                                                         bet_amount=request.amount)
        )
        if not confirm_bet_response.success:
            return roulette_pb2.StandardResponse(
                success=False,
                error=confirm_bet_response.error
            )

        self.redis_client.publish("intr/roulette", json.dumps({"event": "bet",
                                                               "round": request.round_id,
                                                               "amount": request.amount,
                                                               "side": request.coin}))

        self.redis_client.hincrby(f"roulette_round:{current_round_id}_amount", request.coin, request.amount)
        self.redis_client.hincrby(f"roulette_round:{current_round_id}_count", request.coin, 1)
        self.redis_client.publish(f"notifications:{confirm_bet_response.data.user_id}",
                                  json.dumps({"balance": confirm_bet_response.data.balance,
                                              "xp": confirm_bet_response.data.xp}))

        bet_data = json.dumps({
            "amount": request.amount,
            "side": request.coin,
            "user_id": user_id
            # temporary data
        })

        # Rogorcki beti shemovida, vinaidan am raundis outcome vicit, barem chavyarot mogebulebshi da (balance adjustment)

        # yvela validaciam tu gaiara, gamovaklot balancs imdeni amounti ramdenic shemovida, user balance unda iyos LOCKED
        # pseudo: user.balance = user.balance - amount
        winner_side = self.redis_client.hmget(f"roulette_round:{current_round_id}", "result")
        balance_adjustment_data = {
            "user_id": user_id,
            "amount": request.amount,
            "xp": request.amount
        }
        if winner_side[0] == request.coin:
            # am tipma vinc beti shemoitana, moigo da chavyarot mogebulebshi
            # vicit ramdeni multiplierit moigo, tu 14 ia anu zerom moigo tu 2 coinma
            # user balance LOCKED unda iyos ro race conditioni aviridot sanam vaupdatebt balancs
            # pseudo : user.balance = user.balance + amount * int(bet_multiplier)
            # chavyarot queueshi romelic gatrigerdeba roca ruletka morcheba, anu roca "end" eventi gaisvris

            # TODO Mongos mivcet useris game history

            self.redis_client.sadd(f"roulette_round:{current_round_id}_winners", bet_data)

            balance_adjustment_data["amount"] = (request.amount * int(bet_multiplier))
            self.redis_client.sadd(f"roulette_round:{current_round_id}_winner_bets", json.dumps(balance_adjustment_data))
        else:
            self.redis_client.sadd(f"roulette_round:{current_round_id}_loser_bets", json.dumps(balance_adjustment_data))

        self.redis_client.sadd(f"roulette_round:{current_round_id}_bets", bet_data)
        return roulette_pb2.StandardResponse(
            success=True,
            data=bet_data,
            error=f"null"
        )

