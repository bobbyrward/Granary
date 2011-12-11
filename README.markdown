A (not so) simple RSS feed torrent downloader

TODO in order of priority:

* BUG: The re changed check isn't working
* BUG: New torrent growler notifications aren't working(?)
* BUG: Deluge WebUI integration can lock up the whole app
** Getting config values seems to be the problem point
** Move to a reactor thread and use a deferred to track status?
* BUG: Duplicate entries are added to feed history list If there are any new torrents on app load
* Make db a package and split into separate modules
* Make downloading and updating the database atomic. Nothing should ever be marked as downloaded that wasn't added to the client and vice versa.
* Improve stability.
* Testing is currently half-assed. Fix that.
* Build compiled executable and installer
* Add easier ability to test regular expressions
* Add growl connection options
* Add way to create a regular expression for the user
* Add labels to feeds to indentify them in history
* Add update checking
* Make sure app is working on linux
* Improve performance
* POSSIBLE: Add uTorrent integration

