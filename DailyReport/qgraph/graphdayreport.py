import logging
import json
import requests
import time
from datetime import datetime
from thegraph.querygraph import querygraph

# Configure logging
logger = logging.getLogger(__name__)

graphurl = \
    "https://api.thegraph.com/subgraphs/name/getprotocol/get-protocol-subgraph"

def graphDayReport(date):
    epochdate = datetime(1970, 1, 1)
    datenumber = (date - epochdate).days
    skip = 0
    events = []
    # Gather data, max 100 entries per time, so keep looping until all data is
    # gathered.
    while True:
        q = '''
        {
            usageEvents(orderBy: id, where:{day:%s}, first:100, skip:%s)
            {
                type
                event{
                    eventName
                    ticketeerName
                }
            }
        }
        ''' % (datenumber, skip)
        data = querygraph(q)
        events = events + data['data']['usageEvents']

        if len(data['data']['usageEvents']) < 100:
            return events
        else:
            skip += 100

