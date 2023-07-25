import socket
import re


class Tunnel:
    """
    proxy = SimpleProxy()

    server = Tunnel(proxy)
    server.bind(('0.0.0.0', 8000))

    print(f"Listening on 0.0.0.0:8000.")

    while 1:
        print("Waiting of communication...")
        server.communicate()

    server.close()
    """

    def __init__(self, proxy):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._timeout = 60.0  # 60s
        self._proxy = proxy
        self._chunk_size = 8192  # 8ko

    def settimeout(self, timeout: float):
        self._timeout = timeout

    def bind(self, local_addr: (str, int)):
        self._sock.bind(local_addr)
        self._sock.listen(1)

    def _get_sock(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def communicate(self, reverse=False):
        remote_addr = None

        if reverse:
            tx = self._get_sock()
            rx, client_info = self._proxy.accept()
        else:
            tx = self._proxy.get_sock()
            rx, client_info = self._sock.accept()

        tx.settimeout(self._timeout)
        rx.settimeout(self._timeout)

        print(f"[TUNNEL] New connection income: {client_info}.")

        # Forward
        while 1:
            try:
                data = rx.recv(self._chunk_size)
            except socket.timeout:
                break
            except ConnectionResetError:
                break

            if not data:
                break

            if not remote_addr:
                metadata = re.findall(
                    rb'Host: (.*?)\r\n',
                    data
                )

                # Port 80 are often not specified
                remote_addr = metadata[0] + b':80'
                remote_addr = remote_addr.decode().split(':')
                remote_addr = (
                    remote_addr[0],
                    int(remote_addr[1])
                )
                data = re.sub(rb'\w*://.*?/', b'/', data)

                print(f"[TUNNEL] Connection to {remote_addr}...")
                try:
                    tx.connect(remote_addr)
                except ConnectionError as err:
                    print(f'[TUNNEL] {err}')
                    return

            print(f"[TUNNEL] Forwarding of {len(data)}o...")
            tx.send(data)

        # Reverse
        while 1:

            # In case where no data sent
            if data is None:
                break

            try:
                data = tx.recv(self._chunk_size)
            except socket.timeout:
                break
            except ConnectionResetError:
                break
            # Maybe the host not respond
            except OSError as err:
                print(f'[TUNNEL] {err}')
                break

            if not data:
                break

            print(f"[TUNNEL] Reversing of {len(data)}o...")
            rx.send(data)

        print("[TUNNEL] Closing of the connection...")
        tx.close()
        rx.close()

    def close(self):
        print("[TUNNEL] Closing of the tunnel...")
        self._proxy.close()
        self._sock.close()
