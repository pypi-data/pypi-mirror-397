import asyncio

from mtmai.mtmai_app import app


@app.command()
def daytona_sandbox():
    from mtmai.daytona_utils import daytona_run

    asyncio.run(daytona_run())
