import os
import sys
import imp
import shutil
import cPickle as pickle


class ConfigManager(object):
    def __init__(self):
        self.config_folder = os.path.join(os.environ['LOCALAPPDATA'], 'rss_downloader')
        self.config = {}

        self.default_options = {}
        self.default_options['FEED_URLS'] = []
        self.default_options['MATCH_TORRENTS'] = []
        self.default_options['DOWNLOAD_DIRECTORY'] = '.'
        self.default_options['DELUGE_WEB_UI_PASSWORD'] = 'deluge'
        self.default_options['DELUGE_WEB_UI_URL'] = 'http://localhost:8112'
        self.default_options['TORRENT_INTEGRATION_METHOD'] = 'WATCH_FOLDER'

        if not os.path.exists(self.config_folder):
            os.mkdir(self.config_folder)

        self.config_file_path = os.path.join(self.config_folder, 'rss_downloader.config')
        #                = os.path.join(self.config_folder, 'config.py')

        try:
            with open(self.config_file_path, 'rb') as fd:
                self.config = pickle.load(fd)
        except IOError:
            self.load_defaults()


    def save(self):
        with open(self.config_file_path, 'wb') as fd:
            pickle.dump(self.config, fd)

    def load_defaults(self):
        try:
            config_orig = imp.load_source('rss_downloader.config', os.path.join(self.config_folder, 'config.py'))
        except:
            self.config = self.default_options
        else:
            self.config['FEED_URLS'] = config_orig.FEED_URLS
            self.config['MATCH_TORRENTS'] = config_orig.MATCH_TORRENTS
            self.config['DOWNLOAD_DIRECTORY'] = config_orig.DOWNLOAD_DIRECTORY
            self.config['DELUGE_WEB_UI_PASSWORD'] = config_orig.DELUGE_WEB_UI_PASSWORD
            self.config['DELUGE_WEB_UI_URL'] = config_orig.DELUGE_WEB_UI_URL
            self.config['TORRENT_INTEGRATION_METHOD'] = config_orig.TORRENT_INTEGRATION_METHOD

    def set_key(self, key_name, key_value):
        self.config[key_name] = key_value

    def get_key(self, key_name):
        try:
            return self.config[key_name]
        except KeyError:
            return self.default_options[key_name]

    def get_config_path(self):
        return self.config_folder
    

CONFIG = ConfigManager()


