# Mini RAG Telegram Bot (Option A)

## Project Metadata

- **Author:** Naveen Kumar  
- **Date:** 31-01-2026  
- **License:** Educational / Learning Use  


## Overview
This project implements a **Mini Retrieval-Augmented Generation (RAG)** system exposed through a **Telegram Bot**.  
The bot answers user questions by retrieving relevant information from a small local document set and generating grounded responses using a **local Large Language Model (LLM)**.

The entire system runs **locally using Docker**, with no external APIs or paid services.


## Features
- Telegram bot interface
- `/ask` command for knowledge-based queries
- Local document ingestion and chunking
- Vector similarity search using SQLite + `sqlite-vec`
- Local embeddings using `sentence-transformers`
- Local LLM inference using **Qwen 2.5 7B Instruct** via Ollama
- Fully Dockerized using Docker Compose


## Architecture
Documents → Chunking → Embeddings → SQLite Vector DB → Retrieval → LLM Answer


## Models Used

### Embedding Model
- **Model:** all-MiniLM-L6-v2  
- **Reason:** Lightweight, fast, and suitable for semantic retrieval on small document collections.

### Language Model
- **Model:** Qwen 2.5 7B Instruct  
- **Runtime:** Ollama (local)  
- **Reason:** Strong instruction-following, low hallucination, and fully offline.


## Setup & Run (Docker)

### Prerequisites
- Docker
- Docker Compose
- Telegram Bot Token

###
```
mini-rag-bot/
├── .venv/
├── data_docs/
│   ├── faq.md
│   ├── policy.md
│   └── product.md
├── db/
│   └── rag.db
├── rag/
│   ├── __pycache__/
│   ├── ingest.py
│   ├── llm.py
│   ├── prompts.py
│   └── retrieve.py
├── app.py
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt

```
### Step 1: Clone Repository & Add Knowledge Documents
git clone https://github.com/SaraswathiAnalytics/mini-rag-bot.git
cd mini-rag-bot

Place **3–5 short `.md` or `.txt` files** inside `data/docs/`:

Example content:
- Company policies
- FAQs
- Product documentation

### Step 2: Configure Environment Variables

**Do NOT hard-code your Telegram Bot token.**

Create a `.env` file in the project root:

```env
 - BOT_TOKEN=your_telegram_bot_token_here
```

### Step 3: Start Ollama & Pull Model
```bash
# Start Ollama and Pull the LLM model:
docker compose up ollama -d
docker exec -it ollama ollama pull qwen2.5:7b-instruct

# Ingest Documents
docker compose run --rm rag-bot python rag/ingest.py
# Start the Bot
docker compose up --build -d
```


## Usage
Open Telegram application/web app & search for your bot username

### Commands
- /start              Start the bot
- /help               Show usage instructions
- /ask <question>     Ask questions from documents
- /summarize          Summarize last 3 interactions


### Examles
- /ask What is the refund policy?
- /ask How long does shipping take?
- /ask What user roles are supported?


