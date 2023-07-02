import grpc
import asyncio
from concurrent import futures

from pymongo import MongoClient

from coinflip import coinflip_pb2_grpc # noqa
from coinflip.coinflip_server import CoinFlip

from roulette import roulette_pb2_grpc
from roulette.roulette_server import RouletteService
from roulette.roulette_controller import RouletteController

from balance_client import balance_client_pb2_grpc
import redis

redis_ecp_pool = redis.ConnectionPool(host="redis_ecp", port=6379, db=0, decode_responses=True)
mongo_connection = MongoClient("mongodb://admin:pass@mongo:27017/")


async def start_grpc_server(balance_stub):

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    roulette_pb2_grpc.add_RouletteServicer_to_server(RouletteService(balance_stub, redis_ecp_pool), server)
    coinflip_pb2_grpc.add_CoinflipServicer_to_server(CoinFlip(balance_stub, redis_ecp_pool, mongo_connection), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    try:
        await server.wait_for_termination()
    except:
        await server.stop(None)


async def main():
    balance_notif_channel = grpc.insecure_channel('notifbalance:50051')
    balance_stub = balance_client_pb2_grpc.BalanceStub(balance_notif_channel)
    Roulette = RouletteController(balance_stub, redis_ecp_pool, mongo_connection)

    tasks = [Roulette.game_loop(), start_grpc_server(balance_stub)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
