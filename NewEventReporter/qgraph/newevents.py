import logging
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


def newEvents(fromBlockNumber):
    skip = 0
    events = []
    # Gather data, max 100 entries per time, so keep looping until all data is
    # gathered.
    while True:
        q = '''
        {
            usageEvents (
                where: {
                    type: "NEW_EVENT",
                    blockNumber_gt: %s
                },
                first: 100
                skip: %s
            )
            {
                event {
                    eventName,
                    imageUrl,
                    shopUrl,
                    startTime,
                    ticketeerName
                },
                type,
                eventAddress,
                blockNumber,
                txHash
            }
        }
        ''' % (fromBlockNumber, skip)

        data = querygraph(q)

        events = events + data['data']['usageEvents']

        if len(data['data']['usageEvents']) < 100:
            sortedevents = sorted(events, key=lambda d: int(d['blockNumber']))

            return sortedevents
        else:
            skip += 100
