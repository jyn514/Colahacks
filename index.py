#!/usr/bin/env python
import os

from flask import Flask, render_template, app, request, session

from snapper import SAVE_ROOT

app = Flask(__name__)


@app.route("/", methods = ['GET', 'POST'])
def main():
    if "clear" in request.args:
        session.clear()

    session['dirs'] = os.listdir(SAVE_ROOT)
    session['SAVE_ROOT'] = SAVE_ROOT

    project = request.values.get("project") or session.get('project', None)

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
                session['prev_version'] = versions[index - 1]
            if index + 1 < len(versions):
                session['next_version'] = versions[index + 1]
    return render_template("index.html", **session)

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #TODO don't use this
    app.run(debug=True)
