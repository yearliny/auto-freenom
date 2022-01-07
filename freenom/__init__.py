# -*- coding: utf-8 -*-
import logging

from .Freenom import Freenom
from .MailSender import MailSender

logging.getLogger(__name__).addHandler(logging.NullHandler())
