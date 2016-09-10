# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from django.conf import settings
from django.core.cache import cache
from django_zilla.utils import redis_utils
from fabric.decorators import task
from django.contrib.contenttypes.models import ContentType


@task
def clean_contenttypes():
    """Clean django ContentType model"""
    for c in ContentType.objects.all():
        if not c.model_class():
            print 'Deleting [{}.{}]'.format(c.app_label, c.model)
            confirm = raw_input("Are you sure? Type 'yes' to continue: ")
            if confirm == 'yes':
                c.delete()
    print 'Finished.'


@task
def flush_cache():
    """Flush django default cache"""
    cache.clear()
    redis_utils.reset_stats()
    print 'Cache flushed.'


@task
def clear_sessions():
    """Clear django sessions"""
    cache_session = cache.get_cache(settings.SESSION_CACHE_ALIAS)
    cache_session.clear()
    redis_utils.reset_stats()
    print 'Sessions cleared.'
