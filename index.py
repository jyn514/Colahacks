#!/usr/bin/env python3
import os
import shutil
from zipfile import ZipFile, ZipInfo

from flask import Flask, render_template, app, request, session, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug import secure_filename

from webui import WebUI

import snapper
from snapper import SAVE_ROOT

UPLOADS_DIR = os.path.join(SAVE_ROOT, 'uploads')
PROJECTS_DIR = SAVE_ROOT  # os.path.join(SAVE_ROOT, 'projects')  # TODO(HD) projects probably should be kept in a subdirectory

app = Flask(__name__)
ui = WebUI(app, debug=True)  # TODO(HD) remove debug


# Patch for lost file permissions provided on StackOverflow by Anthon
# https://stackoverflow.com/questions/39296101/python-zipfile-removes-execute-permissions-from-binaries/39296577#39296577
class PatchedZipFile(ZipFile):
    def extract(self, member, path=None, pwd=None):
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()
        else:
            path = os.fspath(path)

        ret_val = self._extract_member(member, path, pwd)
        attr = member.external_attr >> 16
        os.chmod(ret_val, attr)
        return ret_val

    def extractall(self, path=None, members=None, pwd=None):
        if members is None:
            members = self.namelist()

        for zipinfo in members:
            self.extract(zipinfo, path, pwd)

class FileUploadForm(FlaskForm):
    file = FileField(validators=[
        FileRequired(),
        FileAllowed(['zip'], 'Must be zip archive')
    ])

def consolidate_dir(dir):
    '''
    Returns list of all files recursively in dir with relative path as tuple
        (path, is_file) where is_file is true when file is not directory
    '''
    subfiles = set()

    def _consolidate_dir(dir, root_path=None):
        if not root_path:
            root_path = dir
        this_path, subdirs, subs = next(os.walk(dir))
        for subfile in subs:
            subfiles.add((os.path.join(dir, subfile).split(root_path, 1)[-1], True))
        for subdir in subdirs:
            subfiles.add((os.path.join(dir, subdir).split(root_path, 1)[-1], False))
            _consolidate_dir(os.path.join(dir, subdir), root_path=root_path)

    for snap in next(os.walk(dir))[1]:
        _consolidate_dir(os.path.join(dir, snap + os.sep))
    subfiles.discard(("output.html", True))  #TODO(HD) Hopefully this will eventually be unnecessary

    return list(sorted(subfiles, key=lambda x: x[0]))

def consolidated_dirtree(dir):
    '''
    Returns directory tree with each file/folder represented
        (name, level, is_file, rel_path) where
        level is number of subdirectories above the file starting from 0
        is_file is true when the file is not a directory
        rel_path is path starting from project root
    '''
    file_tree = []

    for file, is_file in consolidate_dir(dir):
        file_split = file.split(os.sep)
        name = file_split[-1]
        level = len(file_split) - 1
        file_tree.append((name, level, is_file, file))

    return file_tree

@app.route("/", methods = ['GET', 'POST'])
def main():
    other_vars = dict()
    if "clear" in request.args:
        session.clear()

    if not os.path.isdir(SAVE_ROOT):
        os.makedirs(SAVE_ROOT, exist_ok=True)
    other_vars['dirs'] = os.listdir(PROJECTS_DIR)
    if 'uploads' in other_vars['dirs']: other_vars['dirs'].remove('uploads')  #TODO(HD) hopefully not necessary once projects receive their own directory
    app.config['SAVE_ROOT'] = SAVE_ROOT

    project = request.values.get("project") or session.get('project', None)

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(PROJECTS_DIR, exist_ok=True)

    form = FileUploadForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            project_name = filename.rsplit(".zip", 1)[0]
            saved_zip = os.path.join(UPLOADS_DIR, filename)
            form.file.data.save(saved_zip)
            project_save_dir = os.path.join(UPLOADS_DIR, project_name)

            if os.path.exists(project_save_dir):
                shutil.rmtree(project_save_dir)
            os.makedirs(project_save_dir)

            with PatchedZipFile(saved_zip, 'r') as project_zip:
                project_zip.extractall(project_save_dir)

            if os.path.exists(saved_zip):
                os.remove(saved_zip)

            snapper.main(project_save_dir)

            return redirect(url_for('main', project=project_name))
        else:
            print("Error in main: %s" % form.errors)
            #TODO(HD) tell the user about the issue
        return redirect(url_for('main'))
    other_vars["form"] = form

    if project is not None:
        session['project'] = project
        project_dir = os.path.join(PROJECTS_DIR, project)
        if os.path.isdir(project_dir):
            versions = sorted(os.listdir(project_dir))  #TODO(HD) sorted by git commit not by name
            session['versions'] = versions
            version = request.values.get("version") or session.get('current', None)
            session['version'] = version
            codefile = request.values.get("codefile") or session.get('codefile', None)
            session['codefile'] = codefile

            if version in versions:
                session['current'] = version
                index = versions.index(version)

                if codefile is not None:
                    try:
                        with open(os.path.join(PROJECTS_DIR, project, version, codefile), 'r') as cfile:
                            other_vars['code_file'] = cfile.read()
                    except FileNotFoundError:
                        pass

                try:
                    with open(os.path.join(PROJECTS_DIR, project, version, 'output.html'), 'r') as ofile:
                        other_vars['output_file'] = ofile.read()
                except FileNotFoundError:
                    pass
            else:
                index = 0
                session['current'] = versions[0]

            if index > 0:
                other_vars['prev_version'] = versions[index - 1]
            if index + 1 < len(versions):
                other_vars['next_version'] = versions[index + 1]

            other_vars['project_tree'] = consolidated_dirtree(project_dir)
    return render_template("index.html", **dict(session, **other_vars))

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  #TODO don't use this

    csrf = CSRFProtect()
    csrf.init_app(app)

    # app.run(debug=True)  #TODO remove debug
    ui.run()
