#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
import os.path
import os
import fileinput
from subprocess import PIPE, Popen, run
from shutil import rmtree

import pygments
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

ziproot = 'zip'
saveroot = 'snaps'
compile_snap = 'makesnap.sh'
run_snap = 'runsnap.sh'
diff = 'diff'

def file_diff(codefile, prevcodefile):
    '''
    Diffs the code file to previous code file then returns list of tuples with
        lines which are changes
    Parameters are both strings containing valid paths to code source
    '''
    output = run([diff, codefile, prevcodefile], stdout=PIPE).stdout.decode()
    changes = []
    for line in output.split():
        if len(line) <= 0 or line[0] in "<>- ":
            continue  #Break because we only want the numbers of where diffs are
        for i in range(len(line)):
            if line[i] in "ac":
                #This is an addition or change so use it
                indeces = [int(x) for x in line[i+1:].strip().split(',')]
                if len(indeces) == 1:
                    end = int(indeces[0])
                    start = end - 1
                elif len(indeces) == 2:
                    start = indeces[0] - 1
                    end = indeces[1]
                else:
                    print("Diff output is weird")
                changes.append((start, end))
                break
    return changes

def add_strongs(strong_lines, codehtmlfile):
    '''
    Parses html which is result of pygments to add html strong tags at specified
        strong_lines
    Parameter strong_lines is list of integer pairs which have [start, end)
        line numbers starting from index 0
    '''
    if len(strong_lines) == 0:
        return
    i = 0
    current = strong_lines[0]
    state = 'START'
    prefix = '<div class="highlight"><pre>'
    with fileinput.input(codehtmlfile, inplace=True) as f:
        for number, line in enumerate(f):
            if i < len(strong_lines):
                current = strong_lines[i]
                if number == 0:
                    line = line[len(prefix):]
                    #TODO(HD) deal with the div,pre on first line
                if state == 'START' and number == current[0]:
                    line = '<strong>' + line
                    modified = True
                    state = 'END'
                if state == 'END' and number + 1 == current[1]:
                    line += '</strong>'
                    modified = True
                    state = 'START'
                    i += 1
            if number == 0:
                line = prefix + line
            print(line, end='')

def main(zipfile, source):
    '''(str, str) Accepts 2 file paths
    Returns nothing
    For each version of source, store code and output on disk in HTML format
    '''
    zipfile = zipfile.replace('.zip', '')
    zipdir = ziproot + '/' + os.path.basename(zipfile)
    savedir = saveroot + '/' + os.path.basename(zipfile)

    if not os.path.isdir(zipdir):
        os.makedirs(zipdir)
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    run(['unzip', '-u', '-o', '-q', '-d', zipdir, zipfile])  # unzip automatically adds extension

    previous = None
    for version in os.listdir(zipdir):
        original = zipdir + '/' + version
        saves = savedir + '/' + version

        # overwrite existing
        if os.path.isdir(saves):
            rmtree(saves)
        os.makedirs(saves)

        # not required
        try:
            Popen([original + '/' + compile_snap], cwd=original)
        except FileNotFoundError:
            pass
        try:
            output = Popen([original + '/' + run_snap], stdout=PIPE,
                           cwd=original).stdout.decode()
        except FileNotFoundError:
            output = ''

        pygments.highlight(output, BashLexer(), HtmlFormatter(), open(saves + '/output.html', 'x'))
        code = '\n'.join(open(original + '/' + source).readlines())
        code = pygments.highlight(code, get_lexer_for_filename(source), HtmlFormatter(), open(saves + '/code.html', 'x'))

        # add bolding
        if previous is not None:
            diff_result = file_diff(previous + '/' + source, original + '/' + source)
            add_strongs(diff_result, saves + '/code.html')

        previous = original


if __name__ == '__main__':
    parser = ArgumentParser(__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("source")
    main(**parser.parse_args().__dict__)
