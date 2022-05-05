import logging
from logging import getLogger

import ambient
import requests
from dateutil import parser
from pytz import timezone

from config import NATURE_TOKEN, CHANNEL_ID, WRITE_KEY


logging.basicConfig(filename='./log/temperature.log',
                    level=logging.INFO,
                    format='%(asctime)s: %(message)s')
logger = getLogger(__name__)


def cmd():
    if not NATURE_TOKEN:
        logger.warning('nature remo api token is empty')
        return 1
    if not CHANNEL_ID:
        logger.warning('ambient channel id is empty')
        return 1
    if not WRITE_KEY:
        logger.warning('ambient write key is empty')
        return 1

    try:
        # Nature Remo API
        result = requests.get('https://api.nature.global/1/devices', headers={'Authorization': f'Bearer {NATURE_TOKEN}'})
        if result.status_code != 200:
            logger.info(result.status_code)
            logger.error(f'nature remo api failed: {result.json()}')
            return 1

        header = result.headers
        json = result.json()
        # 温度
        temperature = json[0]['newest_events']['te']['val']
        # 時間(GMT->JST)
        now = parser.parse(header['Date']).astimezone(timezone('Asia/Tokyo')).replace(tzinfo=None)
        now_str = now.strftime('%Y-%m-%d %H:%M:%S:000')
        logger.info(f'temp: {temperature}, datetime: {now_str}')

        # Ambient
        am = ambient.Ambient(CHANNEL_ID, WRITE_KEY)
        result = am.send({'d1': temperature, 'created': now_str})
        if result.status_code != 200:
            logger.error(f'post data failed: {result.json()}')
            return 1
        logger.info('post data succeed')
    except Exception:
        logger.error('request failed', exc_info=True)


if __name__ == '__main__':
    cmd()
