# AI Research Assistant – API Documentation

Base URL: `http://localhost:8000`  
Interactive Swagger UI: `http://localhost:8000/docs`  
Interactive ReDoc: `http://localhost:8000/redoc`

Because multi-agent research operations take between 30 and 120 seconds, the API operates **asynchronously**:
1. Submit a research topic via `POST /api/research` to obtain a `job_id`.
2. Poll the execution state via `GET /api/research/{job_id}`.
3. Once completed, fetch the report content or download the compiled `.pdf` or `.md` files.

Both `/api/research` and `/research` endpoint prefixes are supported interchangeably.

---

## Endpoint Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI Dashboard |
| `GET` | `/health` | Service health verification |
| `POST` | `/api/research` | Submit a research job |
| `GET` | `/api/research/{job_id}` | Retrieve job status, progress, and report payload |
| `GET` | `/api/research/{job_id}/download/{fmt}` | Download final report artifact (`pdf` or `md`) |

---

## 1. Health Check

### `GET /health`
Returns service availability status.

**Response `200 OK`**
```json
{
  "status": "ok"
}
```

---

## 2. Create Research Job

### `POST /api/research` (or `POST /research`)
Dispatches a background research job.

**Request Headers**
`Content-Type: application/json`

**Request Body**
```json
{
  "topic": "Impact of Artificial Intelligence on Modern Healthcare"
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `topic` | string | Yes | Research topic (minimum 3 characters). |

**Response `202 Accepted`**
```json
{
  "job_id": "deb86ece1f97",
  "status": "queued",
  "status_url": "/api/research/deb86ece1f97"
}
```

**cURL Example**
```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Impact of Artificial Intelligence on Modern Healthcare"}'
```

---

## 3. Query Job Status & Results

### `GET /api/research/{job_id}` (or `GET /research/{job_id}`)
Polls the execution state, current agent stage, review metrics, and the full report when finished.

**Path Parameters**
* `job_id` (string, required): 12-character hexadecimal job identifier.

#### Response: While In Progress (`running`)
```json
{
  "job_id": "deb86ece1f97",
  "topic": "Impact of Artificial Intelligence on Modern Healthcare",
  "status": "running",
  "stage": "searching",
  "stage_label": "Searching the web…",
  "agent": "researcher"
}
```

#### Possible `stage` Values
* `queued`: Queued for execution.
* `planning`: Planner agent generating tasks and queries.
* `searching`: Researcher agent running web searches.
* `deduplicating`: Deduplication engine filtering sources.
* `summarising`: Synthesizing factual notes per question.
* `writing`: Writer agent drafting the IEEE paper.
* `reviewing`: Reviewer agent validating citations and structure.
* `completed`: Research finished and artifacts compiled.
* `failed`: Execution encountered an error.

#### Response: Completed (`completed`)
```json
{
  "job_id": "deb86ece1f97",
  "topic": "Impact of Artificial Intelligence on Modern Healthcare",
  "status": "completed",
  "stage": "completed",
  "stage_label": "Report generated ✓",
  "title": "Artificial Intelligence in Healthcare: Clinical Applications and Challenges",
  "plan": [
    {
      "id": 1,
      "question": "What are current clinical applications of AI in diagnostics?",
      "search_queries": [
        "AI diagnostic tools clinical trials FDA approvals",
        "deep learning medical imaging radiology accuracy"
      ]
    }
  ],
  "sources_used": 14,
  "duplicates_removed": 5,
  "revisions": 1,
  "review": {
    "approved": true,
    "score": 9,
    "issues": []
  },
  "report": "# Artificial Intelligence in Healthcare...\n\n## Abstract\n...",
  "md_path": "outputs/deb86ece1f97/report.md",
  "pdf_path": "outputs/deb86ece1f97/report.pdf"
}
```

---

## 4. Download Report Artifacts

### `GET /api/research/{job_id}/download/{fmt}` (or `GET /research/{job_id}/download/{fmt}`)
Streams the compiled document file for the completed research job.

**Path Parameters**
* `job_id` (string, required): The job identifier.
* `fmt` (string, required): File format; must be `pdf` or `md`.

**Responses**
* `200 OK`: File attachment (`report.pdf` or `report.md`).
* `400 Bad Request`: `fmt` is not `pdf` or `md`.
* `404 Not Found`: Job does not exist or file missing.
* `409 Conflict`: Job is still `running` or `queued`.

**cURL Examples**
```bash
# Download IEEE PDF
curl -O -J http://localhost:8000/api/research/deb86ece1f97/download/pdf

# Download Markdown source
curl -O -J http://localhost:8000/api/research/deb86ece1f97/download/md
```

---

## 5. Client Integration Examples

### Python (using `httpx`)
```python
import time
import httpx

BASE_URL = "http://localhost:8000"

with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
    # 1. Start job
    resp = client.post("/api/research", json={"topic": "Quantum Computing in Cryptography"})
    job_id = resp.json()["job_id"]
    print(f"Dispatched job {job_id}")

    # 2. Poll until complete
    while True:
        job = client.get(f"/api/research/{job_id}").json()
        print(f"Status: {job['status']} | Stage: {job.get('stage_label')}")
        if job["status"] in ("completed", "failed"):
            break
        time.sleep(2)

    # 3. Download PDF
    if job["status"] == "completed":
        pdf_bytes = client.get(f"/api/research/{job_id}/download/pdf").content
        with open("research_report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("Downloaded IEEE research_report.pdf")
```

### JavaScript (`fetch`)
```javascript
async function runResearch(topic) {
  // 1. Dispatch
  const createRes = await fetch('/api/research', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  });
  const { job_id } = await createRes.json();

  // 2. Poll
  const interval = setInterval(async () => {
    const jobRes = await fetch(`/api/research/${job_id}`);
    const job = await jobRes.json();
    console.log(`Stage: ${job.stage_label}`);

    if (job.status === 'completed') {
      clearInterval(interval);
      console.log('Report complete! Title:', job.title);
      window.location.href = `/api/research/${job_id}/download/pdf`;
    } else if (job.status === 'failed') {
      clearInterval(interval);
      console.error('Job failed:', job.error);
    }
  }, 2000);
}
```
