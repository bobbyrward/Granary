import urllib2
import os

from granary.configmanager import CONFIG
from granary.integration.delugewebapi import DelugeWebUIClient


def deluge_web_ui_downloader(filename, url):
    try:
        client = DelugeWebUIClient(CONFIG.get_key('DELUGE_WEB_UI_URL'))

        response = client.login(CONFIG.get_key('DELUGE_WEB_UI_PASSWORD'))

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

        options = client.get_config_values(
                    'add_paused', 'compact_allocation', 'download_location',
                    'max_connections_per_torrent', 'max_download_speed_per_torrent',
                    'max_upload_speed_per_torrent', 'max_upload_slots_per_torrent',
                    'prioritize_first_last_pieces')
        
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

        filename = os.path.join(CONFIG.get_key('DOWNLOAD_DIRECTORY'), filename)

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


def add_torrent_to_client(filename, url):
    return TORRENT_INTEGRATION_TRANSLATION[CONFIG.get_key('TORRENT_INTEGRATION_METHOD')](filename, url)

