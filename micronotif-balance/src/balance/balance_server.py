from typing import Tuple, List

from . import balance_pb2
from . import balance_pb2_grpc
from utils import validate_token, validate_balance_bet
import redis
import asyncio
from typing import Union
from itertools import chain


class BalanceService(balance_pb2_grpc.BalanceServicer):
    def __init__(self, redis_pool, pg_pool):
        self.redis_client = redis.Redis(connection_pool=redis_pool)
        self.postgres_pool = pg_pool

    def token_validation(self, token) -> Union[None, str]:
        user_id = validate_token(token)
        if not bool(user_id):
            return None

        if not self.redis_client.get(f"token:{user_id}"):
            return None
        return user_id

    def ValidateToken(self, request, context):
        """ Verifies access tokens, returns user if it is valid (authenticated) else throws an error"""
        user_id = self.token_validation(request.token)

        if not bool(user_id):
            return balance_pb2.StandardResponse(
                success=False,
                error="invalid_token"
            )
        if not (request.bet_amount is None) and request.bet_amount > 0:
            has_sufficient_funds = validate_balance_bet(user_id, request.bet_amount, self.redis_client)
            if has_sufficient_funds:
                return balance_pb2.StandardResponse(
                    success=True,
                    data=user_id,
                    error="null"
                )
            else:
                return balance_pb2.StandardResponse(
                    success=False,
                    error="insufficient_balance"
                )
        return balance_pb2.StandardResponse(
            success=True,
            data=user_id,
            error="null"
        )

    def remove_balance_add_xp_cache(self, user_id: str, amount: int, add_xp=False) -> dict:
        user_data_key = f"user_data:{user_id}"
        with self.redis_client.pipeline(transaction=True) as tr:
            tr.hincrby(user_data_key, "balance", -amount)
            if add_xp:
                tr.hincrby(user_data_key, "xp", amount)
            else:
                tr.hget(user_data_key, "xp")
            tr.delete(f"token:{user_id}")
            data = tr.execute()
        return {
            "user_id": user_id,
            "balance": data[0],
            "xp": int(data[1]),
        }

    async def _save_in_postgres_bulk(self, data: List[dict]):
        with self.postgres_pool.getconn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("BEGIN")
                    query = "UPDATE public.user SET balance = %s, xp = %s WHERE id = %s"
                    values = [(item['balance'], item['xp'], item['user_id']) for item in data]
                    cur.executemany(query, values)
                    cur.execute("COMMIT")
                except Exception as e:
                    cur.execute("ROLLBACK")
                    raise e
            self.postgres_pool.putconn(conn)

    async def _run_syncronize(self, bet_data: List[dict], for_winners=False, add_xp=False) -> list:
        data_for_pg = []
        data_for_response = []
        with self.redis_client.pipeline(transaction=True) as tr:
            if for_winners:
                # winnerebshi redisic davaupdatod da postgrec
                # xps momateba ar gvchirdeba imitoro roca beti daido mashin gavzardet
                for item in bet_data:
                    user_data_key = f"user_data:{item['user_id']}"
                    tr.hincrby(user_data_key, "balance", item['amount']) # Increase winner balance
                    if add_xp:
                        tr.hincrby(user_data_key, "xp", (item['amount'])//2)
                    else:
                        tr.hget(user_data_key, "xp")
                    balance, xp = tr.execute()
                    data = {"balance": int(balance), "xp": int(xp), "user_id": item['user_id']}
                    data_for_pg.append(data)
                    data_for_response.append(balance_pb2.UserBalanceXPData(**data))

            else:
                # loserebshi marto postgre davaupdatot imitoro redisshi ukve chamoklebulia
                for item in bet_data:
                    user_data_key = f"user_data:{item['user_id']}"
                    tr.hget(user_data_key, "balance")
                    if add_xp:
                        tr.hincrby(user_data_key, "xp", (item['amount'] * -1))
                    else:
                        tr.hget(user_data_key, "xp")
                    balance, xp = tr.execute()
                    data = {"balance": int(balance), "xp": int(xp), "user_id": item['user_id']}
                    data_for_pg.append(data)
                    data_for_response.append(balance_pb2.UserBalanceXPData(**data))

        await self._save_in_postgres_bulk(data_for_pg)
        return data_for_response

    async def ConfirmBet(self, request, context):
        user_id = self.token_validation(request.token)
        if not bool(user_id):
            return balance_pb2.ConfirmBetResponse(
                success=False,
                error="invalid_token"
            )
        has_sufficient_funds = validate_balance_bet(user_id, request.bet_amount, self.redis_client)
        if not has_sufficient_funds:
            return balance_pb2.ConfirmBetResponse(
                success=False,
                error="insufficient_balance"
            )
        amount = -request.bet_amount if bool(request.refund) else request.bet_amount
        updated_data = self.remove_balance_add_xp_cache(user_id=user_id, amount=amount, add_xp=bool(request.add_xp))

        return balance_pb2.ConfirmBetResponse(
            success=True,
            data=updated_data,
            error="null",
        )

    async def CommitBettersCoinflip(self, request, context):
        W, L = request.winner, request.loser
        res = await asyncio.gather(
            asyncio.create_task(self._run_syncronize([{"user_id": W.user_id, "amount": W.amount, "xp": W.xp}], for_winners=True, add_xp=True)),
            asyncio.create_task(self._run_syncronize([{"user_id": L.user_id, "amount": -L.amount, "xp": L.xp}], add_xp=True))
        )
        return balance_pb2.CommitBettersBalanceResponse(
            success=True,
            data=list(chain.from_iterable(res)),
            error="null",
        )

    async def CommitBettersBalance(self, request, context):
        winners = []
        losers = []
        for W in request.winners:
            winners.append({
                "user_id": W.user_id,
                "amount": W.amount,
                "xp": W.xp
            })
        for L in request.losers:
            losers.append({"user_id": L.user_id,
                           "amount": -L.amount,
                           "xp": L.xp
                           })

        results = []
        if winners and losers:
            res = await asyncio.gather(
                asyncio.create_task(self._run_syncronize(winners, for_winners=True)),
                asyncio.create_task(self._run_syncronize(losers))
            )
            results.extend(res[0])
        elif winners and not losers:
            res = await asyncio.gather(
                asyncio.create_task(self._run_syncronize(winners, for_winners=True)),
            )
            results.extend(res[0])
        elif not winners and losers:
            await asyncio.gather(
                asyncio.create_task(self._run_syncronize(losers))
            )
        else:
            return balance_pb2.CommitBettersBalanceResponse(
                success=False,
                error="no_winners_or_losers",
            )

        return balance_pb2.CommitBettersBalanceResponse(
            success=True,
            data=results,
            error="null",
        )

        # ---------SCENARIO----------
        # 1. validate request data
        # 2. adjust users balance in redis
        # 3. adjust users balance in postgres
        # 4. save to mongodb (in microgames)
