import os.path
import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import exc

from granary.configmanager import config

Base = declarative_base()
Session = scoped_session(sessionmaker())


log = logging.getLogger(__name__)


class Torrent(Base):
    __tablename__ = 'torrents'

    name = Column(String, primary_key=True)
    download_link = Column(String)
    first_seen = Column(DateTime)
    downloaded = Column(Boolean)

    def __init__(self, name, link, first_seen=None, downloaded=False):
        if not first_seen:
            first_seen = datetime.now()

        self.name = name
        self.download_link = link
        self.first_seen = first_seen
        self.downloaded = downloaded


class Database(object):
    def __init__(self):
        self.engine = None

        filename = 'rss_downloader.db'

        self.db_file_path = os.path.join(
                config().get_config_path(), filename)
        self.db_file_path.replace('\\', '/')

        # backwards compatibility with old broken location
        if not os.path.exists(self.db_file_path):
            if os.path.exists(filename):
                os.rename(fielname, self.db_file_path)

    def connect(self, use_in_memory=False):
        if use_in_memory:
            uri = 'sqlite:///:memory:'
        else:
            uri = 'sqlite:///%s' % self.db_file_path

        log.debug('connecting to %s', uri)

        self.engine = create_engine(uri, echo=False)
        Session.configure(bind=self.engine)

    def init(self):
        log.debug('initializing tables')

        session = Session()
        Base.metadata.create_all(self.engine)
        session.commit()
        session.close()


class DBSession(object):
    def __init__(self):
        self.session = Session()

    def query_torrents(self):
        return self.session.query(Torrent)

    def save_torrent(self, torrent):
        log.debug('saving torrent %s', torrent.name)

        self.session.add(torrent)

        return self.commit()

    def commit(self):
        try:
            self.session.commit()
        except exc.SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def set_torrent_downloaded(self, torrent):
        log.debug('setting torrent %s to downloaded', torrent.name)

        torrent.downloaded = True

        return self.save_torrent(torrent)

    def get_torrent(self, name):
        return self.session.query(Torrent).get(name)
