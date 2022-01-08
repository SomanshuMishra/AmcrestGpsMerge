from __future__ import absolute_import, unicode_literals
from celery import task
from .models import *


@task()
def task_number_one():
	harsh = ObdMarkers.objects.last()
	harsh.protocol = 'mayur'
	harsh.save()
    print('I am Running Dude')
