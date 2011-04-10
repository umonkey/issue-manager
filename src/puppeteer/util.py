# vim: set fileencoding=utf-8:

import json
import urllib2
import yaml

def fetch(url):
    u = urllib2.urlopen(urllib2.Request(url))
    if u is not None:
        return u.read()

def fetch_json(url):
    return json.loads(fetch(url))

def load_yaml(filename):
    return yaml.load(open(filename, 'rb'))

def load_json(filename):
    return json.loads(open(filename, 'rb').read())

def save_json(filename, data):
    open(filename, 'wb').write(json.dumps(data))
