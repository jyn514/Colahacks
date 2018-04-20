#!/usr/bin/env python3
import os
import fileinput
from subprocess import PIPE, Popen, run
from shutil import copyfile
import sys
import shlex

import pygments
from pygments.lexers.shell import BashLexer
from pygments.formatters import HtmlFormatter

CACHE_ROOT = '/tmp/snap'
SAVE_ROOT = os.path.expanduser('~/.cache/snap')
COMPILE = 'makesnap.sh'
RUN = 'runsnap.sh'

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


def mkdir_p(*directories):
    '''Replicate functionality of `mkdir -p directory`'''
    for directory in directories:
        if not os.path.isdir(directory):
            os.makedirs(directory)


def checkout(files, previous, current, directory):
    directory = os.path.realpath(directory)
    subdir = '/' + os.path.basename(directory)
    savedir = SAVE_ROOT + subdir + '/' + get_commit(current)
    tmpdir = CACHE_ROOT + subdir
    del subdir

    mkdir_p(savedir, tmpdir)

    for f in files:
        html = savedir + '/' + f  # NOTE: preserves extension
        if not os.path.exists(html):
            run(['git', '--work-tree', tmpdir, '--git-dir', directory + '/.git',
                 'checkout', current, f])  # makes directories if necessary

            tmpfile = tmpdir + '/' + f

            # necessary: f could be in subdir of <directory>
            mkdir_p(os.path.dirname(html))

            try:
                with open(tmpfile) as original:  # should have been checked out by git
                    code = ''.join(original.readlines())  # NOTE: preserves newlines
                lexer = pygments.lexers.guess_lexer_for_filename(f, f)
                with open(html, 'x') as result:
                    pygments.highlight(code, lexer, HtmlFormatter(), result)
            except (UnicodeDecodeError, pygments.util.ClassNotFound):
            # don't mess with binaries
                copyfile(tmpfile, html)

            # do this even if binary; git shows metadata change
            # TODO: cut back on wasteful IO
            diff = html + '.diff'
            with open(diff, 'x') as diff_file:
                Popen(['git', 'diff', previous, current, f],
                      cwd=tmpdir, stdout=diff_file)
            if not os.stat(diff).st_size:
                os.remove(diff)

    return savedir, tmpdir


def tracked(f, commit, cwd):
    '''Tell if an object is tracked in commit'''
    output = output_to_string(Popen(['git', 'ls-tree', commit, f], cwd=cwd,
                                    stdout=PIPE).stdout)
    return not (output is None or output == '')


def flatten(files, commit, directory):
    '''iterable, str, str -> list(str)
    turn directories into top-level files
    If files are untracked by git, discard with warning'''
    result = []
    for f in files:
        if os.path.isdir(f):
            # TODO: python has terribly support for recursion, make this a while loop
            output = Popen(['git', 'ls-tree', '--name-only', commit, f + '/'],
                           cwd=directory, stdout=PIPE).stdout
            # bytes to str, discarding newline
            result += flatten((b.decode()[:-1] for b in output), commit, directory)
        elif not tracked(f, commit, directory):
            print("WARNING: passed '%s' which is not tracked by git. Discarding." % f,
                  file=sys.stderr)
        else:
            result += [f]
    return result


def compile_and_run(tmpdir):
    # not required
    try:
        Popen(['./' + COMPILE], cwd=tmpdir)
    except FileNotFoundError:
        pass
    # we assume that all output will come from stdout of RUN
    try:
        return output_to_string(Popen(['./' + RUN], stdout=PIPE,
                                      cwd=tmpdir).stdout)
    except FileNotFoundError:
        return ''


def main(directory, commit="HEAD", previous="HEAD", files='.'):
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
        - html stored in SAVE_ROOT/$(basename directory)/commit/filename
            extension is preserved; does NOT end in HTML
        - diff is stored SAVE_ROOT/$(basename directory)/commit/filename.diff
            example: main(files='data.csv') ->
                     SAVE_ROOT/$(realpath .)/$(git rev-parse -h HEAD)/data.csv.diff
    '''
    if not isinstance(files, list):
        files = shlex.split(files)
    files = flatten(files, commit, directory)

    savedir, tmpdir = checkout(files, previous, commit, directory)
    output = compile_and_run(tmpdir)

    output_path = savedir + '/output.html'
    if not os.path.exists(output_path):
        with open(output_path, 'x') as output_file:
            pygments.highlight(output, BashLexer(), HtmlFormatter(), output_file)

    return "complete"


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(__doc__)
    parser.add_argument("directory", help='must have a git repository')
    parser.add_argument("commit", default="HEAD", nargs='?',
                        help='treeish (see `man gitglossary` for help)')
    #parser.add_argument('--reset', action='store_true')
    print(main(**{k: v for k, v in parser.parse_args().__dict__.items()
                  if v is not None}))
