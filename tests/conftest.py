import os

# llm.client rejects import when this is missing. A placeholder is enough:
# the suite stubs Groq and never sends a request.
os.environ.setdefault("GROQ_API_KEY", "test-key")
