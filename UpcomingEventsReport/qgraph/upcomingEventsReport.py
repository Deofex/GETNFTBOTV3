import logging
from datetime import timedelta
from thegraph.querygraph import querygraph

# Configure logging
logger = logging.getLogger(__name__)

def updateEvent(eventaddress, blocknumber):
    q = '''
    {
        usageEvents (
            where: {
                eventAddress: "%s",
                blockNumber_gt: %s
                type: "NEW_EVENT"
            }
        )
        {
            id
        }
    }
    ''' % (eventaddress, blocknumber)
    data = querygraph(q)
    if len(data['data']['usageEvents']) > 1:
        return True
    else:
        return False


def upcomingEventsReport(startdate):
    enddate = startdate + timedelta(days=7)
    startdateepoch = int(startdate.timestamp())
    enddateepoch = int(enddate.timestamp())
    skip = 0
    events = []
    # Gather data, max 100 entries per time, so keep looping until all data is
    # gathered.
    while True:
        q = '''
        {
            events (
            where: {
                startTime_gt: %s,
                startTime_lt: %s,
                mintCount_gt: 0,
            },
            first:100,
            skip:%s
            orderBy: mintCount, orderDirection: desc
        )
        {
        eventName,
        mintCount,
        startTime,
        ticketeerName
        }
        }
        ''' % (startdateepoch, enddateepoch, skip)

        data = querygraph(q)
        events = events + data['data']['events']

        if len(data['data']['events']) < 100:
            return events
        else:
            skip += 100

