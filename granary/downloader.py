import logging
import urllib2
import os

from granary.integration.delugewebapi import DelugeWebUIClient
from granary.configmanager import config


log = logging.getLogger('granary.downloader')


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
    log.info('Adding %s to client through deluge WebUI', filename)
    try:
        client = DelugeWebUIClient(config().get_key('DELUGE_WEB_UI_URL'))

        log.debug('Logging in')
        response = client.login(config().get_key('DELUGE_WEB_UI_PASSWORD'))
        if not response:
            return False

        log.debug('Checking session')
        response = client.check_session()
        if not response:
            return False

        log.debug('Downloading torrent locally')
        file_path = client.download_torrent_from_url(url)
        if not response:
            return False

        log.debug('Getting config values')
        options = client.get_config_values(*DELUGE_CONFIG_KEYS)

        #TODO: Just for debugging
        options['add_paused'] = True

        torrent = {
            'path': file_path,
            'options': options,
        }

        log.info('Finally, adding torrent')
        result = client.add_torrents(torrent)

        if not result:
            return False
    except Exception, e:
        log.exception('Error while adding torrent to client')
        return False
    else:
        log.debug('Torrent added successfully')
        return True


def watch_folder_downloader(filename, url):
    log.info('Adding %s to client through watch folder', filename)
    try:
        response = urllib2.urlopen(url)
        content = response.read()

        log.debug('Downloaded %d byte torrent file', len(content))

        watch_folder = config().get_key('DOWNLOAD_DIRECTORY')

        log.debug('Watch folder set to "%s"', watch_folder)

        filename = os.path.join(watch_folder, filename)

        with open(filename, 'wb') as fd:
            fd.write(content)

    except Exception, e:
        log.exception('Error while downloading torrent to watch folder')
        return False
    else:
        log.debug('Torrent downloaded successfully')
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
    integration_method = config().get_key('TORRENT_INTEGRATION_METHOD')
    log.debug('Torrent integration method: %s', integration_method)

    downloader = TORRENT_INTEGRATION_TRANSLATION[integration_method]

    log.debug('Downloading %s', torrent.download_link)
    return downloader(torrent.name + '.torrent', torrent.download_link)
