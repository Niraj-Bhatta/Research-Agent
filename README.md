# AI Research Assistant

A **self‑contained, multi‑agent research pipeline** that takes a topic, searches the web, deduplicates results, synthesises notes, writes an IEEE‑style technical paper, and exports both Markdown and PDF. All components run locally with the free‑tier **Google Gemini** API and **Tavily** search.

---

## Architecture Overview

![Architecture Diagram](docs/images/Architecture.png)

The diagram shows the flow from the user interface through the FastAPI backend into a LangGraph state‑graph that orchestrates seven agents. External services are the Gemini LLM and Tavily search API. The final node writes artefacts to the `outputs/` directory.

---

## Folder Structure

```
Research-Assistant/
├── app/                     # FastAPI application and core logic
│   ├── agents/              # Autonomous agents (Planner, Researcher, …)
│   │   ├── __init__.py
│   │   ├── planner.py       # Breaks a topic into research questions & queries
│   │   ├── researcher.py    # Executes Tavily searches for each query
│   │   ├── reviewer.py      # Validates citations and overall quality
│   │   └── writer.py        # Generates IEEE‑formatted manuscript
│   ├── export/              # PDF generation utilities
│   │   ├── __init__.py
│   │   └── pdf.py           # Uses xhtml2pdf to render the final PDF
│   ├── static/              # Front‑end assets (HTML, CSS, JS)
│   ├── tools/               # Helper utilities (deduplication, search wrapper)
│   ├── config.py            # Central config, environment handling
│   ├── graph.py             # LangGraph state‑graph definition
│   ├── llm.py               # Gemini wrapper with retries
│   └── main.py              # FastAPI routes, background worker
├── docs/                    # Detailed documentation
│   ├── API.md               # REST endpoint specifications
│   └── architecture.md      # Full technical design and sequence diagrams
├── outputs/                 # Generated reports (Markdown + PDF) – ignored by git
├── .env.example             # Template for required environment variables
├── .gitignore               # Standard ignores (venv, outputs, secrets)
├── docker-compose.yml       # Docker Compose orchestration
├── Dockerfile               # Container build definition
├── requirements.txt         # Python dependencies (pinned versions)
└── README.md               # This file
```

---

## Agents Description

| Agent | Responsibility | Key File |
|-------|----------------|----------|
| **Planner** | Decomposes the user‑provided topic into 4‑6 IEEE‑style research questions and generates corresponding search queries. | `app/agents/planner.py` |
| **Researcher** | Sends each query to the Tavily API, collects raw web results, and tags them with the originating question. | `app/agents/researcher.py` |
| **Deduplication** (tool) | Normalises URLs and applies TF‑IDF cosine similarity to filter out duplicate sources. | `app/tools/dedup.py` |
| **Summarizer** | Summarises the unique sources for each question, producing bullet‑point notes with explicit citation indices (`[n]`). | `app/agents/researcher.py` |
| **Writer** | Assembles the notes into a full IEEE conference paper (title, abstract, sections, references) respecting font size, colour, and style constraints. | `app/agents/writer.py` |
| **Reviewer** | Checks the draft for completeness, readability, and citation integrity. If the score is < 8 it feeds a critique back to the Writer; otherwise it allows export. | `app/agents/reviewer.py` |
| **Export** (node) | Formats the final Markdown, inserts a blank line between each reference, and renders a PDF via `xhtml2pdf`. | `app/export/pdf.py` |

---

## Key Features

- **Fully autonomous workflow** – once a topic is submitted the system runs to completion without further user interaction.
- **IEEE‑compliant output** – black text, Times‑Roman font, exact font‑size specifications, and one reference per line.
- **Live progress UI** – a dark‑theme web dashboard shows the current pipeline stage (`planning…`, `searching…`, `summarising…`, `writing…`, `reviewing…`, `completed`).
- **Free‑tier friendly** – uses `gemini-flash-lite-latest` (no paid credits) and Tavily’s free tier.
- **Docker ready** – single‑command deployment with all dependencies bundled.

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Research-Assistant.git
   cd Research-Assistant
   ```
2. **Create a virtual environment** (Windows PowerShell example)
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API keys** – copy the example file and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to set:
   ```text
   GEMINI_API_KEY=your_gemini_key
   TAVILY_API_KEY=your_tavily_key
   ```
5. **Run the server locally**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Open <http://localhost:8000> to view the UI.

---

## Docker Deployment

```bash
# Build and start the container
docker compose up --build
```
The service will be reachable at `http://localhost:8000`. Use the same `.env` file (mounted automatically) for credentials.

---

## API Usage Examples

*Submit a research job*:
```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Applications of Quantum Computing in Cryptography"}'
```
*Poll job status*:
```bash
curl http://localhost:8000/api/research/<job_id>
```
*Download artefacts*:
```bash
curl -O -J http://localhost:8000/api/research/<job_id>/download/pdf
curl -O -J http://localhost:8000/api/research/<job_id>/download/md
```

Full endpoint documentation is available in `docs/API.md`.

---

## License

This project is released under the MIT License.
