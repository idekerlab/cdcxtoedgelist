#!/usr/bin/env python

import os
import sys
import argparse
import traceback
import json
import ndex2


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
    parser.add_argument('--default', default=0.0,
                        help='if --weight is set, but a given edge lacks a value, this'
                             'value will be output instead')
    parser.add_argument('--failonmissingweight', action='store_true',
                        help='If set, fail if weight column is set by and one or '
                             'more edges lack a weight value')
    return parser.parse_args(args)


def run_cxtoedgelist(theargs, out_stream=sys.stdout,
                     err_stream=sys.stderr):
    """
    Converts CX file set via theargs.input to EDGE LIST of format
    The optional weight is set if theargs.weight is not ``None``
    and matches a node column in CX

    ..code-block::

        SOURCE\tTARGET\t(optional weight)\n


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
        weight_col = None
        default_weight = str(theargs.default)
        with open(theargs.input, 'r') as f:
            raw_json = json.load(f)
            if 'weight' in raw_json:
                weight_col = raw_json['weight']
                if weight_col is not None and len(str(weight_col).strip()) == 0:
                    weight_col = None
            if 'cx' not in raw_json:
                # just try to read the CX directly
                raw_json_to_load = raw_json
            else:
                raw_json_to_load = raw_json['cx']
            net = ndex2.create_nice_cx_from_raw_cx(raw_json_to_load)

            for edge_id, edge_obj in net.get_edges():
                out_stream.write(str(edge_obj['s']) + '\t' + str(edge_obj['t']))
                if weight_col is not None:
                    edge_attr = net.get_edge_attribute(edge_id, weight_col)
                    if edge_attr == (None, None) or edge_attr is None:
                        if theargs.failonmissingweight:
                            err_stream.write('\nEdge: ' + str(edge_obj) +
                                             ' lacks a value for '
                                             'weight column: ' +
                                             str(weight_col) + '\n')
                            return 2
                        out_stream.write('\t' + default_weight)
                    else:
                        out_stream.write('\t' + str(edge_attr['v']))
                out_stream.write('\n')
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
