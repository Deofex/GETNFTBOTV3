import sys
import os
import logging
import re
from datetime import datetime
from qgraph.upcomingEventsReport import upcomingEventsReport
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
logger.info('Start Upcoming Events Processor')

# Initialize bot
tg = TelegramBot(telegramapitoken,telegramchannel)

def ticketeername(ticketeername):
    if ticketeername == 'YourTicketProvider':
        ticketeername = 'YTP'
    return ticketeername

def eventname(eventname, ticketeername):
    if ticketeername == 'YourTicketProvider':
        ytpguidregex = '^([0-z]){8}(-([0-z]){4}){3}-([0-z]){12}$'
        if re.match(ytpguidregex, eventname):
            eventname = 'Name event not disclosed'
    return eventname

def tidyupdata(data):
    tdata = {}
    for e in data:
        if e['eventName'] in tdata:
            tdata[e['eventName']][0] = True
            tdata[e['eventName']][1].append(e['startTime'])
            tdata[e['eventName']][2] += int(e['mintCount'])
        else:
            edata = [
                False,
                [e['startTime'],],
                int(e['mintCount']),
                ticketeername(e['ticketeerName']),
                eventname(e['eventName'],e['ticketeerName'])
            ]
            tdata[e['eventName']] = edata

    tldata = []
    for k,v in tdata.items():
        tldata.append({
            'eventName': k,
            'multiEvent': v[0],
            'startTime': v[1],
            'mintCount': v[2],
            'ticketeerName':v[3],
            'displayName':v[4]
        })

    tldata = sorted(
        tldata, key=lambda e: e['mintCount'], reverse=True)
    return tldata


def createrapport(tdata):
    msgs = []
    msg = ('<b>Upcoming event report</b>\nIn the upcoming 7 days, the '
        'following events will take place:\n\n')
    for e in tdata:
        if e['multiEvent'] == True:
            msgp = ('<b>{eventName}</b>\n   Date: {occurrences} occurrences\n'
                    '   Ticketeer: {ticketeerName}\n'
                    '   Tickets sold:{mintCount}\n'.format(
                        eventName=e['displayName'],
                        occurrences=len(e['startTime']),
                        ticketeerName=e['ticketeerName'],
                        mintCount=e['mintCount']
                    ))
        else:
            edate =datetime.fromtimestamp(int(e['startTime'][0]))
            msgp = ('<b>{eventName}</b>\n   Date: {startTime}\n'
                    '   Tickets sold: {mintCount}\n'
                    '   Ticketeer: {ticketeerName}\n'.format(
                        eventName=e['displayName'],
                        startTime=edate.strftime('%d-%m-%Y'),
                        ticketeerName=e['ticketeerName'],
                        mintCount=e['mintCount']
                    ))
        if len(msg) + len(msgp) > 4000:
            msgs.append(msg)
            msg = msgp
        else:
            msg += msgp
    msgs.append(msg)

    fmsgs = []
    if len(msgs) > 1:
        i = 1
        for msg in msgs:
            prefix = "Message {}/{}\n\n".format(i,len(msgs))
            i += 1
            fmsgs.append(prefix + msg)
    else:
        fmsgs = msgs

    return fmsgs


logger.info('Start report run, collect data from TehGraph')
data = upcomingEventsReport(datetime.now())
logger.info('Tidyup data')
tdata = tidyupdata(data)
logger.info('Create Report Message(s)')
msgs = createrapport(tdata)
logger.info("Sending messages via TG (total messages: {})".format(len(msgs)))
for msg in msgs:
    tg.sendmessage(msg)

