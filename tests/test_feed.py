import feed


RSS_TEST_CONTENT = """<?xml version="1.0" encoding="utf-8" ?>
<rss version="1.0">
<channel>
<title>Test Feed</title>
<link>http://test.me</link>
<description>RSS Feed</description>
<item>
<title>Some.Show.S01E02.Name.of.the.Episode.HDTV.XviD-ASDF</title>
<link>http://test.me/download/torrent/1/</link>
<description>Some Show: Name of the Episode</description>
</item>
<item>
<title>Some.Other.Show.S01E03.Other.Name.of.the.Episode.720p.HDTV.x264-QWERTY</title>
<link>http://test.me/download/torrent/2/</link>
<description>Some Other Show: Other Name of the Episode</description>
</item>
<item>
<title>Last.Show.S01E04.Last.Name.HDTV.XviD-ZXCV</title>
<link>http://test.me/download/torrent/3/</link>
<description>Last Show: Last Name</description>
</item>
</channel>
</rss>
"""


def fake_urllib2_urlopen(url):
    class FakeReader(object):
        def read(self):
            return RSS_TEST_CONTENT

    return FakeReader()


def test_feed_parsing():
    feed.urllib2.urlopen = fake_urllib2_urlopen

    rss_feed = feed.Feed('fake url')

    rss_entries = rss_feed.get_entries()

    assert len(rss_entries) == 3

    assert rss_entries[0]['title'] == 'Some.Show.S01E02.Name.of.the.Episode.HDTV.XviD-ASDF'
    assert rss_entries[0]['link'] == 'http://test.me/download/torrent/1/'
    assert rss_entries[0]['description'] == 'Some Show: Name of the Episode'

    assert rss_entries[1]['title'] == 'Some.Other.Show.S01E03.Other.Name.of.the.Episode.720p.HDTV.x264-QWERTY'
    assert rss_entries[1]['link'] == 'http://test.me/download/torrent/2/'
    assert rss_entries[1]['description'] == 'Some Other Show: Other Name of the Episode'

    assert rss_entries[2]['title'] == 'Last.Show.S01E04.Last.Name.HDTV.XviD-ZXCV'
    assert rss_entries[2]['link'] == 'http://test.me/download/torrent/3/'
    assert rss_entries[2]['description'] == 'Last Show: Last Name'
