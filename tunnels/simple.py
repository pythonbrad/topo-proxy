import socket


class SimpleProxy(socket.socket):
    """
    # Forward
    proxy = SimpleProxy()
    sock = proxy.get_sock()
    sock.connect(('0.0.0.0', 8000))
    sock.send(b'hello')
    print(sock.recv(1024))
    sock.close()
    proxy.close()

    # Reverse
    proxy = SimpleProxy(socket.AF_INET, socket.SOCK_STREAM)
    proxy.bind(('0.0.0.0', 8000))
    sock, _ = proxy.accept()
    print(sock.recv(1024))
    sock.send(b'bye')
    sock.close()
    proxy.close()
    """

    def get_sock(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
