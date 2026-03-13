# ⚡ FPGA · AI Analyzer

Static RTL analysis tool powered by **Groq LLM (LLaMA3-70B)** via a **Streamlit** web UI.

## Features
| Category | Details |
|---|---|
| **Latch Inference** | Incomplete `if/case` → unwanted latches |
| **Sensitivity List** | Missing signals in `process()` / `always @()` |
| **Async Reset** | Incorrect reset coding patterns |
| **CDC** | Clock Domain Crossing without synchronizers |
| **Combinational Loops** | Feedback paths in combo logic |
| **Log Parsing** | Vivado/Quartus `Critical Warning`, timing violations |
| **IEEE Compliance** | IEEE Std 1076 / 1364 / 1800 scoring |
| **Resource Hints** | Redundant logic detection |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Groq API key (get free key at console.groq.com)
export GROQ_API_KEY="gsk_your_key_here"

# 3. Launch
streamlit run app.py
```

You can also paste the API key directly in the sidebar at runtime.

## Supported File Types
`.vhd` · `.vhdl` · `.v` · `.sv` · `.txt` · `.log`

## Architecture

```
┌─────────────────────────────────────┐
│          Streamlit Frontend         │
│  File Uploader │ Code Editor │ Tabs │
└────────────────┬────────────────────┘
                 │
          analyze_code()
                 │
         chunk_code()  ←── Large file splitting
                 │
        ┌────────▼────────┐
        │   Groq API      │
        │  llama3-70b     │
        │  + System Prompt│
        └────────┬────────┘
                 │ JSON response
        ┌────────▼────────┐
        │  Issue Parser   │
        │  Error/Warn/    │
        │  Suggestion     │
        └────────┬────────┘
                 │
         Streamlit Tabs UI
```

## Output Format
Every analysis returns structured JSON:
```json
{
  "summary": { "overall_health": "FAIR", "error_count": 2, ... },
  "issues": [
    {
      "id": "ISSUE-001",
      "severity": "ERROR",
      "category": "LATCH",
      "title": "Inferred latch in comb process",
      "description": "...",
      "line_reference": "Line 42",
      "code_snippet": "...",
      "fix": "Add else branch",
      "corrected_code": "..."
    }
  ],
  "ieee_compliance": { "score": 78, "notes": "..." }
}
```
