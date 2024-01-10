import httpx


async def get_async_client():
    # Asynchronous client to be used as a dependency in calls to the ECEO API
    async with httpx.AsyncClient() as client:
        yield client
