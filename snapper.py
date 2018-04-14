#!/usr/bin/env python
from argparse import ArgumentParser
import os.path
import os
from subprocess import run


import pygments
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

root = '/var/www/html'
ziproot = root + '/zip'
saveroot = root + '/snaps'
compile_snap = ['./makesnap.sh']  # list of CLI args
run_snap = ['./runsnap.sh']

def file_diff(codefile, prevcodefile):
    '''
    Diffs the code file to previous code file then returns list of tuples with
        lines which are changes
    Parameters are both strings containing valid paths to code source
    '''
    with code, prevcode as open(codefile, "r"), open(prevcodefile, "r"):
        pass #TODO(HD)

def add_strongs(strong_lines, codehtmlfile):
    '''
    Parses html which is result of pygments to add html strong tags at specified
        strong_lines
    Parameter strong_lines is list of integer pairs which have [start, end)
        line numbers starting from index 0
    '''
    pass #TODO(HD)

def main(zipfile, source):
    '''(str, str) Accepts 2 file paths
    Returns nothing
    For each version of source, store code and output on disk
    '''
    zipfile = zipfile.replace('.zip', '')
    zipdir = ziproot + '/' + zipfile
    savedir = saveroot + '/' + zipfile

    if not os.exists(zipdir):
        os.makedirs(zipdir)
    if not os.exists(savedir):
        os.makedirs(savedir)

    run(['unzip', '-d', zipdir, zipfile])  # unzip automatically adds extension

    for version in os.listdir(zipdir):
        run(compile_snap)
        # decode required so string, not bytes
        output = run(run_snap, stdout=version).stdout.decode()
        pygments.highlight(output, BashLexer(), HtmlFormatter(), version + '/output.html')
        code = pygments.highlight(version, get_lexer_for_filename(source)(), HtmlFormatter(), version + '/code.html')



if __name__ == '__main__':
    parser = ArgumentParser(__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("source")
    main(parser.parse_args())
