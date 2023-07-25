from tunnels.simple import SimpleProxy
from core import Tunnel
import socket


local_addr = ('0.0.0.0', 8001)

proxy = SimpleProxy(socket.AF_INET, socket.SOCK_STREAM)

tunnel = Tunnel(proxy)
tunnel.bind(local_addr)

tunnel.settimeout(1.0)

print(f'Listening on {local_addr}')

while 1:
    print('Waiting for communication...')
    tunnel.communicate()

tunnel.close()
