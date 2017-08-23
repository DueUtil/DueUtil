import json

import generalconfig
from . import util

config = generalconfig.other_configs

CARBON_BOT_DATA = "https://www.carbonitex.net/discord/data/botdata.php"
DISCORD_BOTS = "/api/bots/213271889760616449/stats"

DISCORD_LIST = "https://bots.discord.pw"
BOTS_ORG = "https://discordbots.org"


async def update_server_count(shard):

    await _carbon_server(shard)
    await _shard_count_update(shard, DISCORD_LIST, config["discordBotsKey"])
    await _shard_count_update(shard, BOTS_ORG, config["discordBotsOrgKey"])


async def _carbon_server(shard):

    headers = {"content-type": "application/json"}
    total_server_count = util.get_server_count()
    carbon_payload = {"key": config["carbonKey"], "servercount": total_server_count}
    async with shard.http.post(CARBON_BOT_DATA, data=json.dumps(carbon_payload), headers=headers) as response:
        util.logger.info("Carbon returned %s status for the payload %s" % (response.status, carbon_payload))


async def _shard_count_update(shard, site, key):

    # Seems like there is some from of standard?
    headers = {"content-type": "application/json",
               'authorization': key}
    payload = {"server_count": len(shard.servers),
               "shard_id": shard.shard_id,
               "shard_count": len(util.shard_clients)}
    async with shard.http.post(site+DISCORD_BOTS, data=json.dumps(payload), headers=headers) as response:
        util.logger.info(site+" returned %s for the payload %s" % (response.status, payload))
