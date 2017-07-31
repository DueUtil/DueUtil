import aiohttp
import generalconfig as gconf

DISCOIN = "http://discoin-austinhuang.rhcloud.com"
TRANSACTIONS = "/transaction"
MAKE_TRANSACTION = TRANSACTIONS+"/%s/%s/%s"

# TODO: Wait till Discoin returns JSON
headers = {"Authorization": gconf.other_configs["discoinKey"],
           "json": "true"}

async def start_transaction(sender, amount, to):

    transaction = DISCOIN+MAKE_TRANSACTION % (sender.id, amount, to)

    async with aiohttp.ClientSession() as session:
        async with session.get(transaction, headers=headers) as response:
            result = await response.text()
            print(result, response.status, type(response.status))


async def process_transactions():

    async with aiohttp.ClientSession() as session:
        async with session.get(DISCOIN+TRANSACTIONS, headers=headers) as response:
            result = await response.text()
            print(result)
