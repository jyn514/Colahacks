import os

from flask import Flask, render_template, app, request, session

app = Flask(__name__)
SNAP_DIR = 'snaps'

@app.route("/", methods = ['GET', 'POST'])
def main():
    if "clear" in request.args:
        session.clear()

    project = request.values.get("project")
    if project is not None:
        session['project'] = project
        project = os.path.join(SNAP_DIR, project)
        if os.path.isdir(project):
            files = sorted(os.listdir(project))
            session['files'] = files
            slide = request.values.get("slide")

            if slide is not None:
                session['slide'] = slide
                index = files.index(slide)
            else:
                session['slide'], index = files[0], 0

            if index > 0:
                session['prev_slide'] = files[index - 1]
            if index + 1 < len(files):
                session['next_slide'] = files[index + 1]
    return render_template("index.html", **session)

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #TODO don't use this
    app.run(debug=True)
