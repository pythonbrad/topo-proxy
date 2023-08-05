from tunnels.facebook import FacebookProxy
from core import Tunnel


proxy = FacebookProxy()

tunnel = Tunnel(proxy)
# We maximize the sending of data
# since the encoding increase the size of the data.
tunnel._chunk_size = int(proxy._chunk_size * (1 - 0.25))

print('Listening on facebook...')

while 1:
    print('Waiting for communication...')
    tunnel.communicate(reverse=True)

tunnel.close()
