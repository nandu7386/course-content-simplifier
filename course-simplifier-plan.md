# Course Content Simplification Agent — Plan

## Top-Level Overview

Build a minimal single-file Streamlit application that accepts academic course content and a
learner proficiency level, sends a structured prompt to IBM Granite via the `ibm-watsonx-ai`
Python SDK, and displays the structured response across five expandable panels in the browser.

**Scope:**
- One Python file: `app.py` (UI + prompt builder + Granite call + response parser)
- Supporting files: `.env`, `.env.example`, `requirements.txt`, `README.md`
- No databases, no authentication, no external APIs beyond IBM watsonx, no multi-agent setup

**Non-goals:** RAG, voice, multi-agent orchestration, persistent storage, custom frontend,
PDF upload

---

## Confirmed Decisions

| Decision | Value |
|---|---|
| IBM Granite model ID | `ibm/granite-3-2-8b-instruct` |
| Output sections | 5 — exact headings: `## Simplified Explanation`, `## Important Terms`, `## Key Points`, `## Real-World Example`, `## Quick Quiz` |
| Proficiency level selector | Streamlit sidebar (`st.sidebar.radio`) |
| Main content area | Academic text input + five output expanders |
| System prompt | Final version provided by user — used verbatim in `simplify_content()` |

---

## Sub-Tasks

---

### Sub-Task 1 — Project scaffolding

**Status:** `[ ] pending`

**Intent:**
Create the non-Python supporting files so the project is immediately runnable after cloning.
These files are prerequisites for everything else.

**Expected Outcomes:**
- `requirements.txt` lists exactly three dependencies: `streamlit`, `ibm-watsonx-ai`, `python-dotenv`
- `.env.example` documents the three required environment variables with placeholder values
- `.gitignore` excludes `.env` and standard Python/Streamlit noise
- `README.md` explains prerequisites, setup steps (`pip install -r requirements.txt`,
  populate `.env`), and how to run (`streamlit run app.py`)

**Todo List:**
1. Create `requirements.txt` with `streamlit`, `ibm-watsonx-ai`, `python-dotenv`
2. Create `.env.example` with `WATSONX_API_KEY=`, `WATSONX_PROJECT_ID=`, `WATSONX_URL=`
3. Create `.gitignore` covering `.env`, `__pycache__/`, `.streamlit/`
4. Create `README.md` with setup and run instructions

**Relevant Context:** Greenfield project — workspace is empty.

---

### Sub-Task 2 — Core `app.py`: credentials, model client, prompt builder

**Status:** `[ ] pending`

**Intent:**
Implement the non-UI part of `app.py`: load credentials from `.env`, initialise the
`ibm-watsonx-ai` model client for IBM Granite, and define `simplify_content(content, level)`
which builds the structured prompt and returns the raw Granite response string.

**Expected Outcomes:**
- `app.py` loads `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` from `.env`
  via `python-dotenv`
- An `ibm-watsonx-ai` `ModelInference` is initialised once at module level using those
  credentials, targeting model ID `ibm/granite-3-2-8b-instruct`
- `simplify_content(content: str, level: str) -> str` constructs a prompt that:
  - Sets a system instruction describing the agent's role as an academic content simplifier
  - Includes level-specific rules for all four proficiency levels:
    - **Beginner** — plain language, avoid jargon, use analogies
    - **Intermediate** — introduce basic technical terms with brief definitions
    - **Advanced** — retain full technical terminology, add depth and nuance
    - **Expert** — precise technical language, assume strong prior knowledge
  - Instructs Granite to return exactly **five** sections delimited by these exact headings:
    `## Simplified Explanation`, `## Important Terms`, `## Key Points`,
    `## Real-World Example`, `## Quick Quiz`
  - Under `## Quick Quiz` instructs Granite to produce exactly 3 numbered questions
  - Instructs Granite not to invent facts beyond the input, not to remove important concepts,
    and to state limitations clearly if the input is ambiguous
  - Appends the user's raw academic content
- The function returns the raw text string from the SDK call

**Todo List:**
1. Add `load_dotenv()` call and read the three env vars at module level
2. Initialise `Credentials` and `ModelInference` with model ID `ibm/granite-3-2-8b-instruct`
3. Define level-specific instruction strings for all four proficiency levels
4. Define `simplify_content(content, level)` that assembles the full prompt and calls the model
5. Return the raw response string from the SDK call

**Relevant Context:**
- SDK import path: `from ibm_watsonx_ai.foundation_models import ModelInference`
- Credentials import: `from ibm_watsonx_ai import Credentials`
- Model ID (confirmed, not to be changed): `"ibm/granite-3-2-8b-instruct"`
- The five `##` section headings used here must match exactly the keys expected by
  `parse_response` in Sub-Task 3

---

### Sub-Task 3 — Core `app.py`: response parser

**Status:** `[ ] pending`

**Intent:**
Add `parse_response(raw: str) -> dict` inside `app.py` that splits the Granite response
into the five named sections so the Streamlit UI can render each one independently.

**Expected Outcomes:**
- `parse_response` accepts the raw response string and returns a `dict` with exactly five keys:
  `simplified_explanation`, `important_terms`, `key_points`, `real_world_example`,
  `quick_quiz`
- Splitting is done by matching the `## ` heading markers set in the prompt
- Each section value is stripped of leading/trailing whitespace
- If a section is missing from the response, the dict value is `"(Not provided)"`

**Todo List:**
1. Define an ordered list of `(heading_text, dict_key)` pairs for the five sections
2. Implement `parse_response(raw)` using `re.split` on `## ` markers to slice the response
3. For each expected key, extract the text between its heading and the next heading
   (or end of string)
4. Strip whitespace from each extracted value
5. Default missing sections to `"(Not provided)"`

**Relevant Context:**
- The five section headings (from the final system prompt) are fixed in Sub-Task 2 and must be matched exactly here:
  `Simplified Explanation`, `Important Terms`, `Key Points`, `Real-World Example`, `Quick Quiz`
- This function is called by the Streamlit UI code in Sub-Task 4

---

### Sub-Task 4 — Core `app.py`: Streamlit UI

**Status:** `[ ] pending`

**Intent:**
Add the Streamlit UI layer to `app.py` — sidebar level selector, main-area content input,
run button, spinner, and five expandable result panels.

**Expected Outcomes:**
- `st.set_page_config` sets a page title and icon
- **Sidebar** contains:
  - App title / short description
  - `st.sidebar.radio` for proficiency level: Beginner, Intermediate, Advanced, Expert
- **Main area** contains:
  - Page header
  - `st.text_area` for academic content input
  - "Simplify Content" button
  - If content is empty on button click → `st.warning`, no model call
  - On button click with content → `st.spinner` wraps `simplify_content` + `parse_response`
  - SDK errors caught with `try/except` and shown via `st.error`
  - On success → five `st.expander` panels, one per section, labelled to match the
    section headings from the prompt

**Todo List:**
1. Add `st.set_page_config` with title and icon
2. Build sidebar: app description + `st.sidebar.radio` level selector
3. Add main-area header and `st.text_area` for content input
4. Add "Simplify Content" button with empty-input guard (`st.warning`)
5. Wrap `simplify_content` + `parse_response` in `st.spinner` and `try/except`
6. Render five `st.expander` panels from the parsed dict
7. Show `st.error` for SDK/runtime exceptions

**Relevant Context:**
- `simplify_content` and `parse_response` are defined earlier in the same `app.py` file
- Expander labels must visually match the section heading text for user clarity

---

## File Map (final state)

```
CourseContentSimplifier/
├── app.py               # All logic: credentials, model client, prompt builder, parser, Streamlit UI
├── .env                 # Secrets — never committed
├── .env.example         # Safe credential template — committed to source control
├── .gitignore
├── requirements.txt
└── README.md
```
