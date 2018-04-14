#!/usr/bin/env python
from argparse import ArgumentParser
import os.path
import os
from subprocess import run, PIPE
from shutil import rmtree

import pygments
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

root = '/home/joshua/var/www/html'
ziproot = root + '/zip'
saveroot = root + '/snaps'
compile_snap = 'makesnap.sh'
run_snap = 'runsnap.sh'

def main(zipfile, source):
    '''(str, str) Accepts 2 file paths
    Returns nothing
    For each version of source, store code and output on disk
    '''
    zipfile = zipfile.replace('.zip', '')
    zipdir = ziproot + '/' + os.path.basename(zipfile)
    savedir = saveroot + '/' + os.path.basename(zipfile)

    if not os.path.isdir(zipdir):
        os.makedirs(zipdir)
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    run(['unzip', '-u', '-o', '-d', zipdir, zipfile])  # unzip automatically adds extension
    
    for version in os.listdir(zipdir):
        original = zipdir + '/' + version
        saves = savedir + '/' + version
        if os.path.isdir(saves):
            rmtree(saves)
        os.makedirs(saves)
        try:
            run([original + '/' + compile_snap])
        except FileNotFoundError:
            pass
        # decode required so string, not bytes
        try:
            output = run([original + '/' + run_snap], stdout=PIPE).stdout.decode()
        except FileNotFoundError:
            output = ''
        pygments.highlight(output, BashLexer(), HtmlFormatter(), open(saves + '/output.html', 'x'))
        code = '\n'.join(open(original + '/' + source).readlines())
        code = pygments.highlight(code, get_lexer_for_filename(source), HtmlFormatter(), open(saves + '/code.html', 'x'))


if __name__ == '__main__':
    parser = ArgumentParser(__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("source")
    main(**parser.parse_args().__dict__)
