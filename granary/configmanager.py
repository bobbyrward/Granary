import os
import sys
import imp
import shutil
import cPickle as pickle

import wx


class ConfigManager(object):
    def __init__(self):
        self.std_paths = wx.StandardPaths_Get()

        self.config_folder = self.std_paths.GetUserLocalDataDir()

        self.config = {}

        self.default_options = {}
        self.default_options['FEED_URLS'] = []
        self.default_options['MATCH_TORRENTS'] = []
        self.default_options['DOWNLOAD_DIRECTORY'] = '.'
        self.default_options['DELUGE_WEB_UI_PASSWORD'] = 'deluge'
        self.default_options['DELUGE_WEB_UI_URL'] = 'http://localhost:8112'
        self.default_options['TORRENT_INTEGRATION_METHOD'] = 'WATCH_FOLDER'
        self.default_options['ENABLE_GROWL'] = False
        self.default_options['ENABLE_GROWL_NEW_TORRENT_NOTIFICATION'] = False
        self.default_options['ENABLE_GROWL_DOWNLOAD_NOTIFICATION'] = True
        self.default_options['SEARCH_HISTORY'] = []

        if not os.path.exists(self.config_folder):
            os.mkdir(self.config_folder)

        self.config_file_path = os.path.join(
                self.config_folder, 'rss_downloader.config')

        self.load_defaults()

        try:
            with open(self.config_file_path, 'rb') as fd:
                self.config = pickle.load(fd)
        except IOError:
            pass

    def save(self):
        with open(self.config_file_path, 'wb') as fd:
            pickle.dump(self.config, fd)

    def load_defaults(self):
        self.config = self.default_options

        try:
            config_orig = imp.load_source('rss_downloader.config',
                    os.path.join(self.config_folder, 'config.py'))
        except:
            pass
        else:
            def copy_config(key):
                self.config[key] = getattr(config_orig, key)

            copy_config('FEED_URLS')
            copy_config('MATCH_TORRENTS')
            copy_config('DOWNLOAD_DIRECTORY')
            copy_config('DELUGE_WEB_UI_PASSWORD')
            copy_config('DELUGE_WEB_UI_URL')
            copy_config('TORRENT_INTEGRATION_METHOD')

    def set_key(self, key_name, key_value):
        self.config[key_name] = key_value

    def get_key(self, key_name):
        try:
            return self.config[key_name]
        except KeyError:
            return self.default_options[key_name]

    def get_config_path(self):
        return self.config_folder

    def get_app_path(self):
        return os.path.dirname(__file__)


def config():
    return wx.GetApp().Config
