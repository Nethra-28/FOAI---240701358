from flask import Flask, render_template, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename

from ai_engine import screen_resumes


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/screen", methods=["POST"])
def screen():

    try:

        required_skills = request.form.get("required_skills", "")
        preferred_skills = request.form.get("preferred_skills", "")

        degree = request.form.get(
            "degree",
            "B.E/B.Tech CSE"
        )

        min_cgpa = float(
            request.form.get("min_cgpa", 0)
        )

        min_experience = float(
            request.form.get("min_experience", 0)
        )

        files = request.files.getlist("resumes")

        if not files or all(f.filename == "" for f in files):
            return jsonify({
                "error": "Please upload at least one resume."
            }), 400

        resume_items = []

        for file in files:

            if not file.filename:
                continue

            if not allowed_file(file.filename):

                return jsonify({
                    "error":
                    f"Unsupported file type: {file.filename}. "
                    "Use PDF, DOCX or TXT."
                }), 400

            safe_name = secure_filename(file.filename)

            path = UPLOAD_FOLDER / safe_name

            file.save(path)

            resume_items.append({
                "filename": safe_name,
                "path": str(path)
            })

        job = {

            "required_skills": required_skills,

            "preferred_skills": preferred_skills,

            "degree": degree,

            "min_cgpa": min_cgpa,

            "min_experience": min_experience
        }

        results = screen_resumes(
            resume_items,
            job
        )

        # Delete uploaded files after processing
        for item in resume_items:

            try:
                Path(item["path"]).unlink(
                    missing_ok=True
                )

            except Exception:
                pass

        return jsonify({

            "job": job,

            "results": results

        })

    except Exception as exc:

        return jsonify({
            "error": str(exc)
        }), 500


if __name__ == "__main__":

    app.run(
        debug=True
    )