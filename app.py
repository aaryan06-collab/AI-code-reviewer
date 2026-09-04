import os
import logging
from flask import Flask, render_template, request, jsonify
from reviewer import review_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB limit


@app.route("/health")
def health():
    has_key = bool(os.getenv("GROQ_API_KEY"))
    return jsonify({"status": "ok", "groq_key_set": has_key})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review():
    try:
        logger.info("Review request received")
        review_lang = request.form.get("review_lang", "English") if request.form else "English"

        # Handle JSON body (pasted code)
        if request.is_json:
            data = request.get_json()
            code = data.get("code", "")
            filename = data.get("filename", "untitled.py")
            review_lang = data.get("review_lang", "English")
            logger.info(f"JSON request: filename={filename}, code_length={len(code)}")
            if not code.strip():
                return jsonify({"error": "Please provide code to review."}), 400
        else:
            # Handle file upload
            file = request.files.get("file")
            if not file or not file.filename:
                return jsonify({"error": "Please upload a file or paste code."}), 400
            filename = file.filename
            logger.info(f"File upload: filename={filename}")
            try:
                code = file.read().decode("utf-8")
            except UnicodeDecodeError:
                return jsonify({"error": "File must be a text/code file (not binary)."}), 400

        result = review_code(code, filename, review_lang)
        logger.info("Review completed successfully")
        return jsonify({"review": result})
    except RuntimeError as e:
        logger.error(f"RuntimeError: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.exception("Unexpected error during review")
        return jsonify({"error": f"Review failed: {str(e)}"}), 500


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not set. Create a .env file with your API key.")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
