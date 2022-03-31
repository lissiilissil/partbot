from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool




class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None


    async def create(self):
        self.pool = await asyncpg.create_pool(
            user="example",
            password="smeliihui",
            host="localhost",
            database="partnerka"
        )


    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql="""
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NULL,
        telegram_id BIGINT NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql +=" AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                    start=1)
        ])
        return sql, tuple(parameters.values())

    async def select_all_users(self):
        sql="SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE telegram_id=$1"
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def delete_all_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_table(self):
        await self.execute("DROP TABLE Users", execute=True)
