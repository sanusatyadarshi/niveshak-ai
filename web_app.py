#!/usr/bin/env python3
"""
NiveshakAI Web Interface

Simple web interface replicating CLI functionality.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import markdown

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.utils import NiveshakLogger, logger

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure upload folder
UPLOAD_FOLDER = Path('data/annual_reports')
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with navigation."""
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    """Stock analysis page."""
    return render_template('analyze.html')

@app.route('/api/analyze/company', methods=['POST'])
def api_analyze_company():
    """API endpoint for company analysis."""
    try:
        data = request.get_json()
        company = data.get('company', '').strip().upper()
        query = data.get('query', '')
        
        if not company:
            return jsonify({'error': 'Company symbol is required'}), 400
        
        # Import and run analysis
        from src.cli.analyze import handle_company_analysis
        
        # Create temporary args object
        class Args:
            def __init__(self):
                self.company = company
                self.query = query if query else f"Analyze {company} fundamentally"
                self.valuation = 'dcf'
                self.output = None
                self.config = 'config/settings.yaml'
        
        args = Args()
        result = handle_company_analysis(args)
        
        return jsonify({
            'success': True,
            'company': company,
            'analysis': result,
            'message': f'Analysis completed for {company}'
        })
        
    except Exception as e:
        logger.error(f"Company analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/analyze/ask', methods=['POST'])
def api_analyze_ask():
    """API endpoint for investment questions."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Question is required'}), 400
        
        # Import and run knowledge query
        from src.cli.analyze import handle_ask_query
        
        # Create temporary args object
        class Args:
            def __init__(self):
                self.query = query
                self.config = 'config/settings.yaml'
        
        args = Args()
        result = handle_ask_query(args)
        
        return jsonify({
            'success': True,
            'query': query,
            'answer': result,
            'message': 'Question answered successfully'
        })
        
    except Exception as e:
        logger.error(f"Ask query error: {str(e)}")
        return jsonify({'error': f'Query failed: {str(e)}'}), 500

@app.route('/upload')
def upload():
    """File upload page."""
    return render_template('upload.html')

@app.route('/api/upload/report', methods=['POST'])
def api_upload_report():
    """API endpoint for uploading annual reports."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        company = request.form.get('company', '').strip().upper()
        year = request.form.get('year', '').strip()
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not company:
            return jsonify({'error': 'Company symbol is required'}), 400
        
        if not year:
            return jsonify({'error': 'Year is required'}), 400
        
        if file and allowed_file(file.filename):
            # Create company directory
            company_dir = UPLOAD_FOLDER / company
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file with year as filename
            filename = f"{year}.pdf"
            filepath = company_dir / filename
            file.save(str(filepath))
            
            return jsonify({
                'success': True,
                'message': f'Report uploaded successfully for {company} ({year})',
                'company': company,
                'year': year,
                'filepath': str(filepath)
            })
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/upload/book', methods=['POST'])
def api_upload_book():
    """API endpoint for uploading investment books."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save to books directory
            books_dir = Path('data/books')
            books_dir.mkdir(parents=True, exist_ok=True)
            
            filename = secure_filename(file.filename)
            filepath = books_dir / filename
            file.save(str(filepath))
            
            # Import and process book
            from src.cli.ingest_books import process_single_book
            
            try:
                result = process_single_book(str(filepath))
                return jsonify({
                    'success': True,
                    'message': f'Book uploaded and processed successfully: {filename}',
                    'filename': filename,
                    'result': result
                })
            except Exception as process_error:
                return jsonify({
                    'success': True,
                    'message': f'Book uploaded successfully: {filename}. Processing will happen in background.',
                    'filename': filename,
                    'note': 'Use "Ingest Books" to process the uploaded file.'
                })
        else:
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
            
    except Exception as e:
        logger.error(f"Book upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/ingest/books', methods=['POST'])
def api_ingest_books():
    """API endpoint for ingesting books."""
    try:
        from src.cli.ingest_books import ingest_books_from_directory
        
        books_dir = Path('data/books')
        if not books_dir.exists():
            return jsonify({'error': 'No books directory found'}), 400
        
        result = ingest_books_from_directory(str(books_dir))
        
        return jsonify({
            'success': True,
            'message': 'Books ingestion completed',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Books ingestion error: {str(e)}")
        return jsonify({'error': f'Ingestion failed: {str(e)}'}), 500

@app.route('/reports')
def reports():
    """View generated reports."""
    reports_dir = Path('reports')
    report_files = []
    
    if reports_dir.exists():
        for file in reports_dir.glob('*.md'):
            report_files.append({
                'name': file.name,
                'path': str(file),
                'size': file.stat().st_size,
                'modified': file.stat().st_mtime
            })
    
    return render_template('reports.html', reports=report_files)

@app.route('/view_report/<filename>')
def view_report(filename):
    """View a specific report."""
    try:
        report_path = Path('reports') / secure_filename(filename)
        if not report_path.exists():
            flash('Report not found', 'error')
            return redirect(url_for('reports'))
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        
        return render_template('view_report.html', 
                             filename=filename, 
                             content=html_content,
                             raw_content=content)
    
    except Exception as e:
        flash(f'Error viewing report: {str(e)}', 'error')
        return redirect(url_for('reports'))

@app.route('/download_report/<filename>')
def download_report(filename):
    """Download a report file."""
    try:
        report_path = Path('reports') / secure_filename(filename)
        if not report_path.exists():
            flash('Report not found', 'error')
            return redirect(url_for('reports'))
        
        return send_file(report_path, as_attachment=True)
    
    except Exception as e:
        flash(f'Error downloading report: {str(e)}', 'error')
        return redirect(url_for('reports'))

if __name__ == '__main__':
    # Setup logging
    try:
        NiveshakLogger.setup_logging()
        logger.info("Starting NiveshakAI Web Interface...")
    except Exception as e:
        print(f"Warning: Could not setup logging: {e}")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
