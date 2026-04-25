import streamlit as st
import base64
import json
import datetime
import requests
from dotenv import load_dotenv

import time

def safe_post(url, **kwargs):
    for i in range(3):
        try:
            return requests.post(url, timeout=120, **kwargs)
        except requests.exceptions.RequestException:
            time.sleep(20)
    raise Exception("n8n not reachable")

load_dotenv()

def ensure_dict(data):
    import json
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return {}
    return data if isinstance(data, dict) else {}
# ══════════════════════════════════════════════════════════════════════════════
# n8n ENDPOINT CONFIG
# ══════════════════════════════════════════════════════════════════════════════
N8N_BASE = "https://n8n-production-8bc4.up.railway.app"

PROCESS_PDF_URL   = f"{N8N_BASE}/webhook/process-pdf"
ASK_QUESTION_URL  = f"{N8N_BASE}/webhook/ask-question"
SUMMARISE_URL     = f"{N8N_BASE}/webhook/summarise"

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="InsightPDF Pro",
    layout="wide",
    page_icon="📑",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

:root {
  --bg:       #0A0B0F;
  --surface:  #13151C;
  --surface2: #1A1D27;
  --border:   #252836;
  --accent:   #F0A500;
  --accent2:  #3D8EFF;
  --n8n:      #FF6B9D;
  --text:     #E9ECF5;
  --muted:    #6B7394;
  --success:  #3ECFB2;
  --danger:   #FF5C5C;
  --radius:   10px;
}

[data-theme="dark"] .stApp {
  background: var(--bg) !important;
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--text); }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.8rem !important; max-width: 100% !important }

/* ── Sidebar ── */
[data-theme="dark"] section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border);
}
  

section[data-testid="stSidebar"] * { color: var(--text); }
button[kind="header"] svg {
    color: white !important;
}
/* ── Brand ── */
.brand { display:flex; align-items:center; gap:12px; padding:.4rem 0 1.4rem; }
.brand-icon {
  width:40px; height:40px; border-radius:10px;
  background: linear-gradient(135deg, var(--accent), #c47f00);
  display:flex; align-items:center; justify-content:center; font-size:1.25rem;
}
.brand-name { font-family:'DM Serif Display',serif; font-size:1.35rem; line-height:1; }
.brand-tag  { font-size:.65rem; color:var(--muted) !important; letter-spacing:.1em; text-transform:uppercase; margin-top:2px; }

/* ── Section labels ── */
.slabel {
  font-size:.65rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--muted); margin:1.3rem 0 .45rem; font-weight:600;
}

/* ── Pill badges ── */
.pill {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:20px; font-size:.7rem; font-weight:500;
}
.pill-ready   { background:rgba(62,207,178,.1);  color:var(--success); border:1px solid rgba(62,207,178,.25); }
.pill-empty   { background:rgba(107,115,148,.08); color:var(--muted);   border:1px solid var(--border); }
.pill-n8n     { background:rgba(255,107,157,.1);  color:var(--n8n);     border:1px solid rgba(255,107,157,.3); }
.pill-dot     { width:6px; height:6px; border-radius:50%; }
.dot-on       { background:var(--success); animation:blink 2s infinite; }
.dot-n8n      { background:var(--n8n);    animation:blink 2s infinite; }
.dot-off      { background:var(--muted); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── Buttons ── */
.stButton > button {
  background: var(--accent) !important;
  color: #0A0B0F !important;
  border: none !important;
  border-radius: var(--radius) !important;
  font-weight: 600 !important;
  font-size: .85rem !important;
  padding: .5rem 1rem !important;
  width: 100%;
  letter-spacing: .01em;
  transition: opacity .18s, transform .14s !important;
}
.stButton > button:hover { opacity: .85 !important; transform: translateY(-1px) !important; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea textarea {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-size: .9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(240,165,0,.12) !important;
}

/* ── Chat ── */
div[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1rem 1.25rem !important;
  margin-bottom: .7rem !important;
}
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] span { color: var(--text) !important; }
div[data-testid="stChatInput"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
div[data-testid="stChatInput"] textarea { color: var(--text) !important; background: transparent !important; }

/* ── Expander ── */
.stExpander {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
}
.stExpander summary { color: var(--muted) !important; font-size: .8rem !important; }
.stExpander p, .stExpander span { color: var(--text) !important; font-size: .82rem !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: var(--surface2) !important;
  border: 1.5px dashed var(--border) !important;
  border-radius: var(--radius) !important;
}

/* ── Source card ── */
.src-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: .65rem .95rem;
  margin-bottom: .45rem;
  font-size: .8rem;
}
.src-card .sh { color: var(--accent); font-weight: 600; margin-bottom: 3px; }
.src-card .sb { color: var(--muted); line-height: 1.55; }

/* ── n8n step card ── */
.step-card {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .9rem 1.1rem;
  margin-bottom: .6rem;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.step-num {
  min-width: 28px; height: 28px;
  background: rgba(255,107,157,.12);
  border: 1px solid rgba(255,107,157,.3);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 700; color: var(--n8n);
}
.step-body .st { font-size: .85rem; font-weight: 600; color: var(--text); margin-bottom: 2px; }
.step-body .sd { font-size: .78rem; color: var(--muted); line-height: 1.5; }

/* ── Pipeline flow ── */
.flow-box {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.2rem;
  margin-bottom: .5rem;
  font-size: .82rem;
}
.flow-box .fl { color: var(--n8n); font-weight: 700; font-size: .7rem;
  letter-spacing: .1em; text-transform: uppercase; margin-bottom: 4px; }
.flow-box .fd { color: var(--text); }
.flow-arrow { text-align:center; color: var(--muted); font-size:1.1rem; margin:.15rem 0; }

/* ── Stat row ── */
.stat-row { display:flex; gap:8px; margin-bottom:1rem; }
.stat-box {
  flex:1; background:var(--surface2); border:1px solid var(--border);
  border-radius:8px; padding:.55rem .75rem; text-align:center;
}
.stat-v { font-size:1.15rem; font-weight:700; color:var(--accent); font-family:'DM Serif Display',serif; }
.stat-l { font-size:.62rem; color:var(--muted); text-transform:uppercase; letter-spacing:.08em; }

/* ── Page header ── */
.page-hdr { padding-bottom:.9rem; border-bottom:1px solid var(--border); margin-bottom:1.4rem; }
.page-ttl { font-family:'DM Serif Display',serif; font-size:1.85rem; color: inherit; margin:0; }
.page-sub { font-size:.8rem; color:var(--muted); margin-top:3px; }

.divider { border:none; border-top:1px solid var(--border); margin:.9rem 0; }

/* ── Processing indicator ── */
.proc-badge {
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(255,107,157,.08); border:1px solid rgba(255,107,157,.2);
  border-radius:8px; padding:.5rem .9rem; font-size:.8rem; color:var(--n8n);
  margin-bottom:.8rem;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {
    "chunks":       [],    # list of {text, source, page} returned by n8n
    "doc_meta":     [],    # [{name, pages, chunk_count}]
    "chat_history": [],    # [(question, answer, sources)]
    "proc_log":     [],    # processing event log
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# n8n API CALLS  —  these are the REAL integration points
# ══════════════════════════════════════════════════════════════════════════════

def call_n8n_process_pdf(pdf_name: str, pdf_bytes: bytes) -> dict:
# Better Render warmup
    import time
    print("🌡 Warming up Render server...")
    for warmup_attempt in range(3):
        try:
            r = requests.get(N8N_BASE, timeout=15)
            if r.status_code < 500:
                print(f"✅ Server awake after {warmup_attempt+1} attempts")
                break
        except:
            print(f"⏳ Warmup attempt {warmup_attempt+1} failed, waiting...")
            time.sleep(15)  # Give Render 15s between checks

    time.sleep(20)  # Extra buffer after warmup
def call_n8n_ask_question(question: str, chunks: list, history: list) -> dict:
    payload = {
        "event": "ask_question",
        "question": question,
        "chunks": chunks,
        "history": history,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    resp = safe_post(ASK_QUESTION_URL, json=payload, timeout=60)
    resp.raise_for_status()

    # 🔥 FIX: Safe JSON parsing
    try:
        data = resp.json()
    except:
        data = json.loads(resp.text)

    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return {}
    return data


def call_n8n_summarise(chunks: list, doc_meta: list) -> dict:
    if not chunks:
        return {"summary": "No chunks available. Please process documents first."}

    chunks = chunks[:30]
    print("CHUNKS BEING SENT")
    print("Total chunks:", len(chunks))
    if chunks:
        print("First chunk source:", chunks[0].get('source','?'))
        print("First chunk text:", chunks[0].get('text','')[:150])
    print("==========================")
    payload = {
        "event": "summarise",
        "chunks": chunks,
        "documents": doc_meta,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    resp = safe_post(SUMMARISE_URL, json=payload, timeout=120)
    resp.raise_for_status()

    # 🔥 FIX: Safe JSON parsing
    if not resp.text.strip():
        return {"summary": "n8n returned an empty response. Check your summarise workflow is active and returning data."}
    try:
        data = resp.json()
    except:
        return {"summary": f"Non-JSON response from n8n: {resp.text[:300]}"}
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0] 
    if isinstance(data, str):
        try:
          data = json.loads(data)
        except:
            return {"summary": data}
        
    data = ensure_dict(data)
    print("SUMMARISE RAW RESPONSE")
    print( json.dumps(data, indent=2))
    print("END RESPONSE")
    summary = (
        data.get("summary") or
        data.get("output") or
        data.get("text") or
        data.get("result") or
        data.get("message") or
        "n8n returned no summary. Keys received: " +str(list(data.keys()))
    )
    return {"summary": summary}


def log_event(label: str, status: str, msg: str = ""):
    st.session_state.proc_log.append({
        "time":   datetime.datetime.now().strftime("%H:%M:%S"),
        "label":  label,
        "status": status,
        "msg":    msg,
    })

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">📑</div>
      <div>
        <div class="brand-name">InsightPDF</div>
        <div class="brand-tag">AI Document Assistant · Powered by n8n</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── n8n Connection Check ──
    def check_n8n():
        try:
            requests.get(N8N_BASE, timeout=3)
            return True   
        except:
            return False

    # ── n8n Status Indicator ──
    n8n_status = check_n8n()

    if n8n_status:
        st.markdown("""
        <div class="pill pill-n8n" style="margin-top:6px">
          <div class="pill-dot dot-n8n"></div>
          n8n Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pill pill-empty" style="margin-top:6px">
          <div class="pill-dot dot-off"></div>
          n8n Offline
        </div>
        """, unsafe_allow_html=True)


    # ── Doc status ──
    if st.session_state.chunks:
        st.markdown(f"""
        <div class="pill pill-ready" style="margin-top:6px">
          <div class="pill-dot dot-on"></div>
          {len(st.session_state.doc_meta)} doc(s) · {len(st.session_state.chunks)} chunks
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pill pill-empty" style="margin-top:6px">
          <div class="pill-dot dot-off"></div>
          No documents loaded
        </div>""", unsafe_allow_html=True)

    # ── Upload ──
    st.markdown('<div class="slabel">Upload Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "PDFs", type=["pdf"], accept_multiple_files=True,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Process Documents", use_container_width=True):
            if not uploaded_files:
                st.warning("Upload at least one PDF.")
            else:
                all_chunks = []
                all_meta   = []
                errors     = []

                prog = st.progress(0, text="Sending to n8n…")
                for i, pdf in enumerate(uploaded_files):
                    prog.progress((i+1) / len(uploaded_files), text=f"n8n processing {pdf.name}…")
                    try:
                        pdf_bytes = pdf.read()
                        
                        # ── REAL n8n call: PDF → text extraction + chunking ──
                        result = call_n8n_process_pdf(pdf.name, pdf_bytes)
                        
                        result = ensure_dict(result)
                        chunks = result.get("chunks") or []
                        all_chunks.extend(chunks)
                        all_meta.append({
                            "name":        pdf.name,
                            "pages":       result.get("pages", "?"),
                            "chunk_count": len(chunks),
                        })
                        log_event(f"📄 {pdf.name}", "ok", f"{len(chunks)} chunks extracted")

                    except requests.exceptions.ConnectionError:
                        errors.append(pdf.name)
                        log_event(f"📄 {pdf.name}", "error", "Cannot reach n8n — is it running?")
                    except Exception as e:
                        errors.append(pdf.name)
                        log_event(f"📄 {pdf.name}", "error", str(e)[:100])

                prog.empty()

                if all_chunks:
                    st.session_state.chunks   = all_chunks
                    st.session_state.doc_meta = all_meta
                    st.success(f"✓ {len(all_chunks)} chunks ready")
                if errors:
                    st.error(f"Failed: {', '.join(errors)}")

    with col2:
        if st.button("🗑 Reset Workspace", use_container_width=True):
            for k in ["chunks", "doc_meta", "chat_history", "proc_log"]:
                st.session_state[k] = []
            st.rerun()

    # ── Loaded files ──
    if st.session_state.doc_meta:
        st.markdown('<div class="slabel">Loaded Files</div>', unsafe_allow_html=True)
        for m in st.session_state.doc_meta:
            name = m["name"][:26] + ("…" if len(m["name"]) > 26 else "")
            st.markdown(f"""
            <div style="font-size:.76rem;padding:.4rem .6rem;background:var(--surface2);
                        border-radius:7px;margin-bottom:4px;border:1px solid var(--border)">
              <span style="color:var(--accent);font-weight:600">{name}</span><br>
              <span style="color:var(--muted)">{m['pages']} pages · {m['chunk_count']} chunks (via n8n)</span>
            </div>""", unsafe_allow_html=True)

    # ── Stats ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-box">
        <div class="stat-v">{len(st.session_state.chat_history)}</div>
        <div class="stat-l">Queries</div>
      </div>
      <div class="stat-box">
        <div class="stat-v">{len(st.session_state.proc_log)}</div>
        <div class="stat-l">n8n Calls</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="page-hdr">
  <div class="page-ttl">InsightPDF Pro</div>
  <div class="page-sub">AI Document Intelligence System · Context-aware Q&A · Summarisation via n8n</div>
</div>
""", unsafe_allow_html=True)

tab_chat, tab_summary, tab_pipeline, tab_log = st.tabs([
    "💬 Ask Questions", "📋 Document Summary", "⚡ Workflow Pipeline", "📋 System Logs"
])

# ── TAB 1 : CHAT ──────────────────────────────────────────────────────────────
with tab_chat:
    if not st.session_state.chunks:
        st.info("👈 Upload PDFs in the sidebar and click **⚡ Process** — n8n will handle all the extraction.")
    else:
        # Show history
        for q, a, srcs in st.session_state.chat_history:
            with st.chat_message("user", avatar="👤"):
                st.markdown(q)
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(a)
                if srcs:
                    with st.expander("📍 Sources", expanded=False):
                        for s in srcs:
                            if isinstance(s, str):
                                try:
                                    s = json.loads(s)
                                except:
                                    s = {}
                            st.markdown(f"""
                            <div class="src-card">
                              <div class="sh">📄 {s.get('source','?')} — Page {s.get('page','?')}</div>
                              <div class="sb">{s.get('snippet','')}</div>
                            </div>""", unsafe_allow_html=True)

        if question := st.chat_input("Ask anything about your documents (context-aware AI)…"):
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown('<div class="proc-badge">⚡ Sending to n8n for AI processing…</div>',
                            unsafe_allow_html=True)
                with st.spinner(""):
                    try:
                        # Prepare condensed history for context
                        history_ctx = [
                            {"q": q, "a": a}
                            for q, a, _ in st.session_state.chat_history[-3:]
                        ]
                        # ── REAL n8n call: question + chunks → Gemini answer ──
                        result  = call_n8n_ask_question(
                            question,
                            st.session_state.chunks,
                            history_ctx
                        )
                        result = ensure_dict(result)

                        answer  = result.get("answer", "❌ n8n returned no answer.")
                        sources = result.get("sources", [])
                        clean_sources = []
                        for s in sources:
                            if isinstance(s,str):
                                try:
                                    s = json.loads(s)
                                except:
                                    continue
                            if isinstance(s,dict):
                                clean_sources.append(s)
                        sources = clean_sources
                        log_event("💬 Q&A", "ok", f"Q: {question[:60]}…")

                    except requests.exceptions.ConnectionError:
                        answer  = "❌ Cannot reach n8n. Make sure your n8n workflow is running and the webhook is active."
                        sources = []
                        log_event("💬 Q&A", "error", "Connection refused")
                    except Exception as e:
                        answer  = f"❌ n8n error: {e}"
                        sources = []
                        log_event("💬 Q&A", "error", str(e)[:100])

                st.markdown(answer)
                if sources:
                    with st.expander("📍 Sources", expanded=False):
                        for s in sources:
                            if isinstance(s, str):
                                try:
                                    s = json.loads(s)
                                except:
                                    s = {}
                            st.markdown(f"""
                            <div class="src-card">
                              <div class="sh">📄 {s.get('source','?')} — Page {s.get('page','?')}</div>
                              <div class="sb">{s.get('snippet','')}</div>
                            </div>""", unsafe_allow_html=True)

                st.session_state.chat_history.append((question, answer, sources))

# ── TAB 2 : SUMMARY ───────────────────────────────────────────────────────────
with tab_summary:
    if not st.session_state.chunks:
        st.info("👈 Load documents first.")
    else:
        st.markdown("AI will analyze your documents and generate a structured summary using the workflow pipeline.")
        if st.button("✨ Generate Summary via n8n"):
            st.markdown('<div class="proc-badge">⚡ n8n is summarising your documents…</div>',
                        unsafe_allow_html=True)
            with st.spinner(""):
                try:
                    # ── REAL n8n call: chunks → Gemini summary ──
                    result  = call_n8n_summarise(
                        st.session_state.chunks,
                        st.session_state.doc_meta
                    )
                    result = ensure_dict(result)
                    
                    summary = result.get("summary", "❌ n8n returned no summary.")
                    log_event("📋 Summary", "ok", "Summary generated")
                except requests.exceptions.ConnectionError:
                    summary = "❌ Cannot reach n8n. Make sure your workflow is active."
                    log_event("📋 Summary", "error", "Connection refused")
                except Exception as e:
                    summary = f"❌ n8n error: {e}"
                    log_event("📋 Summary", "error", str(e)[:100])

            st.markdown(summary)
            st.download_button("⬇ Download Summary", data=summary,
                               file_name="summary.md", mime="text/markdown")

# ── TAB 3 : PIPELINE EXPLAINER ────────────────────────────────────────────────
with tab_pipeline:
    st.markdown("### ⚡ How the n8n Pipeline Works")
    st.markdown("Each action in this app triggers a real n8n workflow — here's what happens inside:")

    st.markdown("#### 📤 When you click **Process PDF**")
    for i, step in enumerate([
        ("Receive PDF",       "Streamlit base64-encodes the PDF and POSTs it to n8n's `/webhook/process-pdf`"),
        ("Extract Text",      "n8n uses the **Extract from File** node to pull raw text from every page of the PDF"),
        ("Clean & Chunk",     "n8n's **Code** node splits the text into overlapping chunks of ~1000 characters"),
        ("Tag Metadata",      "Each chunk is tagged with `source` (filename) and `page` number"),
        ("Return to App",     "n8n responds with all chunks as JSON — Streamlit stores them in session state"),
    ]):
        st.markdown(f"""
        <div class="step-card">
          <div class="step-num">{i+1}</div>
          <div class="step-body">
            <div class="st">{step[0]}</div>
            <div class="sd">{step[1]}</div>
          </div>
        </div>""".replace("{_+1}", str(i+1)), unsafe_allow_html=True)
        # note: using enumerate below instead
    # re-render properly
    steps_pdf = [
        ("Receive PDF",   "Streamlit base64-encodes the PDF and POSTs it to n8n `/webhook/process-pdf`"),
        ("Extract Text",  "n8n Extract from File node pulls raw text from every page"),
        ("Chunk Text",    "n8n Code node splits text into ~1000-char overlapping chunks"),
        ("Tag Metadata",  "Each chunk gets tagged with filename and page number"),
        ("Return Chunks", "n8n responds with all chunks as JSON → stored in Streamlit session"),
    ]

    st.markdown("#### 💬 When you ask a **Question**")
    steps_qa = [
        ("Receive Question",   "Streamlit POSTs the question + all stored chunks to n8n `/webhook/ask-question`"),
        ("Similarity Search",  "n8n Code node scores each chunk against the question using keyword/cosine logic"),
        ("Build Prompt",       "Top 4 relevant chunks are assembled into a Gemini prompt with chat history"),
        ("Call Gemini AI",     "n8n HTTP Request node calls the Gemini API and gets the answer"),
        ("Return Answer",      "n8n sends back the answer + source citations → Streamlit displays them"),
    ]
    for i, (title, desc) in enumerate(steps_qa, 1):
        st.markdown(f"""
        <div class="step-card">
          <div class="step-num">{i}</div>
          <div class="step-body">
            <div class="st">{title}</div>
            <div class="sd">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("#### 📋 When you generate a **Summary**")
    steps_sum = [
        ("Receive Chunks",    "Streamlit POSTs all stored chunks to n8n `/webhook/summarise`"),
        ("Select Key Chunks", "n8n picks the most representative chunks from intro, body, and conclusion sections"),
        ("Summarise",         "n8n calls Gemini with a structured summary prompt"),
        ("Return Summary",    "n8n sends back the formatted markdown summary"),
    ]
    for i, (title, desc) in enumerate(steps_sum, 1):
        st.markdown(f"""
        <div class="step-card">
          <div class="step-num">{i}</div>
          <div class="step-body">
            <div class="st">{title}</div>
            <div class="sd">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔧 n8n Webhook Endpoints Expected")
    st.code(f"""
# Set these in your .env file
N8N_BASE_URL       = {N8N_BASE}

POST {PROCESS_PDF_URL}
  Body: {{ "filename": "doc.pdf", "pdf_b64": "<base64>", "event": "process_pdf" }}
  Returns: {{ "status": "ok", "pages": 12, "chunks": [...] }}

POST {ASK_QUESTION_URL}
  Body: {{ "question": "...", "chunks": [...], "history": [...] }}
  Returns: {{ "status": "ok", "answer": "...", "sources": [...] }}

POST {SUMMARISE_URL}
  Body: {{ "chunks": [...], "documents": [...] }}
  Returns: {{ "status": "ok", "summary": "## Overview..." }}
""", language="text")

# ── TAB 4 : PROCESS LOG ───────────────────────────────────────────────────────
with tab_log:
    st.markdown("### 📋 n8n Processing Log")
    st.caption("Every call made to n8n this session.")

    if not st.session_state.proc_log:
        st.info("No calls yet — process a PDF or ask a question.")
    else:
        for entry in reversed(st.session_state.proc_log):
            color   = "var(--success)" if entry["status"] == "ok" else "var(--danger)"
            icon    = "✓" if entry["status"] == "ok" else "✗"
            st.markdown(f"""
            <div style="background:var(--surface2);border:1px solid var(--border);
                        border-left:3px solid {color};border-radius:8px;
                        padding:.55rem .9rem;margin-bottom:.4rem;font-size:.79rem;
                        display:flex;gap:12px;align-items:center">
              <span style="color:var(--muted)">{entry['time']}</span>
              <span style="font-weight:600;color:var(--text)">{entry['label']}</span>
              <span style="color:{color}">{icon} {entry['msg']}</span>
            </div>""", unsafe_allow_html=True)
