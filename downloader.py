import urllib2


class TorrentDownloader(object):
    def __init__(self):
        pass

    def download(self, url):
        response = urllib2.urlopen(url)

        return Torrent(response.read())


class Torrent(object):
    def __init__(self, encoded_torrent):
        self.encoded = encoded_torrent

    def write_to(self, filename):
        with open(filename, 'wb') as fd:
            fd.write(self.encoded)

    


