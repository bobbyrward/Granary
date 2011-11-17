import re
import os
from collections import defaultdict


import config
import feed
import downloader


class RssDownloader(object):
    def __init__(self):
        self.feed = feed.Feed(config.FEED_URL)
        self.downloader = downloader.TorrentDownloader()
        self.matches = defaultdict(list)

    def check_feed_entry(self, entry):
        """Check a feed entry for a match against MATCH_TORRENTS"""

        for match_regexp in config.MATCH_TORRENTS:
            match = re.match(match_regexp, entry['title'])

            if match:
                # If it matches a regular expression, add it to matches under that regular expression
                self.matches[match_regexp].append(entry)
                return True

        # no match
        return False

    def find_matches(self):
        """Find all entries that match a regular expression in MATCH_TORRENTS"""

        for entry in self.feed.get_entries():
            # check each entry
            self.check_feed_entry(entry)

    def download_torrent(self, entry):
        torrent = self.downloader.download(entry['link'])
        path = os.path.join(config.DOWNLOAD_DIRECTORY, entry['title'] + '.torrent')
        torrent.write_to(path)

    def download_matches(self):
        """Download all matches entries"""

        for regexp, matches in self.matches.iteritems():
            for entry in matches:
                # Download the torrent
                self.download_torrent(entry)

    def run(self, args):
        self.find_matches()
        self.download_matches()




if __name__ == '__main__':
    import sys
    
    downloader = RssDownloader()
    downloader.run(sys.argv)


