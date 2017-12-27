import aiohttp
import generalconfig as gconf
import json

from . import players, stats
from .stats import Stat
from dueutil import util, tasks

import traceback

# A quick discoin implementation.

DISCOIN = "http://discoin.sidetrip.xyz"
VERIFY = DISCOIN+"/verify"
# Endpoints
TRANSACTION = "/transaction"
TRANSACTIONS = "/transactions"
REVERSE = TRANSACTION+"/reverse"
headers = {"Authorization": gconf.other_configs["discoinKey"]}


async def make_transaction(sender_id, amount, to):

    transaction_data = {
        "user": sender_id,
        "amount": amount,
        "exchangeTo": to
    }

    with aiohttp.Timeout(10):
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCOIN + TRANSACTION,
                                    data=json.dumps(transaction_data), headers=headers) as response:
                return await response.json()


async def reverse_transaction(receipt):

    reverse_data = {"receipt": receipt}

    with aiohttp.Timeout(10):
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCOIN + REVERSE,
                                    data=json.dumps(reverse_data), headers=headers) as response:
                return await response.json()


async def unprocessed_transactions():
    async with aiohttp.ClientSession() as session:
        async with session.get(DISCOIN + TRANSACTION + "s", headers=headers) as response:
            return await response.json()


@tasks.task(timeout=120)
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
        receipt = transaction.get('receipt')
        source_bot = transaction.get('source')
        amount = transaction.get('amount')
        amount = int(amount)

        player = players.find_player(user_id)
        if player is None or amount < 1:
            await reverse_transaction(receipt)
            client.run_task(notify_complete, user_id, transaction, failed=True)
            return

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
                            % (util.format_number(amount, full_precision=True, money=True), transaction["receipt"])
                            + "You can see your full exchange record at <%s/record>." % DISCOIN), client=client)
        else:
            await util.say(user, ":warning: Your Discoin exchange has been reversed (receipt %s)!\n"
                           % transaction["receipt"]
                           + "To exchange to DueUtil you must be a player "
                           + "and the amount has to be worth at least 1 DUT.", client=client)
    except Exception as error:
        util.logger.error("Could not notify discoin complete %s", error)
        traceback.print_exc()
