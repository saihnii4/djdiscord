import requests
import os

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
