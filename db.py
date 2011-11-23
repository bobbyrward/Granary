import os.path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import exc

from configmanager import CONFIG


Base = declarative_base()
Session = sessionmaker()


class Torrent(Base):
    __tablename__ = 'torrents'

    name = Column(String, primary_key=True)
    downloaded = Column(DateTime)

    def __init__(self, name, downloaded=None):
        if not downloaded:
            downloaded = datetime.now()

        self.name = name
        self.downloaded = downloaded


class Database(object):
    def __init__(self):
        self.engine = None
        self.session = None
        self.db_file_path = os.path.join(CONFIG.get_config_path(), 'rss_downloader.db').replace('\\', '/')

    def connect(self):
        #uri = 'sqlite:////%s' % self.db_file_path
        uri = 'sqlite:///rss_downloader.db'

        self.engine = create_engine(uri, echo=True)

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
        except exc.FlushError:
            return False

        return True



if __name__ == '__main__':
    db = Database()
    db.connect()

    results = db.query_torrents().filter(Torrent.name.like('Sons.of.Anarchy.%')).all()

    new_torrent = Torrent('Sons.of.Anarchy.S04E12.Burnt.and.Purged.Away.HDTV.XviD-FQM', datetime.now())

    if db.save_torrent(new_torrent):
        print 'Saved successfully'
    else:
        print 'Error saving torrent'

    print results







