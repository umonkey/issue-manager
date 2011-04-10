# vim: set fileencoding=utf-8:

import base64
import os
import sys
import yaml

CONFIG_NAME = '~/.config/puppeteer.yaml'

class YamlConfig:
    """YAML interface."""
    def __init__(self):
        self.filename = os.path.expanduser(CONFIG_NAME)
        if os.path.exists(self.filename):
            self.data = yaml.load(open(self.filename, 'rb').read())
        else:
            self.data = {}

    def save(self):
        dump = yaml.dump(self.data)
        exists = os.path.exists(self.filename)
        f = open(self.filename, 'wb')
        f.write(dump.encode('utf-8'))
        f.close()
        if not exists:
            os.chmod(self.filename, 0600)

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def set(self, key, value):
        self.data[key] = value

    def get_password(self, key):
        value = self.get(key)
        if value is not None:
            value = base64.b64decode(value)
        return value

    def set_password(self, key, value):
        self.set(key, base64.b64encode(value))

def Open():
    return YamlConfig()
