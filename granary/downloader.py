import urllib2
import os

from granary.integration.delugewebapi import DelugeWebUIClient
from granary.configmanager import config


DELUGE_CONFIG_KEYS = [
    'add_paused',
    'compact_allocation',
    'download_location',
    'max_connections_per_torrent',
    'max_download_speed_per_torrent',
    'max_upload_speed_per_torrent',
    'max_upload_slots_per_torrent',
    'prioritize_first_last_pieces',
]


def deluge_web_ui_downloader(filename, url):
    try:
        client = DelugeWebUIClient(config().get_key('DELUGE_WEB_UI_URL'))

        response = client.login(config().get_key('DELUGE_WEB_UI_PASSWORD'))

        if not response:
            print 'ERROR: Deluge web ui did not accept configured password'
            return False

        response = client.check_session()
        if not response:
            print 'ERROR: Deluge web ui did not accept configured password'
            return False

        file_path = client.download_torrent_from_url(url)
        if not response:
            print 'ERROR: Deluge web ui did not download torrent successfully'
            return False

        options = client.get_config_values(*DELUGE_CONFIG_KEYS)

        torrent = {
            'path': file_path,
            'options': options,
        }

        result = client.add_torrents(torrent)

        if not result:
            print 'ERROR: Deluge web ui did not add torrent successfully'
            return False
    except Exception, e:
        print '%r: %s' % (e, e)
        import traceback
        traceback.print_exc()
        return False
    else:
        return True


def watch_folder_downloader(filename, url):
    try:
        response = urllib2.urlopen(url)
        content = response.read()

        filename = os.path.join(
                config().get_key('DOWNLOAD_DIRECTORY'),
                filename)

        with open(filename, 'wb') as fd:
            fd.write(self.encoded)
    except Exception, e:
        print '%r: %s' % (e, e)
        import traceback
        traceback.print_exc()
        return False
    else:
        return True


TORRENT_INTEGRATION_METHODS = {
    'WATCH_FOLDER': 'Watch Directory',
    'DELUGE_WEB_UI': 'Deluge Web UI',
}


TORRENT_INTEGRATION_TRANSLATION = {
    'WATCH_FOLDER': watch_folder_downloader,
    'DELUGE_WEB_UI': deluge_web_ui_downloader,
}


def add_torrent_to_client(torrent):
    downloader = TORRENT_INTEGRATION_TRANSLATION[
            config().get_key('TORRENT_INTEGRATION_METHOD')]

    return downloader(torrent.name, torrent.download_link)
