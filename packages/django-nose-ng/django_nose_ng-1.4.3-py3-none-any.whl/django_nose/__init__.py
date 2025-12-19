"""The django_nose module."""
from importlib.metadata import PackageNotFoundError, version

from django_nose.runner import BasicNoseRunner, NoseTestSuiteRunner
from django_nose.testcases import FastFixtureTestCase

__all__ = ["BasicNoseRunner", "NoseTestSuiteRunner", "FastFixtureTestCase", "__version__"]

try:
    __version__ = version("django-nose-ng")
except PackageNotFoundError:
    __version__ = "0.0.0"
