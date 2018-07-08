# -*- coding: utf-8 -*-
""" File config.py

"""

import yaml
import collections

CONFIG_FILE = './etc/config.yaml'


def load_config(section):
    config_dict = yaml.load(open(CONFIG_FILE, 'r'))
    config = collections.namedtuple('config', config_dict[section].keys())
    cfg = config(*config_dict[section].values())
    return cfg
