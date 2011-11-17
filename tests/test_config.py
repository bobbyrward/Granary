import config


def test_required_settings():
    assert hasattr(config, "MATCH_TORRENTS")
    assert hasattr(config, "FEED_URL")





