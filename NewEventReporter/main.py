import sys
import os
import logging
import time
from datetime import datetime
from qgraph.newevents import newEvents,updateEvent
from blockmanager.blockmanager import BlockManager
from telegram.telegram import TelegramBot

# Log level 1 is INFO, Log level 2 is Debug
loglevel = int(os.environ.get('loglevel'))
# Telegram API Token and channel
telegramapitoken = os.environ.get('telegramapitoken')
telegramchannel = os.environ.get('eventchannel')
# Load config(s)
blockmanagerconfig = os.environ.get('eventimporterblockmanagerconfig')
mimimumblock = os.environ.get('eventimporterminimumblock')


# Configure the logger
if loglevel == 1:
    loglevel = logging.INFO
elif loglevel == 2:
    loglevel = logging.DEBUG
logging.basicConfig(
    format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    datefmt="%a %d/%m/%Y %H:%M:%S",
    level=loglevel,
    stream=sys.stdout)

# Initialize logger
logger = logging.getLogger(__name__)
logger.info('Start New Events Processor')

# Initialize bot
tg = TelegramBot(telegramapitoken,telegramchannel)

# Initialize blockmanager
bm = BlockManager(blockmanagerconfig,mimimumblock)

def createMsg(event, eventisupdated):
    if eventisupdated:
        msg = "Event updated: "
    else:
        msg = "New event registered: "
    msg += (
        "New event registered: <b>{eventname}</b>\n"
        "TX Polygon Chain: "
        "<a href=\"https://polygonscan.com/tx/{transactionhash}\">"
        "link</a>\n"
        "Website: {shopurl}\n"
        "Date: {date}\n"
        "Ticketeer: {ticketeer}").format(
        eventname=event['event']['eventName'],
        transactionhash=event['txHash'],
        shopurl=event['event']['shopUrl'],
        date=datetime.fromtimestamp(int(event['event']['startTime'])).strftime(
            '%Y-%m-%d %H:%M'),
        ticketeer=event['event']['ticketeerName']
    )
    return msg


def processNewEvents():
    fromBlockNumber= bm.get_processedblock()
    events = newEvents(fromBlockNumber)
    for e in events:
        logger.info("New event found. TX: {}, Name: {}".format(
            e['txHash'], e['event']['eventName']
        ))
        eventisupdated = updateEvent(e['eventAddress'],e['blockNumber'])
        logger.info('Event is updated: {}'.format(eventisupdated))

        msg = createMsg(e, eventisupdated)
        if '.' in e['event']['imageUrl']:
            tg.sendphoto(e['event']['imageUrl'], msg)
        else:
            tg.sendmessage(msg)
        bm.set_processedblock(e['blockNumber'])

while True:
    processNewEvents()
    logger.info('End run: Sleep 60 seconds')
    time.sleep(60)