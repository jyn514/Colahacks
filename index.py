#!/usr/bin/env python3
import os

from flask import Flask, render_template, app, request, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug import secure_filename

from snapper import SAVE_ROOT

app = Flask(__name__)


class FileUploadForm(FlaskForm):
    file = FileField()

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

    upload_dir = os.path.join(SAVE_ROOT, 'uploads')
    if not os.path.isdir(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    form = FileUploadForm(request.form)
    if request.method == 'POST' and form.validate():
        if form.validate_on_submit():
            filename = secure_filename(form.file.data.filename)
            form.file.data.save(os.path.join(upload_dir, 'uploads', filename))
            #TODO do more stuff with the file
    other_vars["form"] = form

    if project is not None:
        session['project'] = project
        project = os.path.join(SAVE_ROOT, project)
        if os.path.isdir(project):
            versions = sorted(os.listdir(project))
            session['versions'] = versions
            version = request.values.get("version") or session.get('current', None)

            if version is not None:
                session['current'] = version
                index = versions.index(version)
            else:
                session['current'], index = versions[0], 0

            if index > 0:
                other_vars['prev_version'] = versions[index - 1]
            if index + 1 < len(versions):
                other_vars['next_version'] = versions[index + 1]
    return render_template("index.html", **dict(session, **other_vars))

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'  #TODO don't use this
    app.run(debug=True)  #TODO remove debug
