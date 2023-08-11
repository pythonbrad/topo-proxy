from tunnels.facebook import FacebookProxy
from core import Tunnel
import logging
import logging.config
import os


logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

local_addr = ('0.0.0.0', 8001)

proxy = FacebookProxy(
    os.getenv('FB_USERNAME'), os.getenv('FB_PASSWORD'),
    os.getenv('FB_FRIEND'))

tunnel = Tunnel(proxy)
tunnel.bind(local_addr)

print(f'Listening on {local_addr}')

while 1:
    print('Waiting for communication...')
    tunnel.communicate()

tunnel.close()
