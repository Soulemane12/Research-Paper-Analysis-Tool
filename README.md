# Research Paper Analysis Tool

A Flask-based web application that analyzes research papers, extracts key insights, and visualizes relationships between claims and evidence using an interactive discourse graph.

## Features

- PDF research paper upload and analysis
- Automatic extraction of:
  - Research questions
  - Key claims
  - Supporting evidence
  - Contextual information
- Cross-referencing of claims across papers
- Interactive discourse graph visualization
- Automatic session and data cleanup between uploads

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd research-paper-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Julep API key:
```
JULEP_API_KEY=your_api_key_here
```

5. Create required directories:
```bash
mkdir -p uploads insights
touch uploads/.gitkeep insights/.gitkeep
```

## Project Structure

```
research-paper-analysis/
├── app.py                  # Main Flask application
├── julep_task.py          # Paper analysis logic
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
├── requirements.txt       # Python dependencies
├── static/
│   ├── js/
│   │   └── discourse-graph.js  # Graph visualization
│   └── styles.css        # Application styles
├── templates/
│   └── index.html        # Main page template
├── uploads/              # Temporary PDF storage
└── insights/             # Analysis results storage
    └── processed_results.json
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open a web browser and navigate to `http://localhost:5000`

3. Upload PDF research papers using the file input

4. View the analysis results, including:
   - Extracted claims and evidence
   - Cross-referenced claims
   - Interactive discourse graph

## Development

- The application automatically clears previous results and uploaded files between sessions
- Session data is stored in `insights/processed_results.json`
- Uploaded PDFs are temporarily stored in the `uploads/` directory

## Environment Variables

Create a `.env` file with the following variables:
```
JULEP_API_KEY=your_api_key_here
```

## Dependencies

- Flask
- PyMuPDF (fitz)
- python-dotenv
- Julep API
- D3.js (included via CDN)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]
