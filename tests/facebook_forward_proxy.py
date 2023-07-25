from tunnels.facebook import FacebookProxy
from core import Tunnel


local_addr = ('0.0.0.0', 8001)

proxy = FacebookProxy()

tunnel = Tunnel(proxy)
tunnel.bind(local_addr)

print(f'Listening on {local_addr}')

while 1:
    print('Waiting for communication...')
    tunnel.communicate()

tunnel.close()
