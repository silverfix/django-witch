# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division
from django.conf import settings
from fabric.context_managers import hide
from fabric.decorators import task
from fabric.operations import local, settings as fab_settings

DB = settings.DATABASES['default']


@task
def dump(filepath='db.dump'):
    """Issues pg_dump using proper django settings"""
    return local(
        'pg_dump --username=%s --host=%s -Fc %s > %s' % (DB['USER'], DB['HOST'], DB['NAME'], filepath)
    )


@task
def restore(filepath):
    """Issues pg_restore using proper django settings"""
    return local(
        'pg_restore --username=%s --host=%s --dbname=%s %s' % (DB['USER'], DB['HOST'], DB['NAME'], filepath)
    )


@task
def exists():
    """Check if DB exists"""
    with fab_settings(hide('warnings'), warn_only=True):
        result = local(
            'psql --username=%s --dbname=%s --host=%s --command="\q"' % (DB['USER'], DB['NAME'], DB['HOST'])
        )
    return result.succeeded


@task
def shell(user=None):
    """Open PostgreSQL shell using proper django settings"""
    user = user or DB['USER']
    return local('psql --username=%s --dbname=postgres --host=%s' % (user, DB['HOST']))


@task
def psql_cmd(cmd, user=None):
    """Issues a command to psql using proper django settings"""
    user = user or DB['USER']
    return local(
        'psql --username=%s --dbname=postgres --host=%s --command="%s"' % (user, DB['HOST'], cmd)
    )


@task
def create_db():
    """Create DB"""
    if exists():
        print "Cannot create DB %s: it exists already" % DB['NAME']
    else:
        print psql_cmd('CREATE DATABASE %s WITH ENCODING=\'UTF8\' CONNECTION LIMIT=-1' % DB['NAME'])


@task
def drop_db():
    """Drop DB"""
    if not exists():
        print "Cannot drop DB %s: it doesn't exist" % DB['NAME']
    else:
        print psql_cmd('drop database %s' % DB['NAME'])


@task
def create_user(superuser='postgres'):
    """Create user"""
    print psql_cmd("CREATE USER %s WITH PASSWORD '%s'" % (DB['USER'], DB['PASSWORD']), user=superuser)
    print psql_cmd("ALTER USER %s WITH SUPERUSER" % DB['USER'], user=superuser)


@task
def drop_user(superuser='postgres'):
    """Drop user"""
    print psql_cmd("DROP USER %s" % DB['USER'], user=superuser)
