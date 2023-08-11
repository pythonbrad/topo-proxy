import argparse
from .tunnels import simple, facebook
from .core import Tunnel
import logging
import logging.config
import os
import sys
import time
import socket


BASEDIR = os.path.dirname(sys.argv[0])
logging.config.fileConfig(
    fname=os.path.join(BASEDIR, 'log.conf'),
    disable_existing_loggers=False,
    defaults={
        "logfilename": os.path.join(
            BASEDIR,
            os.getenv('LOGFILENAME', str(time.time())+'.log')
        )
    }
)

# Get the logger specified in the file
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser(
    prog='TopoProxy',
    description='Tunneling through a free access service.',
)
parser.add_argument(
    'tunnel', choices=['default', 'facebook'],
    help='tunneling module')
parser.add_argument(
    '-r', '--reverse', action='store_true',
    help='tunnel as a reverse proxy')
parser.add_argument(
    '-i', '--ip', nargs='?', default='0.0.0.0',
    help='local ip address')
parser.add_argument(
    '-p', '--port', type=int, nargs='?',
    default=8000, help='local port address')
parser.add_argument(
    '-t', '--timeout', type=float, nargs='?',
    default=0.5, help='[default] timeout')
parser.add_argument(
    '-td', '--txdelay', type=float, nargs='?',
    default=2.0, help='[facebook] delay between each request on facebook')
parser.add_argument(
    '-rd', '--rxdelay', type=float, nargs='?',
    default=5.0, help='[facebook] delay between each waiting of data')


args = parser.parse_args()


if args.tunnel == 'default':
    proxy = simple.SimpleProxy(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind((args.ip, args.port))

    tunnel = Tunnel(proxy)
    tunnel.settimeout(args.timeout)

    if args.reverse:
        proxy.listen(1)
    else:
        pass
elif args.tunnel == 'facebook':
    proxy = facebook.FacebookProxy(
        os.getenv('FB_USERNAME'), os.getenv('FB_PASSWORD'),
        os.getenv('FB_FRIEND'))
    proxy._delay = args.rxdelay
    proxy._fb_api.delay = args.txdelay
    tunnel = Tunnel(proxy)

    if args.reverse:
        # We maximize the sending of data
        # since the encoding increase the size of the data.
        tunnel._chunk_size = int(proxy._chunk_size * (1 - 0.25))
    else:
        pass
else:
    raise Exception(f'Tunnel `{args.tunnel}` not take in account.')
