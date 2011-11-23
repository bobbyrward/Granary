from configmanager import CONFIG
import os


def test_required_settings():
    assert CONFIG.get_key("MATCH_TORRENTS") != None
    assert CONFIG.get_key("FEED_URL") != None
    assert CONFIG.get_key("DOWNLOAD_DIRECTORY") != None


def test_config_directory_exists():
    assert os.path.exists(CONFIG.get_config_path())




