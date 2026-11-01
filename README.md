# AI-Powered Personal Knowledge Management & Note-Taking Assistant

A clean, local-first Python application that helps you manage personal notes, capture knowledge from Markdown and text files, and use AI to summarize content, generate tags, and answer questions based on your own local knowledge base.

## Features

- Recursively scans a local directory for notes and Markdown files
- Reads plain text and Markdown content from supported files
- Uses the OpenRouter API for AI-powered summarization and Q&A
- Generates concise topic tags for notes
- Allows interactive or scripted usage from a command-line interface
- Keeps a local-first workflow while augmenting it with AI assistance

## Project Structure

```text
.
├── ai_engine.py
├── file_scanner.py
├── main.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── notes/
```

## Requirements

- Python 3.10+
- An OpenRouter API key
- A local directory containing your notes (for example, `./notes`)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/solodevelopersai/local-ai-note-assistant.git
cd local-ai-note-assistant
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
```

Then edit `.env` and set your values:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
NOTES_DIRECTORY=./notes
APP_NAME=Local AI Note Assistant
APP_URL=https://github.com/solodevelopersai/local-ai-note-assistant
```

## OpenRouter API Setup

1. Sign up or log in to OpenRouter: https://openrouter.ai
2. Create an API key from your account dashboard
3. Make sure your key has access to a supported chat model such as:
   - `openai/gpt-4o-mini`
   - `anthropic/claude-3.5-sonnet`
   - `google/gemini-2.0-flash-exp`
4. Store the API key in `.env` or in your shell environment

## Usage

### 1. Prepare your notes folder

Create a folder such as:

```bash
mkdir -p notes
```

Add text or Markdown documents there, such as:

- `notes/project-notes.md`
- `notes/weekly-review.txt`
- `notes/ideas/meeting-notes.md`

### 2. Ask a question about your notes

```bash
python main.py --notes-dir ./notes --query "What are the key action items from my project notes?"
```

### 3. Summarize each document

```bash
python main.py --notes-dir ./notes --summarize
```

### 4. Generate tags for each document

```bash
python main.py --notes-dir ./notes --tags
```

### 5. Run interactive mode

```bash
python main.py --notes-dir ./notes --interactive
```

This starts a loop where you can ask questions about your notes conversationally.

## Example Workflow

```bash
mkdir -p notes
cat > notes/learning-notes.md <<'EOF'
# Learning Notes

## Python
- Built a small data processing project
- Used FastAPI to create a REST service
- Learned about dependency injection in web apps

## AI
- Explored prompt engineering patterns
- Compared summarization quality across models
- Enabled local note retrieval with AI assistance
EOF

python main.py --notes-dir ./notes --summarize
python main.py --notes-dir ./notes --tags
python main.py --notes-dir ./notes --query "What topics did I learn about in this note?"
```

## How It Works

- `file_scanner.py` walks the filesystem and collects supported text-like files
- `ai_engine.py` sends the relevant file content to OpenRouter for summarization, tagging, or Q&A
- `main.py` provides the CLI interface and orchestrates the workflow

## Security Notes

- Keep your `.env` file private and never commit it to version control
- Do not store sensitive personal information in plaintext if you do not want it sent to AI providers
- Review API usage and model behavior before relying on it for important knowledge management workflows

## License

This project is provided as a starter template and can be adapted for personal or commercial use.

## Next Enhancements

- Add a SQLite-backed note index
- Support searchable embeddings for semantic retrieval
- Build a web UI with Streamlit or Gradio
- Add note tagging persistence and database storage
- Integrate a local vector database for offline retrieval
