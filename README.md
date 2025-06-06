# NiveshakAI

> Your Personal AI Fundamental Investing Assistant

---

## Overview

**NiveshakAI** is a personal AI agent designed to help you become a smarter, data-driven fundamental investor.  
It reads and understands your chosen investing books, analyzes company annual reports, and provides buy/sell recommendations along with detailed explanations — all shaped by your personalized investor philosophy.

Inspired by classic investing wisdom and powered by modern LLMs and vector search, NiveshakAI is your intelligent investing companion.

---

## Features

- 📚 Ingest investing books from any market (e.g. Warrent Buffet, Philip Fisher)
- 📄 Parse and analyze company annual reports from multiple markets
- 🧠 Embed your investor persona and risk profile for tailored recommendations
- 📊 Perform fundamental valuations like Discounted Cash Flow (DCF) and P/E ratio
- 🤖 Answer your queries with transparent explanations and data-backed reasoning
- 🛠️ CLI interface for easy interaction, with future plans for web UI

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager
- [Qdrant](https://qdrant.tech/) or [Weaviate](https://weaviate.io/) vector database running locally or remotely
- OpenAI API key or compatible LLM provider

### Installation

```bash
git clone https://github.com/<your-github-username>/NiveshakAI.git
cd NiveshakAI
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```
