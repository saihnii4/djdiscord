import dotenv
import requests
import rethinkdb
import os

dotenv.load_dotenv()

if "progress.png" not in os.listdir("./assets"):
    with open("./assets/progress.png", "wb") as progress:
        progress.write(
            requests.get(
                "https://notduckduckcode.github.io/djdiscord/assets/progress.png"
            ).content
        )

if "logo.png" not in os.listdir("./assets"):
    with open("./assets/logo.png", "wb") as logo:
        logo.write(
            requests.get(
                "https://notduckduckcode.github.io/djdiscord/assets/logo.png"
            ).content
        )

with open("./Lavalink.jar", "wb") as lavalink:
    lavalink.write(
        requests.get(
            "https://github.com/Frederikam/Lavalink/releases/download/3.3.2.3/Lavalink.jar"
        ).content
    )

database = rethinkdb.r.connect(
    db="djdiscord",
    host=os.environ["RETHINKDB_HOST"],
    port=os.environ["RETHINKDB_PORT"],
    user=os.environ["RETHINKDB_USERNAME"],
    password=os.environ["RETHINKDB_PASSWORD"],
)

rethinkdb.r.db_create("djdiscord").run(database)

rethinkdb.r.db("djdiscord").table_create("playlists").run(database)

rethinkdb.r.db("djdiscord").table_create("stations").run(database)

rethinkdb.r.db("djdiscord").table_create("logs").run(database)

rethinkdb.r.db("rethinkdb").table("users").insert(
    {"id": "djdiscord", "password": os.environ["RETHINKDB_PASSWORD"]}
).run(database)
