# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, absolute_import

from fabric.api import env

from fabric.context_managers import cd, prefix
from fabric.decorators import task
from fabric.operations import local, run
from fabric.utils import abort
from os.path import join

from witch import utils
from witch.utils import remote, print_local, print_remote


@task
@remote
def deploy():
    """Deploy to target env"""
    deploy_branch = getattr(env, 'deploy_branch', 'deploy')
    working_branch = utils.get_current_branch()
    if working_branch == deploy_branch:
        abort('Deploying from "{}" branch is not permitted'.format(deploy_branch))

    print_local('Preparing commit and deploy branch..')
    local('git symbolic-ref HEAD refs/heads/{}'.format(deploy_branch))
    local('git add --all .')
    local('git commit --allow-empty -m \'Deploy {} @ {}\''.format(working_branch, env.stage['name']))
    local('git symbolic-ref HEAD refs/heads/{}'.format(working_branch))
    local('git reset')

    print_local('Pushing to origin/{}..'.format(deploy_branch))
    local('git push -f origin {}'.format(deploy_branch))

    with cd(env.stage['project_root']), prefix(env.stage['venv_command']):
        print_remote('Fetching from origin/{}..'.format(deploy_branch))
        run('git fetch origin {}'.format(deploy_branch))
        run('git reset --hard origin/{}'.format(deploy_branch))
        run('git clean --force -d')
        print_remote('Pointing settings to the right stage..')
        run('cp {stage_settings} {current_settings}'.format(
            stage_settings=join(env.stage['settings_root'], '{}.py'.format(env.stage['name'])),
            current_settings=join(env.stage['settings_root'], 'CURRENT.py')
        ))
        print_remote('Running pip install..')
        run('pip install -r requirements.txt')
        print_remote('Deleting old *.pyc files..')
        run('find . -name \*.pyc -delete')
        print_remote('Running manage.py migrate..')
        run('python manage.py migrate')
        print_remote('Running manage.py collectstatic..')
        run('python manage.py collectstatic --clear --noinput')
        print_remote('Triggering graceful reload..')
        run('touch {}'.format(env.stage['uwsgi_ini']))


# TODO rewrite as the draft below
# @task
# def fetch():
#     """--> Align env.db_selected/migrations/media from target"""
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
# def fetchdb(target_stage='prod'):
#     """--> Align env.db_selected/migrations/media from target"""
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
