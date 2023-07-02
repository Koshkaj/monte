import grpc
import asyncio
from concurrent import futures

import psycopg2
from psycopg2 import pool
from balance import balance_pb2_grpc
from balance.balance_server import BalanceService

import redis


async def start_grpc_server():
    redis_pool_nbc = redis.ConnectionPool(host="redis_nbc", port=6379, db=0, decode_responses=True)
    pg_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host="postgres",
        database="main",
        user="admin",
        password="pass"
    )
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    balance_pb2_grpc.add_BalanceServicer_to_server(BalanceService(redis_pool_nbc, pg_pool), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    try:
        await server.wait_for_termination()
    except:
        await server.stop(None)

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
