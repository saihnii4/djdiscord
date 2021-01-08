import asyncio
import os
import unittest

import pytest
import rethinkdb


@pytest.fixture(scope="class")
def event_loop(request):
    request.cls.loop = asyncio.get_event_loop()
    yield request.cls.loop
    request.cls.loop.close()


@pytest.mark.usefixtures("event_loop")
class DatabaseTest(unittest.TestCase):
    def test_rethinkdb_async(self) -> None:
        rethinkdb.r.set_loop_type("asyncio")

        async def _conn_db() -> None:
            return await rethinkdb.r.connect(
                db="test",
                user=os.environ["RETHINKDB_USER"],
                password=os.environ["RETHINKDB_PASS"],
                host=os.environ["RETHINKDB_HOST"],
                port=os.environ["RETHINKDB_PORT"])

        assert self.loop.run_until_complete(_conn_db())
