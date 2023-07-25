from tunnels.simple import SimpleProxy
from core import Tunnel
import socket


local_addr = ('0.0.0.0', 8001)

proxy = SimpleProxy(socket.AF_INET, socket.SOCK_STREAM)
proxy.bind(local_addr)
proxy.listen(1)

tunnel = Tunnel(proxy)
tunnel.settimeout(1.0)

print(f'Listening on {local_addr}')

while 1:
    print('Waiting for communication...')
    tunnel.communicate(reverse=True)

tunnel.close()
