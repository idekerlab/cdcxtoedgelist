#!/usr/bin/env python

import os
import sys
import argparse
import traceback
import subprocess
import uuid
import csv
import shutil

DEFAULT_ERR_MSG = ('Did not get any clusters from HiDeF. Not sure'
                   ' what is going on\n')

X_PREFIX = 'x'

CDRES_KEY_NAME = 'communityDetectionResult'

NODE_CX_KEY_NAME = 'nodeAttributesAsCX2'

ATTR_DEC_NAME = 'attributeDeclarations'

PERSISTENCE_COL_NAME = 'HiDeF_persistence'


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


def _parse_arguments(desc, args):
    """
    Parses command line arguments
    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('input',
                        help='Network in CX format')
    parser.add_argument('--n', type=int,
                        help='Target community number. Explore the'
                             'maximum resolution parameter until the '
                             'number of generated communities at this '
                             'resolution is close enough to this value. '
                             'Increase to get more smaller communities')
    parser.add_argument('--weight',
                        help='Optional, name of node column containing edge weights')
    parser.add_argument('--tempdir', default='/tmp',
                        help='Directory needed to hold files temporarily for processing')
    return parser.parse_args(args)


def create_tmpdir(theargs):
    """
    Creates temp directory for hidef output with
    a unique name of format cdcxtoedgelist_<UUID>

    :param theargs: Holds attributes from argparse
    :type theargs: `:py:class:`argparse.Namespace`
    :return: Path to temp directory
    :rtype: str
    """
    tmpdir = os.path.join(theargs.tempdir, 'cdcxtoedgelist_' + str(uuid.uuid4()))
    os.makedirs(tmpdir, mode=0o755)
    return tmpdir


def convert_hidef_output_to_cdaps(out_stream, tempdir, prefix=X_PREFIX,
                                  include_mapping=False):
    """
    Looks for x.nodes and x.edges in `tempdir` directory
    to generate output in COMMUNITYDETECTRESULT format:
    https://github.com/idekerlab/communitydetection-rest-server/wiki/COMMUNITYDETECTRESULT-format

    This method leverages

    :py:func:`#write_members_for_row`

    and

    :py:func:`#write_communities`

    to write output

    :param out_stream: output stream to write results
    :type out_stream: file like object
    :param tempdir:
    :type tempdir: str
    :return: None
    """
    nodefile = os.path.join(tempdir, prefix + '.nodes')
    max_node_id = get_max_node_id(nodefile)
    cluster_node_map = {}
    persistence_map = {}
    out_stream.write('{"communityDetectionResult": "')
    with open(nodefile, 'r') as csvfile:
        linereader = csv.reader(csvfile, delimiter='\t')
        for row in linereader:
            max_node_id, cur_node_id = update_cluster_node_map(cluster_node_map,
                                                               row[0],
                                                               max_node_id)
            update_persistence_map(persistence_map, cur_node_id, row[-1])
            write_members_for_row(out_stream, row,
                                  cur_node_id)
    edge_file = os.path.join(tempdir, prefix + '.edges')
    write_communities(out_stream, edge_file, cluster_node_map)
    if include_mapping is not None and include_mapping is True:
        write_cluster_mapping(out_stream, cluster_node_map)
    write_persistence_node_attribute(out_stream, persistence_map)

    out_stream.write('\n')
    return None


def run_cxtoedgelist(theargs, out_stream=sys.stdout,
                     err_stream=sys.stderr):
    """
    Runs hidef command line program and then converts
    output to CDAPS compatible format that is output to
    standard out.

    :param theargs: Holds attributes from argparse
    :type theargs: `:py:class:`argparse.Namespace`
    :param out_stream: stream for standard output
    :type out_stream: file like object
    :param err_stream: stream for standard error output
    :type err_stream: file like object
    :return: 0 upon success otherwise error
    :rtype: int
    """
    if theargs.input is None or not os.path.isfile(theargs.input):
        err_stream.write(str(theargs.input) + ' is not a file')
        return 3

    if os.path.getsize(theargs.input) == 0:
        err_stream.write(str(theargs.input) + ' is an empty file')
        return 4
    try:
        return 0
    finally:
        err_stream.flush()
        out_stream.flush()


def main(args):
    """
    Main entry point for program
    :param args: command line arguments usually :py:const:`sys.argv`
    :return: 0 for success otherwise failure
    :rtype: int
    """
    desc = """
    Runs CX to EDGELIST on command line, sending output to standard
    out
    """
    theargs = _parse_arguments(desc, args[1:])
    try:
        return run_cxtoedgelist(theargs, sys.stdout, sys.stderr)
    except Exception as e:
        sys.stderr.write('\n\nCaught exception: ' + str(e))
        traceback.print_exc()
        return 2


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
