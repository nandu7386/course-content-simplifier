# Course Content Simplification Agent

A minimal Streamlit application that rewrites academic content at the appropriate difficulty level using IBM Granite via IBM watsonx.

---

## Prerequisites

- Python 3.9 or later
- An IBM Cloud account with watsonx.ai access
- A watsonx project ID
- An IBM Cloud API key

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd CourseContentSimplifier
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> **Never commit `.env` to source control.** It is listed in `.gitignore`.

URL options by region:
- Dallas (us-south): `https://us-south.ml.cloud.ibm.com`
- Frankfurt (eu-de): `https://eu-de.ml.cloud.ibm.com`
- Tokyo (jp-tok): `https://jp-tok.ml.cloud.ibm.com`
- London (eu-gb): `https://eu-gb.ml.cloud.ibm.com`

---

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

---

## Usage

1. Select your learner proficiency level from the **sidebar** (Beginner, Intermediate, Advanced, Expert).
2. Paste academic course content into the text area.
3. Click **Simplify Content**.
4. Review the five output sections:
   - **Simplified Explanation** — content rewritten at the selected level
   - **Important Terms** — key technical or academic terms explained
   - **Key Points** — the most important facts, formulas, and conclusions
   - **Real-World Example** — a concrete example grounded in the source
   - **Quick Quiz** — 3 short questions to test understanding

---

## Model

IBM Granite `ibm/granite-3-2-8b-instruct` via the `ibm-watsonx-ai` Python SDK.

---

## Project Structure

```
CourseContentSimplifier/
├── app.py               # All logic: credentials, model client, prompt builder, parser, Streamlit UI
├── .env                 # Your credentials — never committed
├── .env.example         # Credential template — safe to commit
├── requirements.txt
└── README.md
```
