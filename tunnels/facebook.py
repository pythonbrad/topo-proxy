import requests
from bs4 import BeautifulSoup
import time
import base64
import re
import os


class FacebookAPI:
    """
    import os

    LIMIT = "[EOF]"

    # Connection
    fb = FacebookAPI()
    fb.login(os.getenv('FB_USERNAME'), os.getenv('FB_PASSWORD'))
    # Sending messages
    fb.send(LIMIT)
    fb.send('Table of multiplcation of 3!')
    [
        fb.send(f'3 x {i} = {3 * i}')
        for i in range(1, 13)
    ]

    print("Reading messages")
    page = None

    while 1:
        data = fb.read(page)

        print(data['messages'])

        if not data['prev_page'] or LIMIT in data['messages']:
            break
        else:
            page = data['prev_page']
    """

    def __init__(self):
        self._host = "https://free.facebook.com"
        self._session = requests.session()
        self._friend_id = None
        self._last_request_time = time.time()
        self.delay = 2  # 2s

    def is_login(self):
        return bool(self._session.cookies.get('c_user', None))

    def _get_bs(self, html: str):
        return BeautifulSoup(html, features="xml")

    def _request(self, url: str, data: dict = None):

        while time.time() - self._last_request_time < self.delay:
            time.sleep(0.1)

        if data:
            resp = self._session.post(url, data=data)
        else:
            resp = self._session.get(url)

        self._last_request_time = time.time()

        return resp

    def login(self, email: str, password: str):
        print('[FB-API] Athentification...')
        resp = self._request(self._host)
        form = self._get_bs(resp.text).find(id="login_form").find_all('input')
        form = {
            i.attrs['name']: i.attrs['value']
            for i in form
            if 'value' in i.attrs
        }
        form['email'] = email
        form['pass'] = password

        self._request(
            f'{self._host}/login/device-based/regular/login',
            data=form
        )
        self._user_id = self._session.cookies.get('c_user', None)

        if not self._user_id:
            raise Exception("Authentification failed.")

        self._friend_id = None

    def set_friend(self, friend_id: str):

        if friend_id == self._session.cookies.get('c_user'):
            raise Exception("Friend can't be yourself")

        self._friend_id = friend_id

    def _check(self):

        if not self.is_login():
            raise Exception('Login required')

        if not self._friend_id:
            raise Exception('Friend required')

    def read(self, page: str = None):
        print('[FB-API] Reading messages...')
        self._check()

        if not page:
            page = f'/messages/read/?fbid={self._friend_id}'

        resp = self._request(f'{self._host}{page}')
        root = self._get_bs(resp.text)

        msg = []

        for span in root.find(id="messageGroup").find_all('span'):
            msg.append(span.text)

        page = root.find(id="see_older")

        if page:
            page = page.a.attrs['href']

        return {'messages': msg, 'prev_page': page}

    def send(self, msg):
        print('[FB-API] Sending message...')
        self._check()

        resp = self._request(
            f'{self._host}/messages/read/?fbid={self._friend_id}')
        form = self._get_bs(resp.text).find(id="composer_form")
        form_url = form.attrs['action']
        form = {
            i.attrs['name']: i.attrs['value']
            for i in form.find_all('input')
            if 'value' in i.attrs and not i.attrs.get('type', None) == 'submit'
        }
        form['body'] = msg

        resp = self._request(f'{self._host}{form_url}', data=form)


class FacebookProxy:

    def __init__(self):
        self._chunk_size = 15000  # 15ko
        self._delay = 2  # 2s
        self._forwarder = None
        self._output_mode = True
        self._noise_filter = lambda data: [
            i[1:-1]
            for i in data
            if re.match(r'^\[.*?\]$', i)
        ]

        print('[FB-PROXY] Initialization...')

        # Connection
        self._fb_api = FacebookAPI()
        self._fb_api.login(os.getenv('FB_USERNAME'), os.getenv('FB_PASSWORD'))
        self._fb_api.set_friend(
            os.getenv('FB_FRIEND', self._fb_api._friend_id))

    def _check(self):
        if self._forwarder is None:
            raise Exception('Proxy mode unknow')

    def _wait(self, token: str):
        print(f'[FB-PROXY] Waiting for token: {token}...')

        while 1:
            data = self._fb_api.read()['messages']
            data = self._noise_filter(data)

            if data and re.match(token, data[-1]):
                break

            time.sleep(self._delay)

    def connect(self, addr=None):
        print('[FB-PROXY] Initialize connection with the server...')
        self._forwarder = True

        self._fb_api.send('[CONNECT]')
        self._wait(r'ACCEPT')
        self._wait(r'EOF-2')

    def accept(self):
        print('[FB-PROXY] Initialize connection with the client...')
        self._forwarder = False

        self._wait(r'CONNECT')
        self._fb_api.send('[ACCEPT]')

        return self, None

    def settimeout(self, timeout=None):
        pass

    def get_sock(self):
        return self

    def send(self, data: bytes) -> int:
        self._check()
        size = len(data)

        if self._forwarder is None:
            raise Exception('Proxy mode unknow')

        self._output_mode = True
        data = base64.b64encode(data).decode()

        while data:
            chunk = data[:self._chunk_size]
            print(f'[FB-PROXY] Sending of {len(chunk)}o...')
            self._fb_api.send('[%s]' % chunk)
            data = data[self._chunk_size:]
            print(f'[FB-PROXY] {len(data)}o remaining...')

        return size

    def recv(self, length=None) -> bytes:
        self._check()

        if self._forwarder and self._output_mode:
            self._fb_api.send('[EOF-1]')
            self._wait(r'EOF-2|CLOSE')
            self._output_mode = False
        elif not self._forwarder and self._output_mode:
            self._fb_api.send('[EOF-2]')
            self._wait(r'EOF-1|CLOSE')
            self._output_mode = False
        else:
            return b''

        page = None
        buffer = ''

        while 1:
            data = self._fb_api.read(page)

            buf = ''.join(self._noise_filter(data['messages']))
            buffer = buf + buffer

            if not data['prev_page'] or re.search(r'EOF-[12]', buf):
                break

            page = data['prev_page']

        buffer = re.split(r'EOF-[12]|CLOSE', buffer)[-2]

        return b''.join([
            # "==" is for both case 
            base64.b64decode(buf+'==')
            for buf in buffer.split('=')]
        )

    def close(self):
        self._fb_api.send('[CLOSE]')
