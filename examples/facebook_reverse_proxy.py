from tunnels.facebook import FacebookProxy
from core import Tunnel
import logging
import logging.config
import os


logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

proxy = FacebookProxy(os.getenv('FB_USERNAME'), os.getenv('FB_PASSWORD'))

tunnel = Tunnel(proxy)
# We maximize the sending of data
# since the encoding increase the size of the data.
tunnel._chunk_size = int(proxy._chunk_size * (1 - 0.25))

print('Listening on facebook...')

while 1:
    print('Waiting for communication...')
    tunnel.communicate(reverse=True)

tunnel.close()
