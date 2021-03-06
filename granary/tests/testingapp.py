import wx

#from twisted.internet import wxreactor
#wxreactor.install()

from twisted.internet import reactor


class MockConfig(object):
    def __init__(self):
        self.config = {}

    def save(self):
        pass

    def load_defaults(self):
        pass

    def set_key(self, key_name, key_value):
        self.config[key_name] = key_value

    def get_key(self, key_name):
        try:
            return self.config[key_name]
        except KeyError:
            return ''

    def get_config_path(self):
        return '.'

    def get_app_path(self):
        return '.'


class TestingApp(wx.App):
    def OnInit(self):
        self.SetAppName("test_app")
        self.Config = MockConfig()
        return True


TESTING_APP = None


def app_run():
    #wnd = wx.Frame(None, -1, "Testing")
    reactor.run()


def app_setup():
    global TESTING_APP

    if not TESTING_APP:
        TESTING_APP = TestingApp(False)
        #reactor.registerWxApp(TESTING_APP)
