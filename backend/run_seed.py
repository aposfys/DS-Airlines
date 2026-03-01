import asyncio
from app.database import client
from app.seed import seed_data

async def run():
    await seed_data()
    client.close()

if __name__ == "__main__":
    asyncio.run(run())
