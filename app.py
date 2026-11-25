"""Interactive Streamlit demo for DocSentinel."""
from __future__ import annotations
import html, json
import streamlit as st
from docsentinel.demo import run_demo
from docsentinel.verifier import verify_payload

st.set_page_config(page_title="DocSentinel | Evidence QA", page_icon="◈", layout="wide")
st.markdown("""<style>
.stApp{background:#0b1020;color:#e8edf8}[data-testid="stHeader"]{background:rgba(11,16,32,.85)}[data-testid="stSidebar"]{background:#10182b}
.hero{padding:1.25rem 1.5rem;border:1px solid #263653;border-radius:18px;background:linear-gradient(120deg,#14233d,#10182b);margin-bottom:1rem}
.eyebrow{color:#83b7ff;letter-spacing:.16em;font-size:.72rem;font-weight:700}.hero h1{margin:.25rem 0;color:#f4f7ff;font-size:2.15rem}.hero p{color:#b9c6dc;margin:0}
.panel{border:1px solid #263653;border-radius:14px;padding:1rem 1.1rem;background:#111b2e;margin:.5rem 0}
.tag{display:inline-block;border-radius:999px;padding:.22rem .65rem;font-size:.72rem;font-weight:700;letter-spacing:.04em}.good{color:#8ce0bd;background:#153a35}.bad{color:#ffb3a8;background:#482723}
.muted{color:#9eacc4;font-size:.86rem}.quote{border-left:3px solid #6ea8fe;padding:.65rem .8rem;background:#0c1527;border-radius:0 8px 8px 0;color:#dce8ff;font-family:ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere}
div[data-testid="stMetric"]{background:#111b2e;border:1px solid #263653;border-radius:12px;padding:.8rem 1rem}.stButton button[kind="primary"]{background:#3978d4;border:0}
</style>""",unsafe_allow_html=True)
st.markdown("""<div class="hero"><div class="eyebrow">EVIDENCE-FIRST DOCUMENT QA</div><h1>DocSentinel</h1><p>Inspect whether each generated claim can be traced to the exact source passage it cites.</p></div>""",unsafe_allow_html=True)

SAMPLES={
"Mixed evidence · recommended demo":run_demo(),
"Clean citations · should pass L1":{
"question":"When does the agreement terminate?",
"chunks":[{"chunk_id":"contract::p4::c1","text":"The agreement shall terminate on 31 December 2027 unless renewed in writing."},{"chunk_id":"contract::p7::c2","text":"Any renewal must be agreed by both parties in a signed written instrument."}],
"claims":[{"text":"The agreement terminates on 31 December 2027.","chunk_id":"contract::p4::c1","quote":"The agreement shall terminate on 31 December 2027"},{"text":"Renewal requires a signed written agreement.","chunk_id":"contract::p7::c2","quote":"Any renewal must be agreed by both parties in a signed written instrument."}]},
"Adversarial citation · should abstain":{
"question":"What is the renewal period?",
"chunks":[{"chunk_id":"policy::p2::c1","text":"The subscription renews annually unless cancelled at least 30 days before the renewal date."},{"chunk_id":"policy::p5::c2","text":"A cancellation request must be submitted through the account portal."}],
"claims":[{"text":"The subscription renews every month.","chunk_id":"policy::p2::c1","quote":"The subscription renews monthly."},{"text":"Cancellation must be submitted through the account portal.","chunk_id":"policy::p2::c1","quote":"A cancellation request must be submitted through the account portal."}]}}
if "payload_editor" not in st.session_state:
 st.session_state.payload_editor=json.dumps(SAMPLES["Mixed evidence · recommended demo"],indent=2)
with st.sidebar:
 st.markdown("### Demo controls")
 st.caption("Choose a scenario, or provide your own structured answer.")
 selected=st.selectbox("Example scenario",list(SAMPLES.keys()))
 if st.button("Load example",use_container_width=True):
  st.session_state.payload_editor=json.dumps(SAMPLES[selected],indent=2)
 uploaded=st.file_uploader("Upload a JSON payload",type=["json"])
 if uploaded is not None:
  try:
   st.session_state.payload_editor=json.dumps(json.loads(uploaded.getvalue()),indent=2)
   st.success("JSON loaded into the editor.")
  except (UnicodeDecodeError,json.JSONDecodeError):
   st.error("That file is not valid UTF-8 JSON.")
 st.markdown("---")
 st.markdown("**Verification scope**")
 st.caption("L1 checks exact quote existence and chunk provenance after conservative text normalization.")
 st.caption("It does not evaluate semantic entailment, factual truth, or whether a quote logically supports a claim.")
left,right=st.columns([1.05,.95],gap="large")
with left:
 st.markdown("### 1 · Input")
 st.caption("Edit the claim-level answer and retrieved evidence below.")
 payload_text=st.text_area("JSON payload",key="payload_editor",height=410,label_visibility="collapsed")
 run_clicked=st.button("Run evidence verification",type="primary",use_container_width=True)
with right:
 st.markdown("### 2 · How to read the result")
 st.markdown("""<div class="panel"><span class="tag good">QUOTE_VERIFIED</span><p class="muted">The quote exists in the chunk the claim cites. Provenance only; not semantic proof.</p></div><div class="panel"><span class="tag bad">MISATTRIBUTED</span><p class="muted">The quote exists in another retrieved chunk, not the cited one.</p></div><div class="panel"><span class="tag bad">QUOTE_NOT_FOUND</span><p class="muted">The quote was not found in any retrieved chunk.</p></div><div class="panel"><span class="tag bad">UNATTRIBUTED</span><p class="muted">The claim is missing a usable quote or source chunk ID.</p></div>""",unsafe_allow_html=True)
 st.info("Conservative policy: the answer is returned only when every claim passes L1 provenance verification. Otherwise DocSentinel abstains.")
if run_clicked:
 try:
  payload=json.loads(payload_text)
  st.session_state["last_report"]=verify_payload(payload)
  st.session_state["last_payload"]=payload
 except json.JSONDecodeError as exc: st.error(f"Invalid JSON: {exc}")
 except (ValueError,TypeError,KeyError) as exc: st.error(f"Invalid payload: {exc}")
report=st.session_state.get("last_report")
payload=st.session_state.get("last_payload")
if report is not None and payload is not None:
 st.markdown("---")
 st.markdown("### 3 · Verification report")
 m1,m2,m3=st.columns(3)
 m1.metric("Claims checked",report["claim_count"])
 m2.metric("Quotes found in cited chunk",report["verified_claim_count"])
 m3.metric("Decision","RETURN" if not report["abstained"] else "ABSTAIN")
 if report["abstained"]: st.error("ABSTAIN — at least one claim failed the required provenance check.")
 else: st.success("RETURN WITH PROVENANCE — every claim passed the L1 quote-existence check.")
 st.caption(report["verification_scope"])
 chunks={chunk["chunk_id"]:chunk["text"] for chunk in payload.get("chunks",[])}
 for index,result in enumerate(report["claims"],start=1):
  verdict=result["verdict"]
  badge_class="good" if verdict=="QUOTE_VERIFIED" else "bad"
  with st.expander(f"Claim {index} · {verdict}",expanded=True):
   st.markdown(f"**Claim**  \n{result.get('claim','')}")
   st.markdown(f'<span class="tag {badge_class}">{html.escape(verdict)}</span>',unsafe_allow_html=True)
   st.markdown(f"**Cited chunk:** <code>{html.escape(str(result.get('cited_chunk_id')))}</code>",unsafe_allow_html=True)
   st.markdown(f"**Verifier note:** {result.get('detail','')}")
   quote=result.get("quote")
   if quote:
    st.markdown("**Submitted quote**")
    st.markdown(f'<div class="quote">{html.escape(str(quote))}</div>',unsafe_allow_html=True)
   matched_id=result.get("matched_chunk_id")
   if matched_id and matched_id in chunks:
    st.markdown(f"**Matched source · <code>{html.escape(matched_id)}</code>**",unsafe_allow_html=True)
    st.markdown(f'<div class="quote">{html.escape(chunks[matched_id])}</div>',unsafe_allow_html=True)
   elif result.get("cited_chunk_id") in chunks:
    cited=result["cited_chunk_id"]
    st.markdown(f"**Cited source · <code>{html.escape(cited)}</code>**",unsafe_allow_html=True)
    st.markdown(f'<div class="quote">{html.escape(chunks[cited])}</div>',unsafe_allow_html=True)
 with st.expander("View raw audit JSON"): st.json(report)
