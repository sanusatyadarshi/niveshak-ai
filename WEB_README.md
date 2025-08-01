# NiveshakAI Web Interface

A simple web interface for the NiveshakAI investment analysis tool that replicates all CLI functionality through an easy-to-use web browser interface.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Flask and other web dependencies
pip install flask werkzeug

# Or install all requirements
pip install -r requirements.txt
```

### 2. Set Up Environment

Make sure you have your `.env` file with OpenAI API key:

```bash
echo 'OPENAI_API_KEY=your_api_key_here' > .env
```

### 3. Run the Web Application

```bash
# Option 1: Use the startup script (recommended)
./run_web.sh

# Option 2: Run directly
python app.py
```

### 4. Access the Web Interface

Open your browser and go to: **http://localhost:5000**

## 📊 Web Interface Features

### 🏠 Home Page (`/`)

- Overview of all features
- Quick start guide
- Current capabilities summary

### 🔍 Analysis Page (`/analyze`)

- **Company Analysis**: Enter stock symbol (e.g., ITC, ASIANPAINT) for comprehensive analysis
- **Investment Q&A**: Ask questions about investment strategies and get AI-powered answers

### 📁 Upload Page (`/upload`)

- **Annual Reports**: Upload company PDF annual reports organized by symbol and year
- **Investment Books**: Upload PDF books to enhance the knowledge base

### 📊 Reports Page (`/reports`)

- View all generated analysis reports
- Download reports as Markdown files
- Quick preview of report contents

## 🔄 How It Works

The web interface is a simple Flask application that:

1. **Replicates CLI Commands**: Each web form calls the equivalent CLI command
2. **File Management**: Handles PDF uploads for annual reports and books
3. **Report Display**: Shows generated analysis reports in a user-friendly format
4. **Real-time Feedback**: Provides loading indicators and error handling

### API Endpoints

- `POST /api/analyze/company` - Company analysis (equivalent to `python main.py analyze company`)
- `POST /api/analyze/ask` - Investment questions (equivalent to `python main.py analyze ask`)
- `POST /api/upload/annual-report` - Upload annual reports
- `POST /api/upload/book` - Upload and process investment books (equivalent to `python main.py ingest books`)
- `GET /api/reports/<filename>` - Download report files
- `GET /api/reports/<filename>/view` - View report content

## 📁 File Organization

```
niveshak-ai/
├── app.py                 # Flask web application
├── run_web.sh            # Startup script
├── templates/            # HTML templates
│   ├── base.html         # Base template with CSS/JS
│   ├── index.html        # Home page
│   ├── analyze.html      # Analysis forms
│   ├── upload.html       # File upload forms
│   └── reports.html      # Reports listing
├── data/
│   ├── annual_reports/   # Uploaded annual reports
│   ├── books/           # Uploaded investment books
│   └── uploads/         # Temporary upload folder
└── reports/             # Generated analysis reports
```

## 🎯 Key Benefits

1. **Same Functionality**: All CLI features available through web interface
2. **User-Friendly**: No command line knowledge required
3. **File Management**: Easy drag-and-drop file uploads
4. **Visual Feedback**: Loading indicators and progress updates
5. **Report Access**: Easy viewing and downloading of generated reports
6. **Mobile Friendly**: Responsive design works on phones and tablets

## 🔧 Technical Details

- **Framework**: Flask 3.0+ (Python web framework)
- **Frontend**: Vanilla HTML/CSS/JavaScript (no complex frameworks)
- **File Handling**: Werkzeug for secure file uploads
- **CLI Integration**: Subprocess calls to existing CLI commands
- **Styling**: Clean, professional CSS with responsive design

## 🛠️ Development

The web interface is designed to be simple and maintainable:

- **Backend**: Single `app.py` file with all routes
- **Templates**: Jinja2 templates extending a base template
- **Styling**: Embedded CSS in base template (no external dependencies)
- **JavaScript**: Vanilla JS for form handling and AJAX calls

## 📝 Usage Examples

### Upload Annual Report

1. Go to Upload page
2. Enter company symbol (e.g., "ITC")
3. Enter year (e.g., "2024")
4. Select PDF file
5. Click "Upload Annual Report"

### Analyze Company

1. Go to Analyze page
2. Enter company symbol (e.g., "ITC")
3. Optionally add specific question
4. Click "Analyze Company"
5. Wait for analysis to complete
6. View results on page

### Ask Investment Question

1. Go to Analyze page
2. Enter your question in the Q&A section
3. Click "Ask Question"
4. Get AI-powered answer from knowledge base

## 🚧 Future Enhancements

- Better markdown rendering for reports
- Progress bars for long-running analyses
- Report comparison features
- Search functionality for reports
- Export reports to PDF format

---

This web interface provides the same powerful analysis capabilities as the CLI tool but with an intuitive, user-friendly interface that anyone can use.
