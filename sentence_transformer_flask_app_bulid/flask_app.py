# flask_app.py
from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from model_handling import UniversalResumeAnalyzer

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'uploads/resumes'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

analyzer = UniversalResumeAnalyzer()
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    job_description = request.form.get('job_description', '').strip()
    files = request.files.getlist('resumes')

    if not job_description:
        return jsonify({"error": "Job description is required"}), 400
    if len(files) == 0:
        return jsonify({"error": "At least one resume is required"}), 400
    if len(files) > 1000:
        return jsonify({"error": "Maximum 1,000 resumes allowed"}), 400

    file_data = []
    filenames = []
    for file in files:
        if file and allowed_file(file.filename):
            content = file.read()
            file_data.append((content, file.content_type))
            filenames.append(file.filename)

    try:
        results = analyzer.batch_analyze(file_data, job_description)
        df = pd.DataFrame(results)
        # df = df[df.get("Error") != "Failed to extract text"].reset_index(drop=True)
        df = df[df.apply(lambda row: row.get("Error") != "Failed to extract text", axis=1)]
        df["Resume Name"] = filenames[:len(df)]
        df = df[["Resume Name", "Overall Match Score", "Keywords Matched", "Semantic Relevance", "Summary"]]
        df = df.sort_values("Overall Match Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index.map(lambda x: f"{x+1}{'st' if x==0 else 'nd' if x==1 else 'rd' if x==2 else 'th'}")
        return jsonify({"success": True, "results": df.to_dict("records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)