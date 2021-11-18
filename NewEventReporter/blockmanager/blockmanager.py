import logging
import json
import os

# Initialize logger
logger = logging.getLogger(__name__)

class BlockManager():
    def __init__(self, config, processedblock=0):
        logger.info('Initialize Block Manager')
        self.processedblock = int(processedblock)
        self.config = config
        if os.path.isfile(self.config):
            self.load_config()

    def set_processedblock(self,processedblock):
        if int(processedblock) <= self.processedblock:
            logger.warning('Block will not be set because block is '
            'lower or equal than the previous block')
            return
        logger.info('Set processed block on: {}'.format(processedblock))
        self.processedblock = int(processedblock)
        blockconfig = {
            'processedblock': processedblock
        }
        with open(self.config, 'w') as config:
            json.dump(blockconfig, config)

    def load_config(self):
        logger.info('Loading config')
        with open(self.config, 'r') as config:
            loadconfig = json.load(config)
        self.set_processedblock(loadconfig['processedblock'])


    def get_processedblock(self):
        return self.processedblock


if __name__ == '__main__':
    blockprocessedconfig = './config/blockprocessed.json'
    bm = BlockManager(blockprocessedconfig,300000)
    bm.set_processedblock(242443)
    print(bm.get_processedblock())
