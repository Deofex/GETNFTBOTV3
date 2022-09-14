import logging
from datetime import datetime
from thegraph.querygraph import querygraph

# Configure logging
logger = logging.getLogger(__name__)

def graphDayReport(date):
    epochdate = datetime(1970, 1, 1)
    datenumber = (date - epochdate).days
    skip = 0
    minblocknumber = 0
    events = []
    # Gather data, max 100 entries per time, so keep looping until all data is
    # gathered.
    while True:
        # If skip is greated than 5000, set new minimal blocknumber, remove the
        # events which has this blocknumber to avoid incomplete results and
        # reset the skip var.
        if skip > 5000:
            minblocknumber = events[-1]['blockNumber']
            events = [d for d in events \
                if d['blockNumber'] < minblocknumber]
            skip = 0
        q = '''
        {
            usageEvents(
                orderBy: blockNumber,
                where:{day:%s, blockNumber_gte: %s}, first:100, skip:%s
                )
            {
                blockNumber
                type
                event{
                    name
                    integrator {
                        name
                    }
                }
            }
        }
        ''' % (datenumber, minblocknumber, skip)
        data = querygraph(q)
        events = events + data['data']['usageEvents']

        if len(data['data']['usageEvents']) < 100:
            return events
        else:
            skip += 100

