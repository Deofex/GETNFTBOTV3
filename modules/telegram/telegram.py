import time
import logging
import json
import requests
from urllib.parse import quote

# Configure logging
logger = logging.getLogger(__name__)


def get_url(url, headers=None):
    '''Retrieve content from an URL'''
    response = requests.get(url, headers=headers)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url, headers=None):
    '''Retrieve a JSON file from an URL'''
    content = get_url(url, headers)
    js = json.loads(content)
    return js


class TelegramBot():
    def __init__(self, telegramapitoken, telegramchannel):
        self.apikey = telegramapitoken
        self.telegramchannel = telegramchannel
        logger.info('Initialize Telegram bot, channel: {}'.format(
            telegramchannel))

    def createtelegramurl(self, method, parameters={}):
        # Define api url
        turl = "https://api.telegram.org/bot{}/{}".format(
            self.apikey, method)

        # Add parameters to the api url
        if len(parameters.keys()) != 0:
            turl = turl + "?"
            for parameter in parameters.keys():
                turl = turl + parameter + "="
                turl = turl + quote(str(parameters[parameter])) + "&"

        # Remove last &
        turl = turl[:-1]

        logger.debug("Telegram API url: {}".format(turl))
        return turl

    def sendmessage(self, msg, formatstyle="HTML", disablewebpreview="True"):
        method = 'sendMessage'
        parameters = {
            "chat_id": self.telegramchannel,
            "text": msg,
            "parse_mode": formatstyle,
            "disable_web_page_preview": disablewebpreview
        }
        url = self.createtelegramurl(method, parameters=parameters)
        self.processfunction(url)

    def sendphoto(self, photo, caption, parsemode="HTML", backuptotext=True):
        method = 'sendPhoto'
        parameters = {
            "chat_id": self.telegramchannel,
            "caption": caption,
            "photo": photo,
            "parse_mode": parsemode
        }
        url = self.createtelegramurl(method, parameters=parameters)
        try:
            self.processfunction(url)
        except Exception as e:
            if e.args[0] == 'BadFormat' and backuptotext == True:
                self.sendmessage(caption)
            else:
                raise Exception("Unknown error: {}".format(e.args[0]))

    def processfunction(self,url):
        errors = 0
        maxerrors = 10
        while True:
            if errors == maxerrors:
                logger.error('To much errors occured, stop retrying')
                raise Exception('ToMuchRetries')
            logger.info('Interact with TG')
            logger.debug("Process tg function via url: {}".format(url))
            try:
                results = get_json_from_url(url)
            except Exception as e:
                logger.error('Error: {}: {}'.format(
                    e.args[0]['code'], e.args[0]['message']))
                logger.error('Error {}/{} occured, retry in 5 seconds.'.format(
                    errors, maxerrors
                ))
                errors += 1
                time.sleep(5)
                continue

            if results['ok'] == True and 'error_code' not in results:
                return results
            if 'error_code' in results:
                if results['error_code'] == 400:
                    raise Exception('BadFormat')
                elif results['error_code'] == 429:
                    logger.warning(
                        'TG used to much, retry after: {} seconds'.format(
                        results['parameters']['retry_after']
                    ))
                    time.sleep(results['parameters']['retry_after'])
            errors += 1
            logger.error(
                'Error {}/{}, retry'.format(
                    errors, maxerrors
                ))
            time.sleep(5)
