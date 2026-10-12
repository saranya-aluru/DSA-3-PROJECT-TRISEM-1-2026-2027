import streamlit as st
import auth

st.set_page_config(page_title="SimilarityLab", page_icon="🔎", layout="wide")
st.markdown("""<style>
#MainMenu, footer {visibility:hidden}
.hero{padding:2.2rem 2rem;border-radius:18px;background:linear-gradient(135deg,#312e81,#6d28d9 60%,#0ea5e9);color:#fff;margin-bottom:1.2rem}
.hero h1{margin:0 0 .4rem;font-size:2.3rem;color:#fff} .hero p{margin:0;opacity:.9;font-size:1.05rem}
.feat{border:1px solid #e5e7eb33;border-radius:14px;padding:1rem;height:100%}
.feat b{font-size:1.02rem}
</style>""", unsafe_allow_html=True)

if "user" in st.session_state:
    import dashboard
    dashboard.run(st.session_state["user"])
    st.stop()

st.markdown("""<div class="hero"><h1>🔎 SimilarityLab</h1>
<p>Privacy-preserving multi-document word-level similarity analysis, built on advanced DSA (CO1–CO6).</p></div>""", unsafe_allow_html=True)
left, right = st.columns([1.1, 1], gap="large")
with left:
    for t, d in [("🔒 Private scan", "Unpublished papers stay in memory — never stored or uploaded."),
                 ("⚙️ Hand-built algorithms", "KMP, Rabin-Karp, suffix arrays, DP, max-flow, MinHash and more."),
                 ("📑 Clear reports", "Ranked pairs, highlighted passages, manual-review flags.")]:
        st.markdown(f'<div class="feat"><b>{t}</b><br>{d}</div>', unsafe_allow_html=True); st.write("")
with right:
    tab_in, tab_up = st.tabs(["Log in", "Sign up"])
    with tab_in:
        e = st.text_input("Email", key="le"); p = st.text_input("Password", type="password", key="lp")
        if st.button("Log in", type="primary", use_container_width=True):
            fails = st.session_state.get("fails", 0)
            if fails >= 5: st.error("Too many attempts. Refresh the page to try again.")
            elif (n := auth.login(e, p)): st.session_state["user"] = n; st.rerun()
            else: st.session_state["fails"] = fails + 1; st.error("Incorrect email or password.")
    with tab_up:
        n = st.text_input("Full name", key="sn"); e2 = st.text_input("Email", key="se")
        p2 = st.text_input("Password (8+ characters)", type="password", key="sp")
        if st.button("Create account", use_container_width=True):
            ok, msg = auth.register(n, e2, p2); (st.success if ok else st.error)(msg)
