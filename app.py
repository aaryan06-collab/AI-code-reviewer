import os
from flask import Flask, render_template, request, jsonify
from reviewer import review_code

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB limit


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error": "Please upload a file."}), 400

    review_lang = request.form.get("review_lang", "English")

    try:
        code = file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({"error": "File must be a text/code file (not binary)."}), 400

    try:
        result = review_code(code, file.filename, review_lang)
        return jsonify({"review": result})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Review failed: {str(e)}"}), 500


if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set. Create a .env file with your API key.")
    app.run(debug=True)
