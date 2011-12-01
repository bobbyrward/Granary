
try:
    import gntp
    import gntp.notifier
except ImportError:
    gntp = None
    
from configmanager import CONFIG


if gntp is None:
    class Growler(object):
        def __init__(self):
            pass

        def send_download_notification(self):
            pass
else:
    class Growler(object):
        def __init__(self):
            self.growl = gntp.notifier.GrowlNotifier(
                applicationName = "Rss Downloader",
                notifications = ["New Download"],
                defaultNotifications = ["New Download"],
                hostname = "localhost",
            )

            self.growl.register()


        def send_download_notification(self, torrent):
            self.growl.notify(
                noteType = "New Download",
                title = "New torrent downloaded",
                description = "%s was downloaded" % torrent.name,
                sticky = False,
                priority = 1,
            )


if __name__ == '__main__':
    growler = Growler()
    import db

    database = db.Database()
    database.connect()

    torrent = database.query_torrents().order_by(db.Torrent.first_seen.desc()).limit(1).one()

    growler.send_download_notification(torrent)