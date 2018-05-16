#!/usr/bin/env python3
import os
import shutil
from zipfile import ZipFile, ZipInfo

from flask import Flask, render_template, app, request, session, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug import secure_filename

import snapper
from snapper import SAVE_ROOT

UPLOADS_DIR = os.path.join(SAVE_ROOT, 'uploads')
PROJECTS_DIR = SAVE_ROOT  # os.path.join(SAVE_ROOT, 'projects')  # TODO(HD) projects probably should be kept in a subdirectory

app = Flask(__name__)


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

@app.route("/", methods = ['GET', 'POST'])
def main():
    other_vars = dict()
    if "clear" in request.args:
        session.clear()

    if not os.path.isdir(SAVE_ROOT):
        os.makedirs(SAVE_ROOT, exist_ok=True)
    other_vars['dirs'] = os.listdir(SAVE_ROOT)
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

            snapper.main(project_save_dir)  #TODO make this actually work

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
            versions = sorted(os.listdir(project_dir))
            session['versions'] = versions
            version = request.values.get("version") or session.get('current', None)

            if version in versions:
                session['current'] = version
                index = versions.index(version)

                with open(os.path.join(PROJECTS_DIR, project, version, 'output.html'), 'r') as ofile:
                    other_vars['output_file'] = ofile.read()
            else:
                index = 0
                session['current'] = versions[0]

            if index > 0:
                other_vars['prev_version'] = versions[index - 1]
            if index + 1 < len(versions):
                other_vars['next_version'] = versions[index + 1]
    return render_template("index.html", **dict(session, **other_vars))

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  #TODO don't use this

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.run(debug=True)  #TODO remove debug
