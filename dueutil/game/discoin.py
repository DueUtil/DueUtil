import aiohttp
import generalconfig as gconf
import json

from . import players, stats
from .stats import Stat
from dueutil import util, tasks

import traceback

DISCOIN = "https://discoin.disnodeteam.com"
TRANSACTIONS = "/transaction"
MAKE_TRANSACTION = TRANSACTIONS + "/%s/%s/%s"

headers = {"Authorization": gconf.other_configs["discoinKey"],
           "json": "true"}


async def start_transaction(sender_id, amount, to):
    transaction = DISCOIN + MAKE_TRANSACTION % (sender_id, amount, to)

    with aiohttp.Timeout(10):
        async with aiohttp.ClientSession() as session:
            async with session.get(transaction, headers=headers) as response:
                result = await response.text()
                status = response.status

                if status == 200:
                    return json.loads(result)
                elif status == 401:
                    return {"error": "unauthorized"}
                elif status == 403:
                    return {"error": "unverified", "verify": DISCOIN + "/verify"}
                elif status == 400:
                    if "negative" in result:
                        return {"error": "negative_amount"}
                    elif "currency" in result:
                        return {"error": "currency_not_found"}
                    else:
                        return {"error": "NaN"}
                elif status == 429:
                    # Parse crappy text errors.
                    currency_code = result.split("The currency")[1].split("has a daily")[0].strip()
                    limit_msg_end = "Discoins per user"
                    if "daily total" in result:
                        limit_msg_end = "Discoins."
                    limit = float(result.split("limit of")[1].split(limit_msg_end)[0].strip())

                    can_still = 0
                    if "can still" in result:
                        can_still = result.split("a total of")[1].split("Discoins into")[0].strip()
                        if can_still != "undefined":
                            can_still = float(can_still)
                        else:
                            can_still = 0
                    return {"status": "declined",
                            "currency": currency_code,
                            "limit" + ("Total" if limit_msg_end == "Discoins." else ""): limit,
                            "stillExchangeable": can_still}


async def unprocessed_transactions():
    async with aiohttp.ClientSession() as session:
        async with session.get(DISCOIN + TRANSACTIONS, headers=headers) as response:
            result = await response.text()
            if "[ERROR]" in result:
                return None
            else:
                return json.loads(result)


@tasks.task(timeout=3001111111111111111111111111111111111111)
async def process_transactions():
    util.logger.info("Processing Discoin transactions.")
    try:
        unprocessed = await unprocessed_transactions()
    except Exception as exception:
        util.logger.error("Failed to fetch Discoin transactions: %s", exception)
        return

    if unprocessed is None:
        return

    client = util.shard_clients[0]

    for transaction in unprocessed:

        user_id = transaction.get('user')
        receipt = transaction.get('id')
        source_bot = transaction.get('from')
        amount = transaction.get('amount')

        player = players.find_player(user_id)
        if player is None or amount < 1:
            # This does not really work but it's the best I can do.
            refund = await start_transaction(user_id, amount, source_bot)
            if "error" not in refund:
                util.logger.warning("Discoin transaction failed! receipt %s (refund attempted)", receipt)
                await util.duelogger.concern(("Failed to process discoin transaction from %s with receipt ``%s``\n"
                                              + "Refund attempted.") % (user_id, receipt))
            else:
                util.logger.warning("Discoin transaction %s failed! Refund failed (%s)", receipt, refund["error"])
            client.run_task(notify_complete, user_id, transaction, failed=True)
            return

        amount = int(amount)

        client.run_task(notify_complete, user_id, transaction)

        player.money += amount
        stats.increment_stat(Stat.DISCOIN_RECEIVED, amount)
        player.save()

        util.logger.info("Processed discoin transaction %s", receipt)
        await util.duelogger.info("Discoin transaction with receipt ``%s`` processed.\n" % receipt
                                  + "User: %s | Amount: %.2f | Source: %s" % (user_id, amount, source_bot))


async def notify_complete(user_id, transaction, failed=False):
    client = util.shard_clients[0]
    user = await client.get_user_info(user_id)
    try:
        await client.start_private_message(user)
        if not failed:
            amount = int(transaction["amount"])
            await util.say(user,
                           (":white_check_mark: You've received ``%s`` from Discoin (receipt %s)!\n"
                            % (util.format_number(amount, full_precision=True, money=True), transaction["id"])
                            + "You can see your full exchange record at <"+DISCOIN+"/record>."), client=client)
        else:
            await util.say(user, ":warning: Your Discoin exchange failed (receipt %s)!\n" % transaction["id"]
                           + "To exchange to DueUtil you must be a player "
                           + "and the amount has to be worth at least 1 DUT.", client=client)
    except Exception as error:
        util.logger.error("Could not notify discoin complete %s", error)
        traceback.print_exc()
