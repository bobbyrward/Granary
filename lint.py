import os

os.system('pychecker -Q -b wx rss_downloader.py')

# skip line too long messages
# I code on 3 1920x1080 monitors.
# dealwithit.jpg
# It's also my personal opinion that making code comply with this makes it MORE unreadable.
os.system('pep8 --ignore=E501 .')

#os.system('pylint rss_downloader.py')
