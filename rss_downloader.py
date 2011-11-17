import config
import feed


class RssDownloader(object):
    def __init__(self):
        self.feed = feed.Feed(config.FEED_URL)

    def run(self, args):
        pass


if __name__ == '__main__':
    import sys
    
    downloader = RssDownloader()
    downloader.run(sys.argv)


