import os
import json
import fitz  # PyMuPDF for PDF parsing
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from julep_task import process_with_julep, cross_reference_claims, analyze_discourse_relationships
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = './insights/uploads'
PROCESSED_RESULTS = './insights/processed_results.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Clear existing results and uploads before processing new files
        clear_previous_data()
        
        print("Form submitted: Processing uploaded files...")
        files = request.files.getlist('files')
        results = []

        for file in files:
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                print(f"Saving file: {filename}")
                file.save(filepath)

                # Extract text from PDF
                print(f"Extracting text from: {filename}")
                paper_text = extract_text_from_pdf(filepath)
                if paper_text:
                    print(f"Text extracted from {filename}. Sending to Julep for processing...")
                    
                    # Process with Julep AI
                    result = process_with_julep(paper_text)
                    if isinstance(result, dict):
                        result['filename'] = filename
                        results.append(result)
                        print(f"Processing completed for {filename}: {result}")
                    else:
                        print(f"Error processing {filename}: {result}")
                else:
                    print(f"Failed to extract text from {filename}. Skipping.")
            else:
                print(f"Invalid file or non-PDF uploaded: {file.filename}")

        # Save results to JSON
        print("Saving results to JSON file...")
        save_results(results)

    # Load and display results
    processed_data = load_results()
    print(f"Loaded {len(processed_data)} results from JSON file.")

    # Cross-reference claims and evidence
    cross_references = cross_reference_claims(processed_data)

    return render_template('index.html', results=processed_data, cross_references=cross_references, count=len(processed_data))

@app.route('/discourse-graph')
def get_discourse_graph():
    results = load_results()
    graph_data = analyze_discourse_relationships(results)
    return jsonify(graph_data)

def extract_text_from_pdf(filepath):
    """Extracts text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        print(f"Extracted {len(text)} characters of text from {filepath}")
        return text
    except Exception as e:
        print(f"Error extracting text from {filepath}: {e}")
        return ""

def save_results(results):
    """Save processed results to JSON file."""
    if not os.path.exists(PROCESSED_RESULTS):
        print("Initializing processed_results.json...")
        with open(PROCESSED_RESULTS, 'w') as f:
            json.dump([], f)

    try:
        with open(PROCESSED_RESULTS, 'r') as f:
            existing_results = json.load(f)
            print(f"Loaded existing results: {len(existing_results)} entries.")
    except (json.JSONDecodeError, ValueError):
        print("Invalid JSON in processed_results.json. Starting fresh.")
        existing_results = []

    existing_results.extend(results)
    with open(PROCESSED_RESULTS, 'w') as f:
        json.dump(existing_results, f, indent=4)
        print(f"Saved {len(existing_results)} total results.")

def load_results():
    """Load processed results from JSON file, return an empty list if the file is missing or invalid."""
    if not os.path.exists(PROCESSED_RESULTS):
        print("No processed_results.json found. Returning empty list.")
        return []
    
    try:
        with open(PROCESSED_RESULTS, 'r') as f:
            results = json.load(f)
            print(f"Loaded {len(results)} entries from processed_results.json.")
            return results
    except (json.JSONDecodeError, ValueError):
        print("Invalid JSON in processed_results.json. Returning empty list.")
        return []

def clear_previous_data():
    """Clear all previous results and uploaded files"""
    print("Clearing previous data...")
    
    # Clear processed_results.json
    try:
        with open(PROCESSED_RESULTS, 'w') as f:
            json.dump([], f)
        print("Cleared processed_results.json")
    except Exception as e:
        print(f"Error clearing processed_results.json: {e}")

    # Clear uploads directory
    try:
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        print("Cleared uploads directory")
    except Exception as e:
        print(f"Error clearing uploads directory: {e}")

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
