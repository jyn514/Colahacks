from flask import Flask, render_template, app, request, session
app = Flask(__name__)

@app.route("/", methods = ['GET', 'POST'])
def main():
    # if "clear" in request.args:
    #     session.clear()
    # project = request.values.get("project")
    # if project is not None:
    #     session["project"] = project
    # slide = request.values.get("slide")
    # if slide is not None:
    #     session["slide"] = slide

    return render_template("index.html", **session)

if __name__ == "__main__":
    app.secret_key = 'TODO: A0Zr98j/3yX R~XHH!jmN]LWX/,?RT' #TODO don't use this
    app.run(debug=True)
