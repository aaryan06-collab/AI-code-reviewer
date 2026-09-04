import os
from flask import Flask, render_template, request, jsonify
from reviewer import review_code

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB limit


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/review", methods=["POST"])
def review():
    review_lang = request.form.get("review_lang", "English") if request.form else "English"

    # Handle JSON body (pasted code)
    if request.is_json:
        data = request.get_json()
        code = data.get("code", "")
        filename = data.get("filename", "untitled.py")
        review_lang = data.get("review_lang", "English")
        if not code.strip():
            return jsonify({"error": "Please provide code to review."}), 400
    else:
        # Handle file upload
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify({"error": "Please upload a file or paste code."}), 400
        filename = file.filename
        try:
            code = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"error": "File must be a text/code file (not binary)."}), 400

    try:
        result = review_code(code, filename, review_lang)
        return jsonify({"review": result})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Review failed: {str(e)}"}), 500


if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("Warning: GROQ_API_KEY not set. Create a .env file with your API key.")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
