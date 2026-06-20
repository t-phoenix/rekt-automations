#!/usr/bin/env python3
"""Quick smoke test for each LLM provider configured in .env."""
import os
import sys
from pathlib import Path

# Load .env from meme-api root
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
os.chdir(root)

from dotenv import load_dotenv

load_dotenv(root / ".env")


def mask(key: str | None) -> str:
    if not key:
        return "(not set)"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def test_google() -> tuple[bool, str]:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return False, "GOOGLE_API_KEY not set"
    if key.startswith("AIza"):
        key_type = "legacy Standard key (AIza)"
    elif key.startswith("AQ."):
        key_type = "Auth key (AQ.) — current AI Studio default"
    else:
        key_type = f"unknown prefix ({key[:6]}...)"
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=key)
        r = llm.invoke("Reply with exactly: ok")
        return True, f"OK ({key_type}) — {str(r.content)[:40]}"
    except Exception as e:
        return False, f"{key_type}: {str(e)[:180]}"


def test_openai() -> tuple[bool, str]:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return False, "OPENAI_API_KEY not set"
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=key)
        r = llm.invoke("Reply with exactly: ok")
        return True, f"OK — {str(r.content)[:40]}"
    except Exception as e:
        return False, str(e)[:200]


def test_groq() -> tuple[bool, str]:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return False, "GROQ_API_KEY not set"
    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=key)
        r = llm.invoke("Reply with exactly: ok")
        return True, f"OK — {str(r.content)[:40]}"
    except Exception as e:
        return False, str(e)[:200]


def test_deepseek() -> tuple[bool, str]:
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        return False, "DEEPSEEK_API_KEY not set"
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=key,
            base_url="https://api.deepseek.com",
        )
        r = llm.invoke("Reply with exactly: ok")
        return True, f"OK — {str(r.content)[:40]}"
    except Exception as e:
        return False, str(e)[:200]


def test_openrouter() -> tuple[bool, str]:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return False, "OPENROUTER_API_KEY not set"
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="google/gemini-2.5-flash",
            api_key=key,
            base_url="https://openrouter.ai/api/v1",
        )
        r = llm.invoke("Reply with exactly: ok")
        return True, f"OK — {str(r.content)[:40]}"
    except Exception as e:
        return False, str(e)[:200]


def main():
    tests = [
        ("Google (gemini-flash)", test_google),
        ("OpenAI (gpt-4o-mini)", test_openai),
        ("Groq (llama-3.3-70b)", test_groq),
        ("DeepSeek", test_deepseek),
        ("OpenRouter (gemini via OR)", test_openrouter),
    ]

    print("LLM provider smoke tests\n" + "=" * 50)
    print(f"DEFAULT_LLM={os.getenv('DEFAULT_LLM', '(not set)')}\n")

    results = []
    for name, fn in tests:
        ok, msg = fn()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}")
        print(f"       {msg}\n")
        results.append((name, ok))

    working = [n for n, ok in results if ok]
    print("=" * 50)
    if working:
        print(f"Working providers: {', '.join(working)}")
        if not any("Google" in n and ok for n, ok in results):
            print("\nFix: set DEFAULT_LLM to a working preset, e.g.:")
            if any("Groq" in n and ok for n, ok in results):
                print("  DEFAULT_LLM=groq-llama-70b")
            if any("OpenAI" in n and ok for n, ok in results):
                print("  DEFAULT_LLM=gpt-4o-mini")
    else:
        print("No providers passed — check keys and restart server.")
        sys.exit(1)


if __name__ == "__main__":
    main()
