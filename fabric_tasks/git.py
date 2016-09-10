# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from fabric.decorators import task
from fabric.operations import local, settings as fab_settings
from fabric.utils import abort


def has_uncommitted_changes():
    return bool(local("git status -s", capture=True))


def get_current_branch():
    return local("git symbolic-ref HEAD", capture=True).split('/')[-1]


@task
def push(remote='origin'):
    """ Push to origin """
    local("git push %s --tags %s" % (remote, get_current_branch()))


@task
def pull(params=''):
    """ Pull files from the repo -> clean """
    local("git add --all .")
    if has_uncommitted_changes():
        abort('There are uncommited changes')
    with fab_settings(warn_only=True):
        local("git pull --no-edit origin %s %s" % (get_current_branch(), params))
    local("git clean -d -f --interactive")
    local("git status")


@task
def commit(message=None):
    """ Add all files in the repo -> commit """
    local("git add --all .")
    with fab_settings(warn_only=True):
        local("git commit -m '%s'" % message or 'no-msg commit')


@task
def delete_branch(branch_name):
    """ Delete branch """
    if branch_name == get_current_branch():
        abort('You have to switch to another branch')
    with fab_settings(warn_only=True):
        local("git branch -D %s" % branch_name)
        local("git push origin --delete %s" % branch_name)


@task
def prune_branches():
    """ Sync local branch list with origin """
    local("git fetch --prune")
