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

    def get_raw_cx_file(self):
        return os.path.join(os.path.dirname(__file__), 'data', 'raw.cx')

    def get_cx_with_weight(self):
        return os.path.join(os.path.dirname(__file__), 'data', 'cxwithweight.json')

    def get_cx_with_emptyweight(self):
        return os.path.join(os.path.dirname(__file__), 'data', 'cxwithemptyweight.json')

    def test_parse_args_all_defaults(self):
        myargs = ['inputarg']
        res = cdcxtoedgelistcmd._parse_arguments('desc', myargs)
        self.assertEqual('inputarg', res.input)
        self.assertEqual(None, res.weight)
        self.assertEqual(False, res.failonmissingweight)
        self.assertEqual(0.0, res.default)

    def test_main_missingfile(self):
        tmpdir = tempfile.mkdtemp()
        try:
            missingfile = os.path.join(tmpdir, 'foo.json')
            res = cdcxtoedgelistcmd.main(['prog', missingfile])
            self.assertEqual(3, res)

        finally:
            shutil.rmtree(tmpdir)

    def test_main_invalidjson(self):
        tmpdir = tempfile.mkdtemp()
        try:
            invalidjson = os.path.join(tmpdir, 'bad.json')
            with open(invalidjson, 'w') as f:
                f.write('blahblah')
            res = cdcxtoedgelistcmd.main(['prog', invalidjson])
            self.assertEqual(2, res)

        finally:
            shutil.rmtree(tmpdir)


    def test_run_cxtoedgelist_emptyfile(self):
        tmpdir = tempfile.mkdtemp()
        try:
            emptyfile = os.path.join(tmpdir, 'foo.json')
            open(emptyfile, 'a').close()
            theargs = cdcxtoedgelistcmd._parse_arguments('desc',
                                                         [emptyfile])

            f_out = io.StringIO()
            f_err = io.StringIO()
            res = cdcxtoedgelistcmd.run_cxtoedgelist(theargs, err_stream=f_err,
                                                     out_stream=f_out)
            self.assertEqual(4, res)
            self.assertEqual(emptyfile + ' is an empty file', f_err.getvalue())
            self.assertEqual('', f_out.getvalue())
        finally:
            shutil.rmtree(tmpdir)

    def test_run_cxtoedgelist_rawcx(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inputfile = self.get_raw_cx_file()
            theargs = cdcxtoedgelistcmd._parse_arguments('desc',
                                                         [inputfile])

            f_out = io.StringIO()
            f_err = io.StringIO()
            res = cdcxtoedgelistcmd.run_cxtoedgelist(theargs, err_stream=f_err,
                                                     out_stream=f_out)
            self.assertEqual(0, res)
            self.assertEqual('', f_err.getvalue())
            self.assertEqual(10980, len(f_out.getvalue()))
            self.assertTrue('0\t1118\n' in f_out.getvalue())
            self.assertTrue('2\t1082\n' in f_out.getvalue())
        finally:
            shutil.rmtree(tmpdir)

    def test_run_cxtoedgelist_cxwithweight(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inputfile = self.get_cx_with_weight()
            theargs = cdcxtoedgelistcmd._parse_arguments('desc',
                                                         [inputfile])

            f_out = io.StringIO()
            f_err = io.StringIO()
            res = cdcxtoedgelistcmd.run_cxtoedgelist(theargs, err_stream=f_err,
                                                     out_stream=f_out)
            self.assertEqual(0, res)
            self.assertEqual('', f_err.getvalue())
            self.assertEqual(16749, len(f_out.getvalue()))
            self.assertTrue('0\t1118\t0.375\n' in f_out.getvalue())
            self.assertTrue('0\t1120\t0.0\n' in f_out.getvalue())
            self.assertTrue('2\t1082\t0.5\n' in f_out.getvalue())
        finally:
            shutil.rmtree(tmpdir)

    def test_run_cxtoedgelist_cxwithemptyweight(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inputfile = self.get_cx_with_emptyweight()
            theargs = cdcxtoedgelistcmd._parse_arguments('desc',
                                                         [inputfile])

            f_out = io.StringIO()
            f_err = io.StringIO()
            res = cdcxtoedgelistcmd.run_cxtoedgelist(theargs, err_stream=f_err,
                                                     out_stream=f_out)
            self.assertEqual(0, res)
            self.assertEqual('', f_err.getvalue())
            self.assertEqual(10980, len(f_out.getvalue()))
            self.assertTrue('0\t1118\n' in f_out.getvalue())
            self.assertTrue('0\t1120\n' in f_out.getvalue())
            self.assertTrue('2\t1082\n' in f_out.getvalue())
        finally:
            shutil.rmtree(tmpdir)

    def test_run_cxtoedgelist_cxwithweightfailonmissing(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inputfile = self.get_cx_with_weight()
            theargs = cdcxtoedgelistcmd._parse_arguments('desc',
                                                         [inputfile,
                                                          '--failonmissingweight'])

            f_out = io.StringIO()
            f_err = io.StringIO()
            res = cdcxtoedgelistcmd.run_cxtoedgelist(theargs, err_stream=f_err,
                                                     out_stream=f_out)
            self.assertEqual(5, res)
            self.assertTrue('lacks a value for weight column: 3', f_err.getvalue())

        finally:
            shutil.rmtree(tmpdir)


if __name__ == '__main__':
    sys.exit(unittest.main())
