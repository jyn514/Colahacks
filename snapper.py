#! /usr/bin/env python3

import os
from os import makedirs, listdir
import os.path
from os.path import join as pathjoin, basename, isdir, exists as pathexists
import fileinput
from subprocess import PIPE, Popen, run
from shutil import rmtree, which
import sys

import pygments
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

ziproot = 'zip'
saveroot = 'snaps'
compile_snap = 'makesnap.sh'
run_snap = 'runsnap.sh'

sh_cmd = which('sh')
diff_cmd = which('diff')
unzip_cmd = which('unzip')

def file_diff(codefile, prevcodefile):
    '''
    Diffs the code file to previous code file then returns list of tuples with
        lines which are changes
    Parameters are both strings containing valid paths to code source
    '''
    output = run([diff_cmd, codefile, prevcodefile], stdout=PIPE).stdout.decode()
    changes = []
    for line in output.splitlines():
        if len(line) <= 0 or line[0] in "<>- ":
            continue  # we only want the numbers of where diffs are
        for i, char in enumerate(line):
            if char in "ac":
                # addition or change so use it
                indices = [int(x) for x in line[i+1:].strip().split(',')]
                if len(indices) == 1:
                    end = int(indices[0])
                    start = end - 1
                elif len(indices) == 2:
                    start = indices[0] - 1
                    end = indices[1]
                else:
                    print("Diff output is weird", file=sys.stderr)
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
    if not strong_lines:
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
                    state = 'END'
                if state == 'END' and number + 1 == current[1]:
                    line += '</strong>'
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
    zipdir = pathjoin(ziproot, basename(zipfile))
    savedir = pathjoin(saveroot, basename(zipfile))

    if not isdir(zipdir):
        makedirs(zipdir)
    if not isdir(savedir):
        makedirs(savedir)

    run([unzip_cmd, '-u', '-o', '-q', '-d', zipdir, zipfile])  # unzip automatically adds extension
#    run(['chmod', '-R', '777', zipdir])

    previous = None
    for version in sorted(listdir(zipdir)):
        original = pathjoin(zipdir, version)
        saves = pathjoin(savedir, version)

        # overwrite existing
        if isdir(saves):
            rmtree(saves)
        makedirs(saves)

        # not required
        compile_output = ''
        if pathexists(pathjoin(original, compile_snap)):
            try:
                compile_output = run([sh_cmd, compile_snap],
                        stdout=PIPE, cwd=original).stdout.decode()
            except FileNotFoundError:
                pass  # Shouldn't happen but just in case

        output = ''
        if pathexists(pathjoin(original, run_snap)):
            try:
                output = run([sh_cmd, run_snap],
                        stdout=PIPE, cwd=original).stdout.decode()
                # output = '\n'.join(i.decode() for i in output)
            except FileNotFoundError:
                pass  # Shouldn't happen but just in case
            except OSError as e:
                output = 'OSError in snap %s\n%s' % (version, e)

        pygments.highlight(output, BashLexer(), HtmlFormatter(),
                open(pathjoin(saves, 'output.html'), 'x'))
        code = ''.join(open(pathjoin(original, source)).readlines())
        code = pygments.highlight(code, get_lexer_for_filename(source),
                HtmlFormatter(), open(pathjoin(saves, 'code.html'), 'x'))

        # add bolding
        if previous is not None:
            diff_result = file_diff(pathjoin(previous, source), pathjoin(original, source))
            add_strongs(diff_result, pathjoin(saves, 'code.html'))

        previous = original


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(__doc__)
    parser.add_argument("zipfile")
    parser.add_argument("source")
    main(**parser.parse_args().__dict__)
