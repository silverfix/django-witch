# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import, print_function

from functools import wraps

from fabric import colors
from fabric.api import settings as fabric_settings, hide
from fabric.operations import local
from fabric.state import env


_PRINT_JUSTIFY_N_CHAR = 10


def get_current_branch():
    return local('git symbolic-ref HEAD', capture=True).split('/')[-1]


def uncommitted_changes():
    with hide('warnings'), fabric_settings(warn_only=True):
        diff_index = local('git diff --quiet HEAD')
        return bool(diff_index.return_code)


def remote(task):
    @wraps(task)
    def wrapper(*args, **kwargs):
        if not env.roles:
            raise ValueError(colors.red('Need to specify some target role with "fab -R rolename .."'))
        env.stage = env.roledefs[env.roles[0]]
        return task(*args, **kwargs)
    return wrapper


def print_local(msg):
    return print('{} {}'.format(
        colors.magenta('[LOCAL]'.ljust(_PRINT_JUSTIFY_N_CHAR, ' ')),
        colors.yellow(msg)
    ))


def print_remote(msg):
    return print('{} {}'.format(
        colors.magenta('[REMOTE]'.ljust(_PRINT_JUSTIFY_N_CHAR, ' ')),
        colors.green(msg)
    ))
