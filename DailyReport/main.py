import sys
import os
import logging
import re
from datetime import datetime, timedelta
from qgraph.graphdayreport import graphDayReport
from reportbuilder.reportbuilder import ReportBuilder
from telegram.telegram import TelegramBot

# Log level 1 is INFO, Log level 2 is Debug
loglevel = int(os.environ.get('loglevel'))
# Telegram API Token and channel
telegramapitoken = os.environ.get('telegramapitoken')
telegramchannel = os.environ.get('eventchannel')


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
logger.info('Start Daily Report Processor')

# Initialize bot
tg = TelegramBot(telegramapitoken,telegramchannel)


def filterdata(data, type):
    # Your ticket provider guid in regex format + counter
    ytpguidregex = '^([0-z]){8}(-([0-z]){4}){3}-([0-z]){12}$'
    filtereddata = {}
    filteredsumcount = 0

    for e in data:
        # If the type is different than specified
        if e['type'] != type:
            continue
        filteredsumcount += 1
        if re.match(ytpguidregex, e['event']['eventName']) and \
                e['event']['ticketeerName'] == 'YourTicketProvider':
            n = 'YourTicketProvider events (nameless)'
        else:
            n = e['event']['eventName']
        # If event exist, update the amount, else create a new entry
        if n in filtereddata.keys():
            filtereddata[n] = filtereddata[n] + 1
        else:
            filtereddata[n] = 1

    # sort events
    sortedfilteredsum = dict(sorted(
        filtereddata.items(), key=lambda item: item[1], reverse=True))
    return sortedfilteredsum, filteredsumcount


def createrapport(data, reportdate):
    rb = ReportBuilder()
    rb.addline("<b>NFT report: {}-{}-{}</b>".format(
        reportdate.day, reportdate.month, reportdate.year))
    rb.addemptyline()
    psalesum, psaletotal = filterdata(data, "MINT")
    if len(psalesum) > 0:
        i = 0
        rb.addline("<b>Tickets sold on the primary market:</b>")
        for k, v in psalesum.items():
            i += 1
            rb.addline("<b>{})</b> {} --> {}".format(
                i, k, v))
        rb.addline('<b>Total Amount: {}</b>'.format(psaletotal))
        rb.addemptyline()
    ssalesum, ssaletotal = filterdata(data, "RESALE")
    if len(ssalesum) > 0:
        i = 0
        rb.addline("<b>Tickets sold on the secondary market:</b>")
        for k, v in ssalesum.items():
            i += 1
            rb.addline("<b>{})</b> {} --> {}".format(
                i, k, v))
        rb.addline('<b>Total Amount: {}</b>'.format(ssaletotal))
        rb.addemptyline()
    tscansum, tscantotal = filterdata(data, "SCAN")
    if len(tscansum) > 0:
        i = 0
        rb.addline("<b>Tickets scanned:</b>")
        for k, v in tscansum.items():
            i += 1
            rb.addline("<b>{})</b> {} --> {}".format(
                i, k, v))
        rb.addline('<b>Total Amount: {}</b>'.format(tscantotal))
        rb.addemptyline()
    tinvalidatedsum, tinvalidatedtotal = filterdata(data, "INVALIDATE")
    if len(tinvalidatedsum) > 0:
        i = 0
        rb.addline("<b>Tickets invalidated:</b>")
        for k, v in tinvalidatedsum.items():
            i += 1
            rb.addline("<b>{})</b> {} --> {}".format(
                i, k, v))
        rb.addline('<b>Total Amount: {}</b>'.format(tinvalidatedtotal))
        rb.addemptyline()

    rb.addline("<a href=\"https://explorer.get-protocol.io/\">"
               "All actions above are performed on getNFTs minted on  "
               "Polygon. View all NFT's in the GET ticket explorer</a>\n")

    return rb.create_report()


def getdayreport():
    ct = datetime.now()
    rd = datetime(ct.year, ct.month, ct.day) - timedelta(days=1)
    logger.info('Get info from TheGraph')
    data = graphDayReport(rd)

    logger.info('Creating report for: {}'.format(rd))

    # Create the report
    report = createrapport(data, rd)
    logger.info('Report created')
    return report

logger.info('Create report message')
msgs = getdayreport()
logger.info('Send message via TG, amount of messages: {}'.format(len(msgs)))
for msg in msgs:
    tg.sendmessage(msg)
