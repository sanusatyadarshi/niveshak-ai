#!/usr/bin/env python3
"""
NiveshakAI Web Application
Simple Flask web interface for the NiveshakAI CLI functionality
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
import subprocess
import json
from datetime import datetime
import glob

# Try to import PDF conversion libraries
try:
    import markdown2
    from weasyprint import HTML, CSS
    from io import BytesIO
    PDF_CONVERSION_AVAILABLE = True
except ImportError:
    PDF_CONVERSION_AVAILABLE = False
    print("Warning: PDF conversion libraries not available. Install markdown2 and weasyprint for PDF support.")

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'data', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(project_root, 'data', 'annual_reports'), exist_ok=True)
os.makedirs(os.path.join(project_root, 'data', 'books'), exist_ok=True)

def convert_markdown_to_pdf(markdown_content, title="Report"):
    """Convert markdown content to PDF using weasyprint"""
    if not PDF_CONVERSION_AVAILABLE:
        raise ImportError("PDF conversion libraries not available. Please install markdown2 and weasyprint.")
    
    # Convert markdown to HTML
    html_content = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
    
    # Add basic CSS styling for better PDF appearance
    css_style = """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h1 {
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
        }
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .alert-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #666;
        }
        @page {
            margin: 2cm;
            @bottom-center {
                content: counter(page);
            }
        }
    </style>
    """
    
    # Combine CSS and HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert to PDF
    pdf_buffer = BytesIO()
    HTML(string=full_html).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer

@app.route('/')
def home():
    """Home page with overview of features"""
    return render_template('index.html')

@app.route('/analyze')
def analyze():
    """Analysis page with company analysis and Q&A forms"""
    return render_template('analyze.html')

@app.route('/upload')
def upload():
    """Upload page for annual reports and books"""
    return render_template('upload.html')

@app.route('/reports')
def reports():
    """Reports page showing generated analysis reports"""
    # Get all generated reports
    reports_dir = os.path.join(project_root, 'reports')
    report_files = []
    
    if os.path.exists(reports_dir):
        for file in glob.glob(os.path.join(reports_dir, '*.md')):
            file_stats = os.stat(file)
            report_files.append({
                'filename': os.path.basename(file),
                'filepath': file,
                'size': file_stats.st_size,
                'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by modification time, newest first
    report_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('reports.html', reports=report_files)

@app.route('/api/analyze/company', methods=['POST'])
def api_analyze_company():
    """API endpoint for company analysis"""
    try:
        data = request.get_json()
        company = data.get('company', '').strip().upper()
        query = data.get('query', '').strip()
        
        if not company:
            return jsonify({'error': 'Company symbol is required'}), 400
        
        # Build command with correct argument format
        cmd = ['python', 'main.py', 'analyze', 'company', '--company', company]
        if query:
            cmd.extend(['--query', query])
        
        # Execute the CLI command
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout,
                'company': company,
                'message': 'Analysis completed successfully',
                'analysis': result.stdout
            })
        else:
            error_output = result.stderr
            if "OpenAI API key not found" in error_output:
                return jsonify({
                    'error': 'AI Analysis Configuration Required',
                    'message': 'OpenAI API key required for PDF analysis',
                    'details': 'Please configure OPENAI_API_KEY in .env file to analyze uploaded annual reports',
                    'setup_instructions': [
                        'Get API key from: https://platform.openai.com/api-keys',
                        'Copy .env.template to .env',
                        'Add OPENAI_API_KEY=your_key_here to .env',
                        'Restart the application'
                    ]
                }), 400
            else:
                return jsonify({
                    'error': f'Analysis failed: {error_output}',
                    'output': result.stdout
                }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/analyze/ask', methods=['POST'])
def api_analyze_ask():
    """API endpoint for investment questions"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Question is required'}), 400
        
        # Execute the CLI command
        cmd = ['python', 'main.py', 'analyze', 'ask', '--query', query]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout,
                'query': query,
                'message': 'Question answered successfully',
                'answer': result.stdout
            })
        else:
            return jsonify({
                'error': f'Query failed: {result.stderr}',
                'output': result.stdout
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/upload/annual-report', methods=['POST'])
def api_upload_annual_report():
    """API endpoint for uploading annual reports"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        company = request.form.get('company', '').strip().upper()
        year = request.form.get('year', '').strip()
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if not company:
            return jsonify({'error': 'Company symbol is required'}), 400
        
        if not year:
            return jsonify({'error': 'Year is required'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            # Create company directory
            company_dir = os.path.join(project_root, 'data', 'annual_reports', company)
            os.makedirs(company_dir, exist_ok=True)
            
            # Save file with year as filename
            filename = f"{year}.pdf"
            filepath = os.path.join(company_dir, filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'message': f'Annual report for {company} ({year}) uploaded successfully',
                'filepath': f'data/annual_reports/{company}/{filename}',
                'needsIngestion': True,
                'company': company,
                'year': year
            })
        else:
            return jsonify({'error': 'Only PDF files are allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/ingest/annual-report', methods=['POST'])
def api_ingest_annual_report():
    """API endpoint for ingesting uploaded annual reports into vector database"""
    try:
        data = request.get_json()
        company = data.get('company', '').strip().upper()
        year = data.get('year', '').strip()
        filepath = data.get('filepath', '').strip()
        
        if not company:
            return jsonify({'error': 'Company symbol is required'}), 400
        
        if not year:
            return jsonify({'error': 'Year is required'}), 400
        
        if not filepath:
            return jsonify({'error': 'File path is required'}), 400
        
        # Build the full file path
        full_filepath = os.path.join(project_root, filepath)
        
        if not os.path.exists(full_filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Run ingestion command with correct argument format
        cmd = [
            'python', 'main.py', 'ingest', 'reports', 
            '--file', full_filepath,
            '--company', company,
            '--year', year
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': f'Annual report for {company} ({year}) ingested successfully',
                'output': result.stdout,
                'company': company,
                'year': year
            })
        else:
            return jsonify({
                'error': f'Ingestion failed: {result.stderr}',
                'output': result.stdout
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Ingestion failed: {str(e)}'}), 500

@app.route('/api/upload/book', methods=['POST'])
def api_upload_book():
    """API endpoint for uploading investment books"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(project_root, 'data', 'books', filename)
            file.save(filepath)
            
            # Run ingestion command with correct argument format
            cmd = ['python', 'main.py', 'ingest', 'books', '--file', filepath]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': f'Book "{filename}" uploaded and processed successfully',
                    'output': result.stdout
                })
            else:
                return jsonify({
                    'error': f'Book processing failed: {result.stderr}',
                    'output': result.stdout
                }), 500
        else:
            return jsonify({'error': 'Only PDF files are allowed'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/reports/<filename>')
def api_download_report(filename):
    """Download a specific report file"""
    try:
        reports_dir = os.path.join(project_root, 'reports')
        filepath = os.path.join(reports_dir, filename)
        
        if os.path.exists(filepath) and filename.endswith('.md'):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/reports/<filename>/view')
def api_view_report(filename):
    """View a specific report file content"""
    try:
        reports_dir = os.path.join(project_root, 'reports')
        filepath = os.path.join(reports_dir, filename)
        
        if os.path.exists(filepath) and filename.endswith('.md'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'filename': filename,
                'content': content
            })
        else:
            return jsonify({'error': 'Report not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to read report: {str(e)}'}), 500

@app.route('/api/reports/<filename>/download-pdf')
def api_download_report_as_pdf(filename):
    """Convert and download a markdown report as PDF"""
    try:
        if not PDF_CONVERSION_AVAILABLE:
            return jsonify({'error': 'PDF conversion not available. Please ensure markdown2 and weasyprint are installed.'}), 500
        
        reports_dir = os.path.join(project_root, 'reports')
        filepath = os.path.join(reports_dir, filename)
        
        if not (os.path.exists(filepath) and filename.endswith('.md')):
            return jsonify({'error': 'Report not found'}), 404
        
        # Read the markdown content
        with open(filepath, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Extract company name from filename for title
        title = filename.replace('.md', '').replace('-', ' ').title()
        
        # Convert to PDF
        pdf_buffer = convert_markdown_to_pdf(markdown_content, title)
        
        # Create PDF filename
        pdf_filename = filename.replace('.md', '.pdf')
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF conversion failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting NiveshakAI Web Application...")
    print("Available at: http://localhost:5000")
    print("\nFeatures:")
    print("- Stock Analysis: http://localhost:5000/analyze")
    print("- File Upload: http://localhost:5000/upload")
    print("- View Reports: http://localhost:5000/reports")
    
    # Determine if running in Docker
    import os
    is_docker = os.path.exists('/.dockerenv')
    
    if is_docker:
        print("\n🐳 Running in Docker container")
        # In Docker, bind to all interfaces
        app.run(debug=False, host='0.0.0.0', port=5000)
    else:
        print("\n💻 Running locally")
        app.run(debug=True, host='0.0.0.0', port=5000)
