import os
import logging
from datetime import datetime
import time

from flask import Flask, render_template, request, url_for
from dotenv import load_dotenv

from utils.analysis import analyze_expenses, allowed_file

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(STATIC_FOLDER, "charts"), exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "expense-analyzer-dev")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


@app.before_request
def log_request_info():
    """Log incoming request details."""
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "api_version": "v1"
    }, 200


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    logger.warning(f"Bad request: {error}")
    return render_template(
        "error.html",
        error_code=400,
        error_message="Bad Request: Invalid request parameters."
    ), 400


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    logger.warning("File upload exceeded size limit")
    return render_template(
        "error.html",
        error_code=413,
        error_message="File too large. Maximum upload size is 16MB."
    ), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return render_template(
        "error.html",
        error_code=500,
        error_message="Internal Server Error. Please try again later."
    ), 500


@app.route("/", methods=["GET", "POST"])
def index():
    report = None
    error = None
    execution_time = None

    if request.method == "POST":
        start_time = time.time()
        uploaded_file = request.files.get("file")
        if not uploaded_file or uploaded_file.filename == "":
            error = "Please choose a CSV file to analyze."
            logger.warning("No file uploaded in request")
        elif not allowed_file(uploaded_file.filename):
            error = "Only CSV files are supported."
            logger.warning(f"Invalid file type uploaded: {uploaded_file.filename}")
        else:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            safe_name = f"expense_upload_{timestamp}.csv"
            upload_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            uploaded_file.save(upload_path)
            logger.info(f"File uploaded successfully: {safe_name}")
            try:
                report = analyze_expenses(upload_path, static_folder=STATIC_FOLDER)
                execution_time = round(time.time() - start_time, 2)
                logger.info(f"Analysis completed for {safe_name} in {execution_time}s")
            except Exception as exc:  # pragma: no cover - surfaced to UI
                error = f"Unable to analyze the file: {exc}"
                logger.error(f"Analysis failed for {safe_name}: {exc}", exc_info=True)

    return render_template(
        "index.html",
        report=report,
        error=error,
        execution_time=execution_time,
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