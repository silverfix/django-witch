# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import
from importlib import import_module
from django.conf import settings
from fabric.context_managers import cd
from fabric.decorators import task
from fabric.operations import local, run
from django_zilla.fabric_tasks import PROJECT_NAME
from django_zilla.fabric_tasks.git import get_current_branch
# from django_zilla.fabric_tasks import db

DEFAULT_TARGET_STAGE = 'prod'


@task
def deploy(target_stage=DEFAULT_TARGET_STAGE):
    """ --> [REMOTE] Deploy to target env """
    static_dist_root = getattr(settings, 'STATIC_DIST_ROOT', None)
    local("git add --all .")
    static_dist_root and local("git add -f %s" % static_dist_root)
    local("git commit --allow-empty -m 'deploy %s/%s'" % (PROJECT_NAME, target_stage))
    local("git push %s %s -f" % (target_stage, get_current_branch()))
    static_dist_root and local("git rm -r --cached %s" % static_dist_root)
    static_dist_root and local("git commit --amend -a --no-edit --allow-empty")


# @task
# def fetch():
#     """ --> [REMOTE] Align env.db_selected/migrations/media from target """
#     settings_remote = import_module(name='%s.%s' % (settings.SETTINGS_PATH, env.target_stage))
#     db_remote = settings_remote.DATABASES['default']
#     media_dirname = os.path.split(settings.MEDIA_ROOT)[-1]
#     print local('rsync --delete -azvvo -e "%s" %s:/srv/www/%s/%s/ %s/'
#                 % (get_ssh_command(), env.host_string, PROJECT_NAME, media_dirname, media_dirname))
#     with cd('/srv/www/%s/' % PROJECT_NAME):
#         print run('pg_dump --username=%s --host=%s -Fc %s > temp.dump' \
#                   % (db_remote['USER'], db_remote['HOST'], db_remote['NAME']))
#         print local('scp -P %s -i %s -r -q %s:%s/temp.dump .' %
#                     (env.port, env.key_filename, env.host_string, PROJECT_NAME))
#         print sudo('rm -f temp.dump')
#         print drop()
#         print create()
#         print restore('temp.dump')
#         print local('rm temp.dump')


# TODO here the draft
# @task
# def fetchdb(target_stage):
#     """ --> [REMOTE] Align env.db_selected/migrations/media from target """
#     settings_remote = import_module(name='%s.%s' % (settings.SETTINGS_PATH, target_stage))
#     db_remote = settings_remote.DATABASES['default']
#     with cd('/srv/www/%s/' % PROJECT_NAME):
#         print run('pg_dump --username=%s --host=%s -Fc %s > temp.dump' \
#                  % (db_remote['USER'], db_remote['HOST'], db_remote['NAME']))
#         print run('git add -f temp.dump')
#         print run('git add -f media/')
#         print run('git commit -m db.fetch')
#         print run('rm -f temp.dump')
#         print local('git pull %s' % target_stage)
#         print db.drop()
#         print db.create()
#         print db.restore('temp.dump')
#         print local('rm temp.dump')