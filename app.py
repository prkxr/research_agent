import time

import streamlit as st

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ---------------------------------------------------------------- page setup
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2.2rem; max-width: 1100px;}
        .hero-title {font-size: 2.4rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0;}
        .hero-sub {color: #8b8fa3; font-size: 1.05rem; margin-top: 0.25rem; margin-bottom: 1.5rem;}
        .step-pill {
            display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 0.78rem; font-weight: 600; margin-right: 6px;
            background: rgba(124,92,255,0.15); color: #7c5cff;
        }
        div[data-testid="stMetric"] {
            background: rgba(128,128,128,0.08); border-radius: 12px; padding: 12px 16px;
        }
        .stButton > button[kind="primary"] {border-radius: 10px; font-weight: 600; height: 2.9rem;}
        .stTextInput input {border-radius: 10px; height: 2.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

STEPS = [
    ("Search", "Finds recent, reliable sources"),
    ("Read", "Scrapes the best source in depth"),
    ("Write", "Drafts the research report"),
    ("Critique", "Reviews the report for quality"),
]

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### 🔎 Research Agent")
    st.caption("A multi-agent research system")
    st.divider()
    st.markdown("**Pipeline**")
    for i, (name, desc) in enumerate(STEPS, 1):
        st.markdown(f"<span class='step-pill'>{i}</span>**{name}** — {desc}", unsafe_allow_html=True)
    st.divider()
    if st.button("Clear results", use_container_width=True):
        st.session_state.pop("result", None)
        st.rerun()


# ---------------------------------------------------------------- pipeline
def run_pipeline_ui(topic: str) -> dict:
    """Same logic as pipeline.run_research_pipeline, but reports progress to the UI."""
    state, timings = {}, {}
    progress = st.progress(0, text="Starting…")

    # Step 1 - search
    with st.status("Step 1 · Search agent is working…", expanded=False) as status:
        t = time.time()
        search_agent = build_search_agent()
        res = search_agent.invoke(
            {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
        )
        state["search_results"] = res["messages"][-1].content
        timings["Search"] = time.time() - t
        status.update(label="Step 1 · Search complete", state="complete")
    progress.progress(25, text="Search done")

    # Step 2 - reader
    with st.status("Step 2 · Reader agent is scraping top resources…", expanded=False) as status:
        t = time.time()
        reader_agent = build_reader_agent()
        res = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = res["messages"][-1].content
        timings["Read"] = time.time() - t
        status.update(label="Step 2 · Scraping complete", state="complete")
    progress.progress(50, text="Reading done")

    # Step 3 - writer
    with st.status("Step 3 · Writer is drafting the report…", expanded=False) as status:
        t = time.time()
        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        timings["Write"] = time.time() - t
        status.update(label="Step 3 · Report drafted", state="complete")
    progress.progress(75, text="Draft ready")

    # Step 4 - critic
    with st.status("Step 4 · Critic is reviewing the report…", expanded=False) as status:
        t = time.time()
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        timings["Critique"] = time.time() - t
        status.update(label="Step 4 · Review complete", state="complete")
    progress.progress(100, text="All done")
    time.sleep(0.4)
    progress.empty()

    state["topic"] = topic
    state["timings"] = timings
    return state


def as_text(x) -> str:
    """Chain outputs may be str or a message object."""
    return x if isinstance(x, str) else getattr(x, "content", str(x))


# ---------------------------------------------------------------- main UI
st.markdown("<p class='hero-title'>Multi-Agent Research System</p>", unsafe_allow_html=True)
st.markdown(
    "<p class='hero-sub'>Enter a topic. Four agents search, read, write and critique — you get a polished report.</p>",
    unsafe_allow_html=True,
)

with st.form("research_form", border=False):
    c1, c2 = st.columns([5, 1], vertical_alignment="bottom")
    topic = c1.text_input(
        "Research topic",
        placeholder="e.g. Latest advances in credit card fraud detection",
        label_visibility="collapsed",
    )
    submitted = c2.form_submit_button("Research", type="primary", use_container_width=True)

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            st.session_state["result"] = run_pipeline_ui(topic.strip())
        except Exception as e:
            st.error(f"Pipeline failed: {e}")

result = st.session_state.get("result")

if result:
    report = as_text(result["report"])
    feedback = as_text(result["feedback"])

    st.divider()
    st.subheader(result["topic"])

    m = st.columns(len(result["timings"]) + 1)
    for col, (name, secs) in zip(m, result["timings"].items()):
        col.metric(name, f"{secs:.1f}s")
    m[-1].metric("Total", f"{sum(result['timings'].values()):.1f}s")

    tab_report, tab_feedback, tab_sources = st.tabs(["📄 Report", "🧐 Critic feedback", "🔗 Raw research"])

    with tab_report:
        st.markdown(report)
        st.download_button(
            "Download report (.md)",
            data=report,
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(feedback)

    with tab_sources:
        with st.expander("Search results", expanded=False):
            st.markdown(as_text(result["search_results"]))
        with st.expander("Scraped content", expanded=False):
            st.markdown(as_text(result["scraped_content"]))
else:
    st.info("Your report will appear here once the agents finish.", icon="💡")