from granary import db
from datetime import datetime
from datetime import timedelta
from granary.tests import testingapp


database = None


TORRENT_NAME = "TORRENT_NAME"
TORRENT_LINK = "TORRENT_LINK"
TORRENT_TIME = datetime.now()

TORRENT2_NAME = "TORRENT_NAME_2"
TORRENT2_LINK = "TORRENT_LINK_2"
TORRENT2_TIME = datetime.now()

TORRENT3_NAME = "TORRENT_NAME_3"
TORRENT3_LINK = "TORRENT_LINK_3"
TORRENT3_TIME = datetime.now()


def setup():
    global database
    testingapp.app_setup()
    database = db.Database()
    database.connect(use_in_memory=True)
    database.init()


def teardown():
    pass


def test_torrent_constructor():
    name = 'name'
    link = 'link'
    yesterday = datetime.now() + timedelta(days=-1)
    downloaded = True
    torrent = db.Torrent(name, link, yesterday, downloaded)

    assert torrent.name == name
    assert torrent.download_link == link
    assert torrent.first_seen == yesterday
    assert torrent.downloaded == downloaded

    torrent = db.Torrent(name, link, yesterday)

    assert torrent.name == name
    assert torrent.download_link == link
    assert torrent.first_seen == yesterday
    assert torrent.downloaded == False

    torrent = db.Torrent(name, link)

    assert torrent.name == name
    assert torrent.download_link == link
    assert torrent.first_seen != yesterday, '%s == %s' % (torrent.first_seen, yesterday)
    assert torrent.downloaded == False


def test_create_and_save_torrent():
    session = db.DBSession()

    torrent = db.Torrent(TORRENT_NAME, TORRENT_LINK, TORRENT_TIME)
    session.save_torrent(torrent)
    torrent = session.query_torrents().filter_by(name=TORRENT_NAME).one()
    assert torrent.name == TORRENT_NAME
    assert torrent.download_link == TORRENT_LINK
    assert torrent.first_seen == TORRENT_TIME
    assert torrent.downloaded == False

    torrent2 = db.Torrent(TORRENT2_NAME, TORRENT2_LINK, TORRENT2_TIME)
    session.save_torrent(torrent2)
    torrent2 = session.query_torrents().filter_by(name=TORRENT2_NAME).one()
    assert torrent2.name == TORRENT2_NAME
    assert torrent2.download_link == TORRENT2_LINK
    assert torrent2.first_seen == TORRENT2_TIME
    assert torrent2.downloaded == False

    torrent3 = db.Torrent(TORRENT3_NAME, TORRENT3_LINK, TORRENT3_TIME, downloaded=True)
    session.save_torrent(torrent3)
    torrent3 = session.query_torrents().filter_by(name=TORRENT3_NAME).one()
    assert torrent3.name == TORRENT3_NAME
    assert torrent3.download_link == TORRENT3_LINK
    assert torrent3.first_seen == TORRENT3_TIME
    assert torrent3.downloaded == True


def test_set_torrent_downloaded():
    session = db.DBSession()

    pre_downloaded_count = session.query_torrents().filter_by(downloaded=True).count()
    assert pre_downloaded_count == 1

    torrent2 = session.query_torrents().filter_by(name=TORRENT2_NAME).one()
    assert torrent2.downloaded == False

    session.set_torrent_downloaded(torrent2)
    assert torrent2.downloaded == True

    post_downloaded_count = session.query_torrents().filter_by(downloaded=True).count()
    assert post_downloaded_count == 2
