import streamlit as st
import os
import json
import re
import urllib.request
import urllib.error

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FPGA · AI Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Industrial Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: #0a0e14;
    color: #c9d1d9;
}

.main { background-color: #0a0e14; }

/* ── Header ── */
.fpga-header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    border: 1px solid #30363d;
    border-left: 4px solid #f7c948;
    padding: 28px 36px;
    border-radius: 4px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.fpga-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 40px,
        rgba(247, 201, 72, 0.03) 40px,
        rgba(247, 201, 72, 0.03) 41px
    );
    pointer-events: none;
}
.fpga-header h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #f7c948;
    margin: 0;
    letter-spacing: 3px;
    text-transform: uppercase;
}
.fpga-header p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #8b949e;
    margin: 6px 0 0 0;
    letter-spacing: 2px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Rajdhani', sans-serif;
    color: #f7c948;
    letter-spacing: 2px;
    font-size: 1.1rem;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
}

/* ── Cards ── */
.card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.card-error {
    border-left: 3px solid #f85149;
    background: linear-gradient(90deg, rgba(248,81,73,0.06) 0%, #161b22 100%);
}
.card-warning {
    border-left: 3px solid #f7c948;
    background: linear-gradient(90deg, rgba(247,201,72,0.06) 0%, #161b22 100%);
}
.card-suggestion {
    border-left: 3px solid #3fb950;
    background: linear-gradient(90deg, rgba(63,185,80,0.06) 0%, #161b22 100%);
}
.card-info {
    border-left: 3px solid #58a6ff;
    background: linear-gradient(90deg, rgba(88,166,255,0.06) 0%, #161b22 100%);
}

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 1px;
    font-weight: 600;
    text-transform: uppercase;
}
.badge-error   { background: rgba(248,81,73,0.15);  color: #f85149; border: 1px solid rgba(248,81,73,0.3); }
.badge-warning { background: rgba(247,201,72,0.15); color: #f7c948; border: 1px solid rgba(247,201,72,0.3); }
.badge-ok      { background: rgba(63,185,80,0.15);  color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
.badge-info    { background: rgba(88,166,255,0.15); color: #58a6ff; border: 1px solid rgba(88,166,255,0.3); }

/* ── Code blocks ── */
.code-block {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #a5d6ff;
    white-space: pre-wrap;
    overflow-x: auto;
    margin-top: 10px;
}

/* ── Metric row ── */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
}
.metric-box {
    flex: 1;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 16px 20px;
    text-align: center;
}
.metric-box .num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1;
}
.metric-box .lbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    color: #8b949e;
    margin-top: 4px;
    text-transform: uppercase;
}
.num-error   { color: #f85149; }
.num-warning { color: #f7c948; }
.num-ok      { color: #3fb950; }
.num-info    { color: #58a6ff; }

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    font-size: 0.9rem;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #f7c948, #e5a820);
    color: #0a0e14;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    border: none;
    border-radius: 3px;
    padding: 10px 32px;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ffd970, #f7c948);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(247,201,72,0.3);
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #161b22;
    border: 1px dashed #30363d;
    border-radius: 4px;
}

/* ── Text areas ── */
textarea {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    background: #0d1117 !important;
    color: #a5d6ff !important;
    border: 1px solid #30363d !important;
}

/* ── Status ── */
.status-bar {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #8b949e;
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 3px;
    padding: 8px 14px;
    letter-spacing: 1px;
}

/* ── Divider ── */
hr { border-color: #21262d; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #f7c948 !important; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SUPPORTED_EXTENSIONS = [".vhd", ".vhdl", ".v", ".sv", ".txt", ".log"]
MODEL_ID = "llama3-70b-8192"
MAX_CHUNK_CHARS = 12000   # safe limit for context

# ─────────────────────────────────────────────
# SYSTEM PROMPT  (core prompt engineering)
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert FPGA synthesis and verification tool — equivalent to a senior RTL design engineer with deep knowledge of VHDL, Verilog, SystemVerilog, and industry synthesis tools (Xilinx Vivado, Intel Quartus Prime, Synopsys Design Compiler).

Your task is to statically analyze the provided HDL code or simulation/synthesis log and return a STRICT JSON response.

## Priority Analysis Areas
1. **LATCH INFERENCE**: Detect incomplete `if/else`, `case/when others` statements that cause unwanted latches in combinational processes.
2. **SENSITIVITY LIST**: Identify missing or incorrect signals in `process(...)` sensitivity lists (VHDL) or `always @(...)` blocks (Verilog).
3. **ASYNC RESET ERRORS**: Find improper asynchronous reset implementations (missing reset in sensitivity list, reset-clock mixing).
4. **CLOCK DOMAIN CROSSING (CDC)**: Flag signals crossing clock domains without proper synchronizers (double-FF, handshake, FIFO).
5. **COMBINATIONAL LOOPS**: Detect feedback paths in combinational logic that cause simulation/synthesis divergence.
6. **TIMING VIOLATIONS**: Parse synthesis logs for "Critical Warning", "Timing Violation", "Setup/Hold Slack" issues.
7. **IEEE COMPLIANCE**: Check coding style against IEEE Std 1076 (VHDL) / IEEE Std 1364/1800 (Verilog/SV).
8. **RESOURCE ESTIMATION**: Comment on potential resource over-utilization (redundant logic, deep combinational paths).

## Severity Classification
- **ERROR**: Will cause functional failure or synthesis failure. Must fix.
- **WARNING**: May cause issues in certain conditions. Should fix.
- **SUGGESTION**: Style, performance, or portability improvement.
- **INFO**: Informational observation about the design.

## MANDATORY Response Format
You MUST respond ONLY with valid JSON — no prose, no markdown fences, no explanation outside the JSON.

```json
{
  "summary": {
    "language": "VHDL | Verilog | SystemVerilog | Log File | Unknown",
    "total_issues": 0,
    "error_count": 0,
    "warning_count": 0,
    "suggestion_count": 0,
    "info_count": 0,
    "overall_health": "CRITICAL | POOR | FAIR | GOOD | EXCELLENT",
    "synopsis": "One sentence overall assessment."
  },
  "issues": [
    {
      "id": "ISSUE-001",
      "severity": "ERROR | WARNING | SUGGESTION | INFO",
      "category": "LATCH | SENSITIVITY_LIST | ASYNC_RESET | CDC | COMBO_LOOP | TIMING | IEEE | RESOURCE | OTHER",
      "title": "Short title",
      "description": "Detailed explanation of the problem.",
      "line_reference": "Line X or N/A",
      "code_snippet": "Offending code (max 5 lines)",
      "fix": "Explanation of the fix",
      "corrected_code": "Fixed code snippet or null"
    }
  ],
  "ieee_compliance": {
    "score": 0,
    "notes": "Brief IEEE compliance notes"
  }
}
```

If the input is a log file, focus on parsing WARNING/ERROR/CRITICAL lines.
If you find no issues, still return the JSON with empty issues array and EXCELLENT health.
Never truncate the JSON. Always close all brackets properly.
"""

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_api_key():
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    if not key:
        key = st.session_state.get("groq_api_key", "")
    return key


def groq_chat(api_key: str, system: str, user: str) -> str:
    """Call Groq REST API using only stdlib urllib — no external packages needed."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def chunk_code(code: str, max_chars: int = MAX_CHUNK_CHARS) -> list:
    """Split large code into overlapping chunks."""
    if len(code) <= max_chars:
        return [code]
    chunks = []
    step = max_chars - 500
    for i in range(0, len(code), step):
        chunks.append(code[i:i + max_chars])
    return chunks


def analyze_code(api_key: str, code: str, filename: str = "") -> dict:
    """Send code to Groq and return parsed JSON result."""
    chunks = chunk_code(code)
    all_issues = []
    summary = None
    ieee = None

    for idx, chunk in enumerate(chunks):
        chunk_label = f"[Chunk {idx+1}/{len(chunks)}]" if len(chunks) > 1 else ""
        user_msg = f"Analyze the following HDL code or log file. Filename: `{filename}` {chunk_label}\n\n```\n{chunk}\n```"

        raw = groq_chat(api_key, SYSTEM_PROMPT, user_msg).strip()

        # Strip markdown fences if model adds them
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {
                "summary": {
                    "language": "Unknown", "total_issues": 1,
                    "error_count": 0, "warning_count": 0,
                    "suggestion_count": 0, "info_count": 1,
                    "overall_health": "FAIR",
                    "synopsis": "Could not parse structured response."
                },
                "issues": [{
                    "id": "PARSE-ERR",
                    "severity": "INFO",
                    "category": "OTHER",
                    "title": "Raw AI Response",
                    "description": raw[:2000],
                    "line_reference": "N/A",
                    "code_snippet": "",
                    "fix": "",
                    "corrected_code": None
                }],
                "ieee_compliance": {"score": 0, "notes": "N/A"}
            }

        if summary is None:
            summary = data.get("summary", {})
            ieee = data.get("ieee_compliance", {})

        all_issues.extend(data.get("issues", []))

    if summary:
        summary["total_issues"]     = len(all_issues)
        summary["error_count"]      = sum(1 for i in all_issues if i.get("severity") == "ERROR")
        summary["warning_count"]    = sum(1 for i in all_issues if i.get("severity") == "WARNING")
        summary["suggestion_count"] = sum(1 for i in all_issues if i.get("severity") == "SUGGESTION")
        summary["info_count"]       = sum(1 for i in all_issues if i.get("severity") == "INFO")

    return {"summary": summary or {}, "issues": all_issues, "ieee_compliance": ieee or {}}


# ─────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────

SEVERITY_BADGE = {
    "ERROR":      ('<span class="badge badge-error">⛔ ERROR</span>', "card-error"),
    "WARNING":    ('<span class="badge badge-warning">⚠ WARNING</span>', "card-warning"),
    "SUGGESTION": ('<span class="badge badge-ok">💡 SUGGESTION</span>', "card-suggestion"),
    "INFO":       ('<span class="badge badge-info">ℹ INFO</span>', "card-info"),
}

HEALTH_COLOR = {
    "CRITICAL":  "#f85149",
    "POOR":      "#ff7b72",
    "FAIR":      "#f7c948",
    "GOOD":      "#3fb950",
    "EXCELLENT": "#56d364",
}


def render_issue_card(issue: dict):
    sev = issue.get("severity", "INFO")
    badge_html, card_class = SEVERITY_BADGE.get(sev, SEVERITY_BADGE["INFO"])
    cat = issue.get("category", "OTHER")
    title = issue.get("title", "Untitled")
    desc = issue.get("description", "")
    line_ref = issue.get("line_reference", "N/A")
    snippet = issue.get("code_snippet", "")
    fix = issue.get("fix", "")
    corrected = issue.get("corrected_code")
    issue_id = issue.get("id", "")

    snippet_html = f'<div class="code-block">{snippet}</div>' if snippet else ""
    corrected_html = f'<div class="code-block">{corrected}</div>' if corrected else ""

    fix_section = f"""
    <div style="margin-top:10px;padding:12px;background:#0d1117;border:1px solid #21262d;border-radius:3px;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#8b949e;letter-spacing:1px;margin-bottom:6px;">▸ RECOMMENDED FIX</div>
        <div style="font-size:0.85rem;color:#c9d1d9;">{fix}</div>
        {corrected_html}
    </div>
    """ if fix else ""

    st.markdown(f"""
    <div class="card {card_class}">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            {badge_html}
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#8b949e;">[{issue_id}]</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#58a6ff;">{cat}</span>
            <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#8b949e;margin-left:auto;">Line: {line_ref}</span>
        </div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;color:#e6edf3;margin-bottom:6px;">{title}</div>
        <div style="font-size:0.85rem;color:#8b949e;line-height:1.6;">{desc}</div>
        {snippet_html}
        {fix_section}
    </div>
    """, unsafe_allow_html=True)


def render_metric_row(summary: dict):
    health = summary.get("overall_health", "FAIR")
    color = HEALTH_COLOR.get(health, "#f7c948")
    e = summary.get("error_count", 0)
    w = summary.get("warning_count", 0)
    s = summary.get("suggestion_count", 0)
    i = summary.get("info_count", 0)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box" style="border-top: 3px solid {color};">
            <div class="num" style="color:{color};">{health}</div>
            <div class="lbl">Design Health</div>
        </div>
        <div class="metric-box" style="border-top: 3px solid #f85149;">
            <div class="num num-error">{e}</div>
            <div class="lbl">Errors</div>
        </div>
        <div class="metric-box" style="border-top: 3px solid #f7c948;">
            <div class="num num-warning">{w}</div>
            <div class="lbl">Warnings</div>
        </div>
        <div class="metric-box" style="border-top: 3px solid #3fb950;">
            <div class="num num-ok">{s}</div>
            <div class="lbl">Suggestions</div>
        </div>
        <div class="metric-box" style="border-top: 3px solid #58a6ff;">
            <div class="num num-info">{i}</div>
            <div class="lbl">Info</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ FPGA·AI ANALYZER")
    st.markdown("---")

    # API Key input
    st.markdown("**API CONFIGURATION**")
    api_input = st.text_input(
        "Groq API Key",
        value=st.session_state.get("groq_api_key", ""),
        type="password",
        placeholder="gsk_...",
        help="Get your free API key at console.groq.com"
    )
    if api_input:
        st.session_state["groq_api_key"] = api_input

    env_key = os.getenv("GROQ_API_KEY", "") or st.secrets.get("GROQ_API_KEY", "")
    if env_key:
        st.markdown('<div class="status-bar">✓ ENV KEY DETECTED</div>', unsafe_allow_html=True)
    elif api_input:
        st.markdown('<div class="status-bar">✓ KEY SET IN SESSION</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bar">✗ NO API KEY</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**MODEL**")
    st.markdown(f'<div class="status-bar">⬡ {MODEL_ID}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**DETECTION RULES**")
    rules = [
        "🔴 Latch Inference",
        "🟠 Sensitivity List",
        "🟡 Async Reset",
        "🔵 Clock Domain Crossing",
        "🔴 Combinational Loops",
        "🟠 Timing Violations",
        "🟢 IEEE Compliance",
        "🔵 Resource Estimation",
    ]
    for r in rules:
        st.markdown(f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.72rem;color:#8b949e;padding:3px 0;">{r}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**SUPPORTED FILES**")
    st.markdown('<div class="status-bar">.vhd .vhdl .v .sv .txt .log</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="fpga-header">
    <h1>⚡ FPGA · AI ANALYZER</h1>
    <p>STATIC RTL ANALYSIS ENGINE — POWERED BY GROQ LLM · LLAMA3-70B</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUT SECTION
# ─────────────────────────────────────────────

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("#### 📂 Upload HDL / Log File")
    uploaded_file = st.file_uploader(
        "Drop your file here",
        type=["vhd", "vhdl", "v", "sv", "txt", "log"],
        label_visibility="collapsed"
    )
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8", errors="replace")
        st.session_state["loaded_code"] = file_content
        st.session_state["loaded_filename"] = uploaded_file.name
        st.markdown(f'<div class="status-bar">✓ LOADED: {uploaded_file.name} ({len(file_content):,} chars)</div>', unsafe_allow_html=True)

with col2:
    st.markdown("#### ✏️ Or Paste Code Directly")
    manual_code = st.text_area(
        "Paste VHDL / Verilog / Log",
        height=160,
        placeholder="-- paste your VHDL / Verilog / synthesis log here...",
        label_visibility="collapsed",
        value=st.session_state.get("manual_code", ""),
    )
    if manual_code:
        st.session_state["manual_code"] = manual_code

# Determine active code
active_code = ""
active_filename = "manual_input.vhd"

if uploaded_file and st.session_state.get("loaded_code"):
    active_code = st.session_state["loaded_code"]
    active_filename = st.session_state.get("loaded_filename", "upload.vhd")
elif manual_code.strip():
    active_code = manual_code.strip()
    active_filename = "manual_input.vhd"

# ─────────────────────────────────────────────
# ANALYSE BUTTON
# ─────────────────────────────────────────────

st.markdown("")
run_col, _ = st.columns([1, 3])
with run_col:
    run_btn = st.button("⚡  RUN ANALYSIS")

# ─────────────────────────────────────────────
# ANALYSIS LOGIC
# ─────────────────────────────────────────────

if run_btn:
    api_key = get_api_key()
    if not api_key:
        st.error("🔑 No Groq API key found. Enter it in the sidebar or set GROQ_API_KEY env variable.")
    elif not active_code:
        st.warning("⚠ No code provided. Upload a file or paste code above.")
    else:
        with st.spinner("🔍 Analyzing HDL with Groq LLM..."):
            try:
                result = analyze_code(api_key, active_code, active_filename)
                st.session_state["analysis_result"] = result
            except Exception as exc:
                st.error(f"❌ Analysis failed: {exc}")

# ─────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────

if "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]
    summary = result.get("summary", {})
    issues  = result.get("issues", [])
    ieee    = result.get("ieee_compliance", {})

    st.markdown("---")
    st.markdown("### 📊 Analysis Results")

    # Synopsis card
    synopsis = summary.get("synopsis", "")
    lang     = summary.get("language", "Unknown")
    if synopsis:
        st.markdown(f"""
        <div class="card card-info" style="margin-bottom:20px;">
            <span class="badge badge-info">{lang}</span>&nbsp;&nbsp;
            <span style="font-size:0.9rem;color:#c9d1d9;">{synopsis}</span>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    render_metric_row(summary)

    # IEEE score
    ieee_score = ieee.get("score", 0)
    ieee_notes = ieee.get("notes", "")
    if ieee_score or ieee_notes:
        bar_w = max(0, min(100, ieee_score))
        st.markdown(f"""
        <div class="card" style="margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-family:'Rajdhani',sans-serif;font-weight:600;font-size:1rem;color:#e6edf3;">IEEE Compliance Score</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:1rem;color:#58a6ff;">{ieee_score}/100</span>
            </div>
            <div style="height:6px;background:#21262d;border-radius:3px;overflow:hidden;">
                <div style="height:100%;width:{bar_w}%;background:linear-gradient(90deg,#1f6feb,#58a6ff);border-radius:3px;"></div>
            </div>
            <div style="font-size:0.82rem;color:#8b949e;margin-top:8px;">{ieee_notes}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──
    errors      = [i for i in issues if i.get("severity") == "ERROR"]
    warnings    = [i for i in issues if i.get("severity") == "WARNING"]
    suggestions = [i for i in issues if i.get("severity") == "SUGGESTION"]
    infos       = [i for i in issues if i.get("severity") == "INFO"]

    tab_labels = [
        f"⛔ Errors ({len(errors)})",
        f"⚠ Warnings ({len(warnings)})",
        f"💡 Suggestions ({len(suggestions)})",
        f"ℹ Info ({len(infos)})",
        "📄 Raw JSON",
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        if errors:
            for issue in errors:
                render_issue_card(issue)
        else:
            st.markdown('<div class="card card-suggestion"><span style="color:#3fb950;">✓ No errors detected.</span></div>', unsafe_allow_html=True)

    with tabs[1]:
        if warnings:
            for issue in warnings:
                render_issue_card(issue)
        else:
            st.markdown('<div class="card card-suggestion"><span style="color:#3fb950;">✓ No warnings detected.</span></div>', unsafe_allow_html=True)

    with tabs[2]:
        if suggestions:
            for issue in suggestions:
                render_issue_card(issue)
        else:
            st.markdown('<div class="card card-info"><span style="color:#58a6ff;">No suggestions.</span></div>', unsafe_allow_html=True)

    with tabs[3]:
        if infos:
            for issue in infos:
                render_issue_card(issue)
        else:
            st.markdown('<div class="card card-info"><span style="color:#58a6ff;">No informational notes.</span></div>', unsafe_allow_html=True)

    with tabs[4]:
        st.json(result)

    # Download button
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇  Download JSON Report",
        data=json_str,
        file_name=f"fpga_analysis_{active_filename}.json",
        mime="application/json",
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-family:'Share Tech Mono',monospace;font-size:0.65rem;
            color:#484f58;letter-spacing:2px;padding:10px 0;">
FPGA·AI ANALYZER · GROQ LLM BACKEND · LLAMA3-70B · FOR ENGINEERING USE ONLY
</div>
""", unsafe_allow_html=True)
