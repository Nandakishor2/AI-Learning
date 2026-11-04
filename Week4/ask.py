#!/usr/bin/env python3
"""
Root entrypoint for asking questions to the Global HR Leave Policy RAG Assistant.
Usage:
    python ask.py
    python ask.py "What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?"
"""
from Services.ask import main

if __name__ == "__main__":
    main()
