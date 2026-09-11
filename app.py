"""
Course Content Simplification Agent
------------------------------------
Streamlit app that rewrites academic content at the selected learner
proficiency level using IBM Granite via the ibm-watsonx-ai SDK.
"""

import os
import re

import streamlit as st
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# ---------------------------------------------------------------------------
# Credentials & model client
# ---------------------------------------------------------------------------

load_dotenv()

_credentials = Credentials(
    url=os.environ["WATSONX_URL"],
    api_key=os.environ["WATSONX_API_KEY"],
)

_model = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials=_credentials,
    project_id=os.environ["WATSONX_PROJECT_ID"],
)

# ---------------------------------------------------------------------------
# System prompt (authoritative — defines the agent behaviour and output format)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a Course Content Simplification Agent.

Your purpose is to adapt academic course content to the learner's selected proficiency level while preserving the factual meaning and important information of the source.

INPUTS:
- Course content provided by the user
- Learner proficiency level

SUPPORTED PROFICIENCY LEVELS:
- Beginner
- Intermediate
- Advanced
- Expert

GENERAL RULES:
1. Base the response only on the provided course content.
2. Never intentionally change the factual meaning of the source.
3. Never fabricate, assume, or add unsupported facts.
4. Preserve important concepts, definitions, formulas, numbers, technical facts, relationships, and conditions from the source.
5. Adapt the explanation, terminology, depth, and examples according to the selected proficiency level.
6. If the source content is ambiguous, incomplete, or does not contain enough information for a requested point, clearly state that limitation instead of guessing.
7. Keep the explanation educational, clear, and relevant to the provided content.

PROFICIENCY LEVEL BEHAVIOR:

Beginner:
- Explain concepts using simple language.
- Assume little or no prior knowledge.
- Define important technical terms in simple words.
- Use simple analogies or everyday examples when they help explain the source.
- Do not remove important technical concepts just to make the explanation easier.

Intermediate:
- Use basic technical terminology.
- Explain important concepts clearly.
- Define terminology that may be unfamiliar.
- Assume some prior academic knowledge.
- Maintain the important technical details of the source.

Advanced:
- Preserve the source's technical terminology.
- Provide deeper and more precise explanations.
- Explain relationships between important concepts when supported by the source.
- Assume the learner understands fundamental concepts.
- Avoid unnecessary oversimplification.

Expert:
- Use precise technical terminology.
- Avoid unnecessary simplification.
- Focus on deeper relationships, assumptions, mechanisms, limitations, and technical details when supported by the source.
- Assume strong prior knowledge.
- Preserve the technical depth of the source.

OUTPUT FORMAT:
Always produce exactly these five sections using these exact headings:

## Simplified Explanation
Provide an explanation of the source content at the selected proficiency level.

## Important Terms
List important technical or academic terms from the source and explain them appropriately for the selected proficiency level.

## Key Points
List the most important concepts, facts, formulas, relationships, or conclusions from the source.

## Real-World Example
Provide one relevant example that helps explain the source content. Keep the example consistent with the facts in the source and do not introduce unsupported claims.

## Quick Quiz
Generate exactly 3 short questions based only on the provided course content.
Number them 1, 2, and 3.
Do not provide the answers unless explicitly requested.

IMPORTANT:
- Use exactly the five headings above.
- Do not add extra sections or headings.
- Do not include unsupported information.
- Do not change the factual meaning of the source."""


# ---------------------------------------------------------------------------
# Core function: build prompt and call IBM Granite
# ---------------------------------------------------------------------------

def simplify_content(content: str, level: str) -> str:
    """Send content + level to IBM Granite and return the raw response string."""
    user_message = (
        f"Learner proficiency level: {level}\n\n"
        f"Course content:\n{content}"
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    response = _model.chat(messages=messages)
    return response["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Response parser: split raw text into five named sections
# ---------------------------------------------------------------------------

# Ordered list of (exact heading text, dict key) pairs — must match SYSTEM_PROMPT headings.
_SECTIONS = [
    ("Simplified Explanation", "simplified_explanation"),
    ("Important Terms",        "important_terms"),
    ("Key Points",             "key_points"),
    ("Real-World Example",     "real_world_example"),
    ("Quick Quiz",             "quick_quiz"),
]


def parse_response(raw: str) -> dict:
    """Split Granite's raw response into a dict of five section strings."""
    # Split on any '## <Heading>' pattern (handles optional trailing whitespace)
    parts = re.split(r"##\s+", raw)

    # Build a lookup: normalised heading text -> body text
    heading_to_body: dict[str, str] = {}
    for part in parts:
        if not part.strip():
            continue
        newline_idx = part.find("\n")
        if newline_idx == -1:
            heading = part.strip()
            body = ""
        else:
            heading = part[:newline_idx].strip()
            body = part[newline_idx:].strip()
        heading_to_body[heading] = body

    result: dict[str, str] = {}
    for heading_text, key in _SECTIONS:
        result[key] = heading_to_body.get(heading_text, "(Not provided)")

    return result


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Course Content Simplifier", page_icon="🎓")

# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.title("🎓 Course Content Simplifier")
    st.markdown(
        "Paste academic content in the main area, select your proficiency "
        "level below, then click **Simplify Content**."
    )
    st.divider()
    level = st.radio(
        "Learner proficiency level",
        options=["Beginner", "Intermediate", "Advanced", "Expert"],
        index=0,
    )

# --- Main area ---------------------------------------------------------------
st.header("Course Content Simplification Agent")
st.markdown(
    "Enter your academic course content below. The agent will rewrite it "
    "at the **{}** level and produce five structured output sections.".format(level)
)

content = st.text_area(
    "Academic content",
    placeholder="Paste your course content here (e.g. lecture notes, textbook passage, topic description)…",
    height=260,
)

if st.button("Simplify Content", type="primary"):
    if not content.strip():
        st.warning("Please paste some academic content before clicking Simplify Content.")
    else:
        with st.spinner("Sending to IBM Granite — this may take a few seconds…"):
            try:
                raw = simplify_content(content, level)
                sections = parse_response(raw)
            except Exception as exc:
                st.error(f"Error communicating with IBM watsonx: {exc}")
                sections = None

        if sections:
            st.success("Done! Expand any section below to read the output.")
            with st.expander("📖 Simplified Explanation", expanded=True):
                st.markdown(sections["simplified_explanation"])
            with st.expander("📚 Important Terms"):
                st.markdown(sections["important_terms"])
            with st.expander("✅ Key Points"):
                st.markdown(sections["key_points"])
            with st.expander("🌍 Real-World Example"):
                st.markdown(sections["real_world_example"])
            with st.expander("❓ Quick Quiz"):
                st.markdown(sections["quick_quiz"])
