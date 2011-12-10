import Queue
import logging

import wx
from wx.lib.newevent import NewEvent
from twisted.internet import reactor, threads

from granary import downloader
from granary import db


(TorrentDownloadedEvent, EVT_TORRENT_DOWNLOADED) = NewEvent()


log = logging.getLogger('granary.download_queue')


class DownloadQueue(object):
    def __init__(self):
        self.torrent_queue = Queue.Queue()
        self.db = None

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
            self.torrent_queue.put(torrent.name)

    def _process_queue(self):
        log.debug('_process_queue')
        self.db = db.DBSession()

        while True:
            item = self.torrent_queue.get()

            log.debug('got item %s', item)

            if isinstance(item, bool) and not item:
                self.torrent_queue.task_done()
                break

            torrent = self.db.get_torrent(item)

            self.download_torrent(torrent)
            self.torrent_queue.task_done()

        log.debug('_process_queue done')

    def download_torrents(self, matched_entries):
        """Download all the new entries
        """
        for torrent in matched_entries:
            self.download_torrent(torrent)

    def download_torrent(self, torrent):
        """Add the torrent to the client and update the app
        """
        # double check it wasn't already downloaded
        if torrent.downloaded:
            # already downloaded
            return

        log.debug('Adding torrent to client')

        # add it to the torrent client to download
        add_success = downloader.add_torrent_to_client(torrent)

        # check if it worked
        if not add_success:
            log.warning('Unable to commit torrent: %s', torrent.name)
            raise Exception('Unable to commit torrent: %s' % torrent.name)

        log.debug('Torrent added to client. Updating db')

        # udpate the database to indicate it was downloaded
        torrent.downloaded = True
        self.db.set_torrent_downloaded(torrent)

        # notify the app that a torrent was downloaded
        evt = TorrentDownloadedEvent()
        evt.torrent = torrent
        wx.PostEvent(wx.GetApp(), evt)
