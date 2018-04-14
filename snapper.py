#!/usr/bin/env python
from argparse import ArgumentParser
import os.path
import os
from subprocess import run


import pygments
from pygments.lexers import shell
from pygments.formatters import HtmlFormatter

root = '/var/www/html'
ziproot = root + '/zipfiles'
compile_snap = ['./makesnap.sh']  # list of CLI args
run_snap = ['./runsnap.sh']

def main(zipfile, source):
    '''(str, str) -> (str, str)
    Accepts 2 file paths
    Returns output, code as HTML string
    '''
    zipfile = zipfile.replace('.zip', '')
    zipdir = ziproot + '/' + zipfile
    if not os.exists(zipdir):
        os.makedirs(zipdir)
    run(['unzip', '-d', zipdir, zipfile])  # unzip automatically adds extension
    if not any(f.lower() == 'makefile' for f in os.listdir(zipdir)):
        raise ValueError("Zip file must contain a makefile")
    run(compile_snap)
    # decode required so string, not bytes
    output = run(run_snap, stdout=subprocess.PIPE).stdout.decode()
    output = pygments.highlight(output, shell(), HtmlFormatter())
    return output, code
    

if __name__ == '__main__':
    parser = ArgumentParser(__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("source")
    main(parser.parse_args())
