import secrets
import hashlib
import random
from datetime import timedelta

import redis
import time
import json
import asyncio

from balance_client import balance_client_pb2

BET_PHASE_DELAY = 20

SPIN_DELAY = 6

END_DELAY = 3

ROUND_DELAY = BET_PHASE_DELAY + SPIN_DELAY + END_DELAY


def generate_public_seed(): # temporary
    return "".join([str(random.randint(0, 9)) for _ in range(10)])


def hash_string_to_seed(string):
    return hashlib.sha256(string.encode()).hexdigest()


class RouletteController:
    __slots__ = ("redis_client", "mongo_client", "winner_result", "balance_grpc_client", "previous_rolls", "winner_roll")

    winner_result: str
    winner_roll: int
    previous_rolls: list

    def __init__(self, balance_stub, redis_ecp_pool, mongo_conn):
        self.redis_client = redis.Redis(connection_pool=redis_ecp_pool)
        self.mongo_client = mongo_conn
        self.balance_grpc_client = balance_stub

    async def _save_game_async(self, current_round_id: int):
        db = self.mongo_client["roulette"]
        collection = db["games"]
        previous_round = self.redis_client.hgetall(f"roulette_round:{current_round_id}")
        previous_round['amount'] = self.redis_client.hgetall(f"roulette_round{current_round_id}_amount")
        previous_round['count'] = self.redis_client.hgetall(f"roulette_round{current_round_id}_count")
        previous_round['bets'] = list(self.redis_client.smembers(f"roulette_round:{current_round_id}_bets"))
        previous_round['winners'] = list(self.redis_client.smembers(f"roulette_round:{current_round_id}_winners"))
        collection.insert_one(previous_round)

        self.redis_client.delete(f"roulette_round:{current_round_id}")
        self.redis_client.delete(f"roulette_round:{current_round_id}_winners")
        self.redis_client.delete(f"roulette_round:{current_round_id}_count")
        self.redis_client.delete(f"roulette_round:{current_round_id}_amount")

    @staticmethod
    def generate_result(private_seed, public_seed, round_number) -> (str, int):
        hash_input = f"{private_seed}-{public_seed}-{round_number}"
        hash_output = hashlib.sha256(hash_input.encode()).hexdigest()
        roll = (int(hash_output[:8], 16) % 15)
        if roll == 0:
            winner = "zero"
        elif 1 <= roll <= 7:
            winner = "t"
        else:
            winner = "ct"
        return winner, roll

    def create_roulette_round(self, current_round_id: int):
        # Generate new game
        print(f"-------------------- GAME STARTED: {current_round_id} --------------------")
        public_seed = generate_public_seed()
        private_seed = hash_string_to_seed(secrets.token_hex(16)) # Generacia gavitanot sxvagan

        self.winner_result, self.winner_roll = self.generate_result(public_seed=public_seed,
                                                                    private_seed=private_seed,
                                                                    round_number=current_round_id)

        def create_redis_keys():
            self.previous_rolls = self.redis_client.lrange("ROULETTE_LAST_100", 0, -1)
            self.redis_client.hset(f"roulette_round:{current_round_id}", "round", current_round_id)
            self.redis_client.hset(f"roulette_round:{current_round_id}", "public_seed", public_seed)
            self.redis_client.hset(f"roulette_round:{current_round_id}", "private_seed", private_seed)
            self.redis_client.hset(f"roulette_round:{current_round_id}", "hashed_private_seed", hash_string_to_seed(private_seed))
            self.redis_client.hset(f"roulette_round:{current_round_id}", "result", self.winner_result)
            self.redis_client.hset(f"roulette_round:{current_round_id}", "result_roll", self.winner_roll)
            self.redis_client.set(f"roulette_round:{current_round_id}_bet_multiplier", "2" if self.winner_result in ("ct", "t") else "14")

            # Initialize zero bets and counts
            self.redis_client.hset(f"roulette_round:{current_round_id}_amount", "ct", 0)
            self.redis_client.hset(f"roulette_round:{current_round_id}_amount", "t", 0)
            self.redis_client.hset(f"roulette_round:{current_round_id}_amount", "zero", 0)

            self.redis_client.hset(f"roulette_round:{current_round_id}_count", "ct", 0)
            self.redis_client.hset(f"roulette_round:{current_round_id}_count", "t", 0)
            self.redis_client.hset(f"roulette_round:{current_round_id}_count", "zero", 0)

            self.redis_client.publish("intr/roulette", json.dumps({"event": "rolling",
                                                                   "round": current_round_id,
                                                                   "timestamp": int(time.time()),
                                                                   "rolls": self.previous_rolls,
                                                                   "timer": BET_PHASE_DELAY}))

        create_redis_keys()
        print("-------------------- ROLLING --------------------")

    # spin shi gvaq 7 wami ro movaswrot daseiveba da frontendis animacia
    # Redis shi key ebis deadline 29 wami (20 bet is faza, 6 spin, 3 end idan axal raundamde)
    async def spin(self, current_round_id):
        save_task = asyncio.create_task(self._save_game_async(current_round_id))
        publish_spin = asyncio.create_task(self.publish_spin(current_round_id))
        await asyncio.gather(publish_spin, save_task, asyncio.sleep(SPIN_DELAY))

    async def _send_grpc_commit_request(self, current_round_id: str):
        winners = []
        losers = []
        for winner in list(self.redis_client.smembers(f"roulette_round:{current_round_id}_winner_bets")):
            winner_data = json.loads(winner)
            winner_info = balance_client_pb2.UserBetInfo(user_id=winner_data['user_id'], amount=winner_data['amount'], xp=winner_data['xp'])
            winners.append(winner_info)

        for loser in list(self.redis_client.smembers(f"roulette_round:{current_round_id}_loser_bets")):
            loser_data = json.loads(loser)
            loser_info = balance_client_pb2.UserBetInfo(user_id=loser_data['user_id'], amount=loser_data['amount'], xp=loser_data['xp'])
            losers.append(loser_info)

        grpc_request = balance_client_pb2.CommitBettersBalanceRequest(winners=winners, losers=losers)

        result = self.balance_grpc_client.CommitBettersBalance(grpc_request) # Gaigzavnos queue shi
        if not result.success:
            print(result.error) # Log

        for res in result.data:
            self.redis_client.publish(f"notifications:{res.user_id}", json.dumps({"balance": res.balance, "xp": res.xp}))

        self.redis_client.delete(f"roulette_round:{current_round_id}_winner_bets")
        self.redis_client.delete(f"roulette_round:{current_round_id}_loser_bets")
        self.redis_client.delete(f"roulette_round:{current_round_id}_bets")

        # send winners/losers to grpc to commit

    async def commit_bets_to_db(self, current_round_id, sleep_time):
        bets = self.redis_client.smembers(f"roulette_round:{current_round_id}_bets")
        publish_end = asyncio.create_task(self.publish_end(current_round_id))
        if len(bets) > 0:
            commit_task = asyncio.create_task(self._send_grpc_commit_request(current_round_id))
            # save_bet_to_mongo = asyncio.create_task()
            await asyncio.gather(commit_task, publish_end, asyncio.sleep(sleep_time))
        else:
            await asyncio.gather(publish_end, asyncio.sleep(sleep_time))

    async def publish_end(self, current_round_id):
        self.redis_client.rpush("ROULETTE_LAST_100", self.winner_roll)
        if self.redis_client.llen("ROULETTE_LAST_100") > 100:
            self.redis_client.ltrim("ROULETTE_LAST_100", 1, 100)
        self.previous_rolls = self.redis_client.lrange("ROULETTE_LAST_100", 0, -1)
        self.redis_client.publish("intr/roulette", json.dumps({"event": "end",
                                                               "round": current_round_id,
                                                               "timestamp": int(time.time()),
                                                               "winner": self.winner_result,
                                                               "rolls": self.previous_rolls})) # roulette:States magivrad intr/roulette "event": "end" 3 wamia end idan axal raundamde

    async def publish_spin(self, current_round_id):
        print("-------------------- SPINNING ROUND --------------------")
        self.redis_client.delete(f"roulette_round:{current_round_id}_bet_multiplier") # Ro avkrdzalo dadeba am raundze
        self.redis_client.publish("intr/roulette", json.dumps({"event": "spin",
                                                               "round": current_round_id,
                                                               "timestamp": int(time.time()),
                                                               "next_round": int(current_round_id) + 1,
                                                               "winner": self.winner_result,
                                                               "rolls": self.previous_rolls}))

    async def timeout_roulette_round(self, current_round_id):
        async def set_round_timeout():
            self.redis_client.setex(f"roulette_round:{current_round_id}_timer", timedelta(seconds=BET_PHASE_DELAY), int(time.time()))

        await asyncio.gather(
            asyncio.sleep(BET_PHASE_DELAY),
            asyncio.create_task(set_round_timeout())
        )

    async def game_loop(self):
        while True:
            start = time.perf_counter()
            current_round = self.redis_client.get("CURRENT_ROULETTE_ROUND")
            self.create_roulette_round(current_round_id=int(current_round))
            await self.timeout_roulette_round(current_round_id=current_round) # bet accepting phase
            await self.spin(current_round) # Triggers spin event
            self.redis_client.incr("CURRENT_ROULETTE_ROUND") # Increment for next round
            await self.commit_bets_to_db(sleep_time=(ROUND_DELAY - time.perf_counter() - start), current_round_id=current_round)
            print(f"-------------------- ROUND ENDED  --------------------")

