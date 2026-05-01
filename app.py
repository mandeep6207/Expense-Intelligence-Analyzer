import os
from datetime import datetime

from flask import Flask, render_template, request, url_for

from utils.analysis import analyze_expenses, allowed_file


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(STATIC_FOLDER, "charts"), exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "expense-analyzer-dev")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or uploaded_file.filename == "":
            error = "Please choose a CSV file to analyze."
        elif not allowed_file(uploaded_file.filename):
            error = "Only CSV files are supported."
        else:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            safe_name = f"expense_upload_{timestamp}.csv"
            upload_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            uploaded_file.save(upload_path)
            try:
                report = analyze_expenses(upload_path, static_folder=STATIC_FOLDER)
            except Exception as exc:  # pragma: no cover - surfaced to UI
                error = f"Unable to analyze the file: {exc}"

    return render_template(
        "index.html",
        report=report,
        error=error,
        chart_base=url_for("static", filename="charts"),
    )


@app.errorhandler(413)
def file_too_large(_):
    return (
        render_template(
            "index.html",
            report=None,
            error="File is too large.",
            chart_base=url_for("static", filename="charts"),
        ),
        413,
    )


if __name__ == "__main__":
    app.run(debug=True)