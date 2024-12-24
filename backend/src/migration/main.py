import asyncio
import argparse
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from .action import *
from ..config import *


DATABASE_URL=f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL)


async def drop_tables():
    async with engine.begin() as conn:
        for sql in drop_tables_sql:
            await conn.execute(text(sql))
    await engine.dispose()


async def create_tables():
    async with engine.begin() as conn:
        for sql in create_tables_sql:
            await conn.execute(text(sql))
    await engine.dispose()



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, required=True)
    args = parser.parse_args()
    action = args.action
    
    if action == 'create':
        asyncio.run(create_tables())
        logging.info("Tables were created.")
    elif action == 'drop':
        asyncio.run(drop_tables())
        logging.info("Tables were droped.")
