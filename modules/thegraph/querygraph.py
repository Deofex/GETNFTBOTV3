import requests
import json
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)


graphurl = \
    "https://api.thegraph.com/subgraphs/name/getprotocol/get-protocol-subgraph-deprecated"


def querygraph(query):
    retry = 0
    maxretry = 20
    while True:
        if retry == maxretry:
            logger.error('Max retry. Throw error')
            raise Exception('Unknown error occured')
        try:
            logger.info('Query the graph')
            r = requests.post(graphurl, json={'query': query})
            data = json.loads(r.text)
            return data
        except Exception as e:
            logger.error(
                'Error occured getting events. Error: {}'.format(
                    e
                ))
            logger.info('Retry in 5 seconds. Retry {}/{}'.format(
                retry, maxretry))
            retry += 1
            time.sleep(5)
        if r.status_code != 200:
            logger.warning('Graph returned wrong access code: {}'.format(
                r.status_code))
            logger.info('Retry in 5 seconds. Retry {}/{}'.format(
                retry, maxretry))
            retry += 1
            time.sleep(5)
            continue
