"""
"Ask this analysis" — a grounded question-answering layer over the project's own
documents and tables.

How it works, and what it deliberately does not do:

  Retrieval is local and transparent. Documents are split into chunks, and chunks
  are scored by how many of the question's terms they contain. There are no
  embeddings: the evidence pack is a few hundred chunks, term overlap works, and
  a reader can check why a chunk was selected. Adding an embedding model would
  add cost and opacity for no measured gain.

  Only the selected chunks are sent to the model. The raw dataset is never sent
  anywhere. The model is instructed to answer from the supplied evidence alone
  and to say so when the evidence does not cover the question.

  Without an API key the page still works: the same retrieval runs and the
  matching passages are shown directly. That fallback is labelled as retrieved
  text, never presented as an AI-generated answer.
"""

import os
import re
from dataclasses import dataclass

import streamlit as st

# Default model. gpt-6-luna is OpenAI's efficient model for focused, high-volume
# tasks, which is what grounded question answering over a small evidence pack is.
# Override with the OPENAI_MODEL environment variable or a Streamlit secret.
DEFAULT_MODEL = "gpt-6-luna"
MAX_OUTPUT_TOKENS = 700
MAX_QUESTIONS_PER_SESSION = 12
MAX_CHUNKS_SENT = 8
CHUNK_WORDS = 190

SUGGESTED_QUESTIONS = [
    "Why was R80711 selected for investigation?",
    "Why is 671.6 MWh not recoverable energy?",
    "Did machine learning add operational value?",
    "Why is Method B the primary method?",
    "What did the timestamp correction change?",
    "What would you request from the operator next?",
    "How does this analysis transfer to solar?",
    "What are the three biggest limitations?",
]

SYSTEM_INSTRUCTIONS = """\
You answer questions about one specific wind-performance analysis project, using
only the evidence passages supplied with each question.

Rules, in order of importance:

1. Answer only from the supplied evidence. If it does not cover the question, say
   "The project does not contain enough evidence to answer that", then name the
   specific operational record or analysis that would be needed.
2. Cite sources by filename in square brackets, for example [phase_3_findings.md]
   or [decision_event_register.csv]. Cite the file each figure came from.
3. Distinguish observation (reproducible from the data), interpretation (the
   analyst's reading), and hypothesis (a possible cause that is not established).
   Never present a hypothesis as an observation.
4. Never diagnose a turbine fault, and never claim recoverable energy, recovered
   revenue or production uplift. Potential shortfall is not recoverable energy.
5. Never invent event codes, work orders, curtailment records or operator logs.
   The project has none; that absence is one of its central findings.
6. Never make claims about Clir Renewables' platform, customers, performance or
   internal methods. This is an independent project using public data.
7. Synthetic benchmark results are not real-world accuracy. The project has no
   real labels, so precision and recall do not exist for it.
8. Keep answers under about 250 words unless asked for more detail.

Write plainly. Do not pad the answer with caveats the question did not raise, but
never drop a caveat that changes the meaning of the number you are quoting.
"""


@dataclass
class Chunk:
    source: str
    text: str
    heading: str


STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "it", "for", "on", "with",
    "that", "this", "was", "were", "are", "be", "by", "as", "at", "from", "what",
    "why", "how", "does", "did", "do", "you", "your", "would", "should", "can",
    "about", "there", "their", "has", "have", "had", "not", "but", "if", "we",
}


def tokenise(text):
    """Lower-case words of three or more characters, minus common filler."""
    return [w for w in re.findall(r"[a-z0-9_.]+", text.lower())
            if len(w) >= 3 and w not in STOP_WORDS]


@st.cache_data(show_spinner=False)
def build_evidence_pack(documents, tables):
    """
    Split the project's documents and small tables into retrievable chunks.

    Markdown is split on headings first so a chunk keeps its context, then long
    sections are split again on length. Each chunk remembers its filename and
    heading, which is what the citation refers to.
    """
    chunks = []
    for name, text in documents.items():
        sections = re.split(r"\n(?=#{1,4}\s)", text)
        for section in sections:
            lines = section.strip().splitlines()
            if not lines:
                continue
            heading = lines[0].lstrip("# ").strip() if lines[0].startswith("#") else ""
            words = section.split()
            for start in range(0, len(words), CHUNK_WORDS):
                piece = " ".join(words[start:start + CHUNK_WORDS])
                if len(piece.split()) < 12:
                    continue
                chunks.append(Chunk(source=name, text=piece, heading=heading))

    for name, text in tables.items():
        words = text.split()
        for start in range(0, len(words), CHUNK_WORDS):
            piece = " ".join(words[start:start + CHUNK_WORDS])
            if len(piece.split()) < 8:
                continue
            chunks.append(Chunk(source=name, text=piece, heading="table data"))
    return chunks


def retrieve(question, chunks, limit=MAX_CHUNKS_SENT):
    """
    Score chunks by overlap with the question's terms.

    Transparent on purpose: the score is the count of distinct question terms
    present in the chunk, with a small bonus for the filename matching a term so
    that "what does phase_3_findings say" finds the right file.
    """
    terms = set(tokenise(question))
    if not terms:
        return []
    scored = []
    for chunk in chunks:
        chunk_terms = set(tokenise(chunk.text))
        overlap = len(terms & chunk_terms)
        if overlap == 0:
            continue
        score = overlap
        if terms & set(tokenise(chunk.source)):
            score += 2
        if chunk.heading and terms & set(tokenise(chunk.heading)):
            score += 1.5
        scored.append((score, chunk))
    scored.sort(key=lambda pair: pair[0], reverse=True)

    # Spread the selection across files so one long document cannot crowd out
    # the rest of the evidence.
    selected, per_source = [], {}
    for score, chunk in scored:
        if per_source.get(chunk.source, 0) >= 3:
            continue
        selected.append((score, chunk))
        per_source[chunk.source] = per_source.get(chunk.source, 0) + 1
        if len(selected) >= limit:
            break
    return selected


def format_evidence(selected):
    """Lay the retrieved chunks out for the model, each labelled with its source."""
    blocks = []
    for index, (score, chunk) in enumerate(selected, start=1):
        label = f"[{chunk.source}]" + (f" — {chunk.heading}" if chunk.heading else "")
        blocks.append(f"EVIDENCE {index} {label}\n{chunk.text}")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# API configuration
# ---------------------------------------------------------------------------

def read_secret(name):
    """
    Read configuration from the environment or Streamlit's server-side secrets.

    Never from a text input, a CSV or source code. Accessing st.secrets raises
    when no secrets file exists, so it is guarded.
    """
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def api_key_available():
    return bool(read_secret("OPENAI_API_KEY"))


def configured_model():
    return read_secret("OPENAI_MODEL") or DEFAULT_MODEL


def ask_model(question, evidence_text, history, client=None):
    """
    Send the question and the retrieved evidence to the Responses API.

    `client` exists so tests can pass a stub. Nothing else injects it.

    Returns (answer_text, error_message). Exactly one is populated.
    """
    if client is None:
        key = read_secret("OPENAI_API_KEY")
        if not key:
            return None, "no_key"
        try:
            from openai import OpenAI
        except ImportError:
            return None, "The openai package is not installed."
        client = OpenAI(api_key=key)

    conversation = []
    for earlier_question, earlier_answer in history[-3:]:
        conversation.append({"role": "user", "content": earlier_question})
        conversation.append({"role": "assistant", "content": earlier_answer})
    conversation.append({
        "role": "user",
        "content": (f"Question: {question}\n\n"
                    f"Evidence passages from the project:\n\n{evidence_text}\n\n"
                    "Answer using only these passages. Cite filenames in square "
                    "brackets.")})

    try:
        response = client.responses.create(
            model=configured_model(),
            instructions=SYSTEM_INSTRUCTIONS,
            input=conversation,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        return response.output_text, None
    except Exception as error:
        return None, describe_error(error)


def describe_error(error):
    """Turn an SDK exception into something a reader can act on."""
    name = type(error).__name__
    text = str(error)
    if "Authentication" in name or "401" in text or "invalid_api_key" in text:
        return ("Authentication failed. The configured API key was rejected. Check "
                "OPENAI_API_KEY in the environment or in .streamlit/secrets.toml.")
    if "RateLimit" in name or "429" in text:
        return ("Rate limit or quota reached. Wait a moment and try again, or check "
                "the billing status of the account that owns the key.")
    if "Connection" in name or "Timeout" in name:
        return ("Could not reach the API. Check the network connection, then retry. "
                "The rest of the application does not need the API.")
    if "NotFound" in name or "model" in text.lower():
        return (f"The configured model ({configured_model()}) was not available to "
                "this key. Set OPENAI_MODEL to a model the account can use.")
    return f"The request failed ({name}). The rest of the application is unaffected."
