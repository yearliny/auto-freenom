# -*- coding: utf-8 -*-
import logging
import sys
from configparser import ConfigParser

from freenom import Freenom

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, stream=sys.stdout)

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('config.ini')

    domain = Freenom(cfg.get('freenom', 'username'), cfg.get('freenom', 'password'))
    domain.renew_all()
