"""Tests for `alburnum.maas.flesh.profiles`."""

__all__ = []

from io import StringIO
import sys
from textwrap import dedent

from alburnum.maas.testing import TestCase

from .. import profiles
from ...utils.tests.test_profiles import make_profile


class TestLoginBase(TestCase):
    """Tests for `cmd_login_base`."""

    def test_print_whats_next(self):
        profile = make_profile()
        stdout = self.patch(sys, "stdout", StringIO())
        profiles.cmd_login_base.print_whats_next(profile)
        expected = dedent("""\
            Congratulations! You are logged in to the MAAS
            server at {profile.url} with the profile name
            {profile.name}.

            For help with the available commands, try:

              maas --help

            """).format(profile=profile)
        observed = stdout.getvalue()
        self.assertDocTestMatches(expected, observed)
