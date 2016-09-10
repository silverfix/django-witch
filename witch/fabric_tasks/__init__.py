# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from django.conf import settings
from fabric.api import env
from fabric.operations import os


PROJECT_NAME = os.path.split(settings.BASE_DIR)[-1]
env.keepalive = 30