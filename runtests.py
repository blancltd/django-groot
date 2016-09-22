#!/usr/bin/env python
import os
import sys
import subprocess

import django
from django.conf import settings
from django.test.utils import get_runner

FLAKE8_ARGS = ['tests', 'groot', '--ignore=E501']


def run_flake8_tests(args):
    command = subprocess.call(['flake8'] + args)
    print("" if command else "Success. flake8 passed.")
    return command


def run_django_tests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['tests'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_flake8_tests(FLAKE8_ARGS)
    run_django_tests()
