import httplib2
import urllib
import json


class DelugeWebUIException(Exception):
    pass


class DelugeClientResponseError(DelugeWebUIException):
    def __init__(self, request, response):
        self.args = ['(%d: %s)' % (response.status, response.reason)]
        self.response = response
        self.request = request


class DelugeWebUIApiError(DelugeWebUIException):
    def __init__(self, request, json_response):
        self.id = json_response['id']
        self.result = json_response['result']
        self.code = json_response['error']['code']
        self.message = json_response['error']['message']
        self.args = ['(%d: %s)' % (self.code, self.message)]
        self.request = request


class DelugeWebUIClient(object):
    def __init__(self, endpoint):
        self.endpoint = urllib.basejoin(endpoint, '/json')
        self.http = httplib2.Http()
        self.headers = {}

    def _send_request(self, method, params=None, id=None):
        if params is None:
            params = []

        if id is None:
            id = 0

        raw_args = {
            'method': method,
            'params': params,
            'id': id,
        }

        request = json.dumps(raw_args)

        response, content = self.http.request(
                self.endpoint, 'POST', request, self.headers)

        if response.status != 200:
            raise DelugeClientResponseError(response)

        decoded = json.loads(content)

        if decoded['error'] is not None:
            raise DelugeWebUIApiError(decoded)

        if 'set-cookie' in response:
            self.headers['Cookie'] = response['set-cookie']

        return decoded['result']

    def login(self, password):
        return self._send_request('auth.login', [password])

    def check_session(self):
        return self._send_request('auth.check_session')

    def get_method_list(self):
        return self._send_request('system.listMethods')

    def update_ui(self):
        return self._send_request('web.update_ui')

    def download_torrent_from_url(self, url):
        return self._send_request('web.download_torrent_from_url', [url])

    def add_torrents(self, *file_paths):
        return self._send_request('web.add_torrents', [file_paths])

    def get_config_values(self, *values):
        return self._send_request('core.get_config_values', [values])


if __name__ == '__main__':
    import pprint
    ENDPOINT = "http://localhost:8112/json"
    PASSWORD = 'deluge'

    client = DelugeWebUIClient(ENDPOINT)
    methods = client.get_method_list()
    pprint.pprint(sorted(methods))

    pprint.pprint(client.login(PASSWORD))
    pprint.pprint(client.check_session())

    result = client.download_torrent_from_url('url here')
    pprint.pprint(result)

    file_path = result

    print 'getting config values'
    options = client.get_config_values(
                'add_paused',
                'compact_allocation',
                'download_location',
                'max_connections_per_torrent',
                'max_download_speed_per_torrent',
                'max_upload_speed_per_torrent',
                'max_upload_slots_per_torrent',
                'prioritize_first_last_pieces')

    pprint.pprint(options)

    torrent = {
        'path': file_path,
        'options': options,
    }

    result = client.add_torrents(torrent)
    pprint.pprint(result)
