import os.path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from granary.configmanager import config

Base = declarative_base()
Session = sessionmaker()


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
        self.session = None

        filename = 'rss_downloader.db'

        self.db_file_path = os.path.join(
                config().get_config_path(), filename)
        self.db_file_path.replace('\\', '/')

        # backwards compatibility with old broken location
        if not os.path.exists(self.db_file_path):
            if os.path.exists(filename):
                os.rename(fielname, self.db_file_path)

    def connect(self):
        uri = 'sqlite:///%s' % self.db_file_path

        self.engine = create_engine(uri, echo=False)

        Base.metadata.create_all(self.engine)

        Session.configure(bind=self.engine)

        self.session = Session()
        self.session.commit()

    def query_torrents(self):
        return self.session.query(Torrent)

    def save_torrent(self, torrent):
        self.session.add(torrent)
        try:
            self.session.commit()
        except exc.SQLAlchemyError:
            self.session.rollback()
            return False

        return True

    def set_torrent_downloaded(self, torrent):
        torrent.downloaded = True
        self.save_torent(torrent)


if __name__ == '__main__':
    db = Database()
    db.connect()

    results = db.query_torrents().filter(
            Torrent.name.like('Sons.of.Anarchy.%')).all()

    new_torrent = Torrent(
            'Sons.of.Anarchy.S04E12.Burnt.and.Purged.Away.HDTV.XviD-FQM',
            '',
            datetime.now()
            )

    if db.save_torrent(new_torrent):
        print 'Saved successfully'
    else:
        print 'Error saving torrent'

    print results
