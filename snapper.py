#!/usr/bin/env python3
import os
import fileinput
from subprocess import PIPE, Popen, run
from shutil import rmtree
import sys
import shlex

import pygments
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

cacheroot = '.cache'
saveroot = 'snaps'
compile_snap = 'makesnap.sh'
run_snap = 'runsnap.sh'

def file_diff(codefile, prevcodefile):
    '''
    Diffs the code file to previous code file then returns list of tuples with
        lines which are changes
    Parameters are both strings containing valid paths to code source
    '''
    output = run(['diff', codefile, prevcodefile], stdout=PIPE).stdout.decode()
    changes = []
    for line in output.split():
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


def output_to_string(output):
    '''bytes -> str'''
    return '\n'.join(i.decode() for i in output)


def get_commit(treeish='HEAD', directory='.'):
    'str -> str'
    args = ['git', 'show-ref']
    if treeish == 'HEAD':
        args += ['-h', 'HEAD']
    else:
        args += [treeish]
    return output_to_string(Popen(args, stdout=PIPE, cwd=directory).stdout).split(' ')[0]


def checkout(f, previous, current, directory):
    '''TODO: take list as a parameter, this is a mess and super slow'''
    # don't change HEAD, just get files
    directory = os.path.realpath(directory)
    subdir = '/' + os.path.basename(directory)
    savedir = saveroot + subdir + '/' + get_commit(current)
    tmpdir = cacheroot + subdir

    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)
        with open(tmpdir + '/.git', 'w') as git:
            git.write('gitdir: ' + directory + '/.git\n')
    if not os.path.isdir(savedir):
        os.makedirs(savedir)

    html = "%s/%s" % (savedir, f)  # NOTE: preserves extension
    if not os.path.exists(html):
        Popen(['git', 'checkout', current, f], cwd=tmpdir)
        with open(tmpdir + '/' + f) as original:
            code = ''.join(original.readlines())  # NOTE: preserves newlines
        with open(html, 'x') as result:
            pygments.highlight(code, get_lexer_for_filename(f), HtmlFormatter(), result)
    if not os.path.exists(html + '.diff'):
        with open(html + '.diff', 'x') as diff:
            Popen(['git', 'diff', previous, current, f],
                    cwd=tmpdir, stdout=diff)


def checkout_all(files, previous, current, directory):
    for f in files:
        if os.path.isdir(f):
            # get only top-level files
            checkout_all(os.walk(f).__next__()[2], previous, current, directory)
        else:
            checkout(f, previous, current, directory)


def compile_and_run(tmpdir):
    '''TODO: should copy first then compile'''
    # not required
    try:
        Popen(['./' + compile_snap], cwd=tmpdir)
    except FileNotFoundError:
        pass
    # we assume that all output will come from stdout of run_snap
    try:
        return output_to_string(Popen(['./' + run_snap], stdout=PIPE,
                                cwd=tmpdir).stdout)
    except FileNotFoundError:
        return ''


def main(directory='.', commit="HEAD", previous="HEAD", files='.'):
    '''(str, str) -> None
    files should be one of:
        - list of file names (basename only, no directory path)
        - str of CLI arguments exactly as normally passed to `git checkout`
          Example: main('~', files='snappy.py README.md "file with spaces"')
    directory can be either absolute or relative
        WARNING: if $(basename directory) already exists AND has different git history,
        hash collisions may occur; files from other project will be overwritten
    commit: tree-ish (see `man gitglossary`; usually commit, tag, or branch)
    previous: tree-ish
    output:
        - html stored in saveroot/$(basename directory)/commit/filename
            extension is preserved; does NOT end in HTML
        - diff is stored saveroot/$(basename directory)/commit/filename.diff
            example: main(files='data.csv') ->
                     saveroot/$(realpath .)/$(git rev-parse -h HEAD)/data.csv.diff
    '''
    if not isinstance(files, list):
        files = shlex.split(files)

    checkout_all(files, previous, commit, directory)
    output = compile_and_run()

    output_path = savedir + '/output.html'
    if not os.path.exists(output_path):
        with open(output_path, 'x') as output_file:
            pygments.highlight(output, BashLexer(), HtmlFormatter(), output_file)

    return "complete"


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(__doc__)
    parser.add_argument("directory", help='must have a git repository', default='.',
                        nargs='?')
    parser.add_argument("commit", default="HEAD", nargs='?',
                        help='treeish (see `man gitglossary` for help)')
    #parser.add_argument('--reset', action='store_true')
    print(main(**{k: v for k, v in parser.parse_args().__dict__.items()
                  if v is not None}))
