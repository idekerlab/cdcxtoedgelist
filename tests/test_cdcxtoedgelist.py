#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_cdcxtoedgelist
----------------------------------

Tests for `cdcxtoedgelist` module.
"""

import os
import sys
import unittest
import tempfile
import shutil
import io
import stat
import json
from unittest.mock import MagicMock
from cdcxtoedgelist import cdcxtoedgelistcmd


class Testcdcxtoedgelist(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_args_all_defaults(self):
        myargs = ['inputarg']
        res = cdcxtoedgelistcmd._parse_arguments('desc', myargs)
        self.assertEqual('inputarg', res.input)
        self.assertEqual(None, res.n)
        self.assertEqual(5, res.k)
        self.assertEqual(25.0, res.maxres)
        self.assertEqual(75, res.p)
        self.assertEqual('leiden', res.alg)
        self.assertEqual('hidef_finder.py', res.hidefcmd)
        self.assertEqual('/tmp', res.tempdir)


if __name__ == '__main__':
    sys.exit(unittest.main())
