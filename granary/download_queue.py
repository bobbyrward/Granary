import Queue
import logging

import wx
from wx.lib.newevent import NewEvent
from twisted.internet import reactor, threads

from granary import downloader
from granary import db


(TorrentDownloadedEvent, EVT_TORRENT_DOWNLOADED) = NewEvent()


log = logging.getLogger(__name__)


class DownloadQueue(object):
    def __init__(self):
        self.torrent_queue = Queue.Queue()

    def stop(self):
        log.debug('stopping')
        self.torrent_queue.put(False)
        self.torrent_queue.join()

    def run(self):
        log.debug('running')
        reactor.callInThread(self._process_queue)

    def queue_torrent(self, *torrents):
        for torrent in torrents:
            log.debug('queuing torrent %s', torrent.name)

            # double check it wasn't already downloaded
            if torrent.downloaded:
                # already downloaded
                continue

            self.torrent_queue.put((torrent.name, torrent.download_link))

    def _process_queue(self):
        log.debug('_process_queue')

        while True:
            item = self.torrent_queue.get()

            log.debug('got item %s', item)

            if isinstance(item, bool) and not item:
                self.torrent_queue.task_done()
                break

            self.download_torrent(item[0], item[1])
            self.torrent_queue.task_done()

        log.debug('_process_queue done')

    def _set_torrent_downloaded(self, name):
        session = db.DBSession()
        torrent = session.get_torrent(name)
        session.set_torrent_downloaded(torrent)

        # notify the app that a torrent was downloaded
        evt = TorrentDownloadedEvent()
        evt.torrent = torrent
        wx.PostEvent(wx.GetApp(), evt)

    def download_torrent(self, name, url):
        """Add the torrent to the client and update the app
        """
        log.debug('Adding torrent to client')

        # add it to the torrent client to download
        add_success = downloader.add_torrent_to_client(name, url)

        # check if it worked
        if not add_success:
            log.warning('Unable to commit torrent: %s', name)
            raise Exception('Unable to commit torrent: %s' % name)

        log.debug('Torrent added to client. Updating db')

        reactor.callFromThread(self._set_torrent_downloaded, name)
