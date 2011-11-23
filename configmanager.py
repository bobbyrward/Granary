import os
import sys
import imp
import shutil


class ConfigManager(object):
    def __init__(self):
        self.config_folder = os.path.join(os.environ['LOCALAPPDATA'], 'rss_downloader')

        if not os.path.exists(self.config_folder):
            os.mkdir(self.config_folder)


        config_file_path = os.path.join(self.config_folder, 'config.py')

        if not os.path.exists(config_file_path):
            dist_config_file = os.path.join(os.path.dirname(__file__), 'config.py')
            shutil.copyfile(dist_config_file, config_file_path)

        self.config = imp.load_source('rss_downloader.config', config_file_path)
    
    def get_key(self, key_name):
        try:
            return getattr(self.config, key_name)
        except AttributeError:
            return None

    def get_config_path(self):
        return self.config_folder
    

CONFIG = ConfigManager()


