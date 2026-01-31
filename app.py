import os
from dotenv import load_dotenv
load_dotenv()
import logging
from collections import defaultdict, deque
from typing import Deque, Dict

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from rag.retrieve import retrieve
from rag.llm import generate
from rag.prompts import build_prompt, build_summary_prompt

# ---------------------------------------------------------------------
# Config & Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("mini-rag-bot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
# BOT_TOKEN = ""
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env variable not set")

# ---------------------------------------------------------------------
# In-Memory Chat History (last 3 Q&A per user)
# ---------------------------------------------------------------------

ChatHistory = Dict[int, Deque[dict]]
CHAT_MEMORY: ChatHistory = defaultdict(lambda: deque(maxlen=3))

# ---------------------------------------------------------------------
# Command Handlers
# ---------------------------------------------------------------------

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "there"

    await update.message.reply_text(
        f"Hello *{name}*!\n\n"
        "I’m a **Mini RAG Bot** 🤖\n\n"
        "*Available commands:*\n"
        "• `/ask <question>` – Ask questions from documents\n"
        "• `/summarize` – Summarize last 3 interactions\n"
        "• `/help` – Show usage instructions",
        parse_mode="Markdown",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*How to use this bot*\n\n"
        "• `/ask <question>` – Query the knowledge base\n"
        "• `/summarize` – Get a summary of your last 3 questions",
        parse_mode="Markdown",
    )


async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args).strip()
    if not question:
        await update.message.reply_text("Please provide a question.")
        return

    user_id = update.effective_user.id

    try:
        logger.info("User %s asked: %s", user_id, question)

        context_text = retrieve(question)
        prompt = build_prompt(context_text, question)
        answer = generate(prompt)

        CHAT_MEMORY[user_id].append(
            {"question": question, "answer": answer}
        )

        await update.message.reply_text(answer)

    except Exception as exc:
        logger.exception("Error while processing /ask")
        await update.message.reply_text(
            "Sorry, something went wrong while answering your question."
        )


async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history = CHAT_MEMORY.get(user_id)

    if not history:
        await update.message.reply_text(
            "No conversation history to summarize yet."
        )
        return

    conversation_text = "\n".join(
        f"{i}. Q: {h['question']}\n   A: {h['answer']}"
        for i, h in enumerate(history, 1)
    )

    try:
        summary_prompt = build_summary_prompt(conversation_text)
        summary = generate(summary_prompt)
        await update.message.reply_text(summary)

    except Exception:
        logger.exception("Error while summarizing")
        await update.message.reply_text(
            "Failed to generate summary."
        )


async def unknown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Unknown command.\n\n"
        "Use `/help` to see available commands.",
        parse_mode="Markdown",
    )

# ---------------------------------------------------------------------
# App Bootstrap
# ---------------------------------------------------------------------

def main():
    logger.info("Starting Mini RAG Bot")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ask", ask_cmd))
    app.add_handler(CommandHandler("summarize", summarize_cmd))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_cmd))

    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
