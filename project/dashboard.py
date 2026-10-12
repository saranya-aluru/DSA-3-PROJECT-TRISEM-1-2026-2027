import io, re, html, zipfile, random
import streamlit as st
import engine as E

FLAG = "High Similarity Detected — Manual Review Recommended"

def extract(name, data):
    ext = name.lower().rsplit(".", 1)[-1]
    if ext == "docx":
        x = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf8", "ignore")
        return html.unescape(re.sub(r"<[^>]+>", "", x.replace("</w:p>", "\n")))
    if ext == "pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    return data.decode("utf-8", "ignore")


CO_CARDS = [
 ("CO1", "Problem-class strategy", "Choose the right algorithm family for each query: pattern search, alignment, flow, NP-hard scheduling.", ["Query classes", "Algorithm selection"]),
 ("CO2", "String algorithms", "Linear-time matching and suffix structures find exact phrases and the longest shared passages.", ["KMP", "Z-function", "Rabin-Karp", "Aho-Corasick", "Suffix array", "LCP"]),
 ("CO3", "Advanced dynamic programming", "Edit distance and sequence alignment catch reworded text that exact matching misses.", ["Levenshtein", "Smith-Waterman", "LCS"]),
 ("CO4", "Network flow", "Max-flow models one-to-one sentence matching between two documents.", ["Edmonds-Karp", "Bipartite matching", "Min-cut"]),
 ("CO5", "NP-completeness & approximation", "Choosing the smallest review set is NP-hard, so a provable 2-approximation is used.", ["Vertex cover", "3-SAT reduction"]),
 ("CO6", "Randomised & parallel", "Monte Carlo and parallel primitives give fast approximate similarity at scale.", ["MinHash", "Miller-Rabin", "Reservoir sampling", "Blelloch scan"]),
]

def home():
    st.markdown("""<style>
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;margin:10px 0 22px}
    .card{border:1px solid #94a3b855;border-radius:16px;padding:16px 18px}
    .card:hover{border-color:#06b6d4;transform:translateY(-3px);transition:.2s}
    .card b{font-size:1.05rem}.pill{display:inline-block;border:1px solid #6366f1aa;border-radius:99px;padding:1px 10px;font-size:.78rem;margin:6px 4px 0 0}
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>Multi-Document Similarity Analysis</h1><p>Compare many documents, find shared words and passages, and rank likely sources — built from hand-coded Advanced DSA algorithms.</p></div>', unsafe_allow_html=True)
    st.markdown("### Course outcomes at a glance")
    st.markdown('<div class="grid">' + "".join(f'<div class="card"><b>{c} · {t}</b><br>{d}<br>' + "".join(f'<span class="pill">{x}</span>' for x in tp) + '</div>' for c, t, d, tp in CO_CARDS) + '</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    a.markdown("### What it does\n- Upload several PDF, DOCX or TXT files\n- Pairwise similarity: Jaccard and TF-IDF cosine\n- Highlights exact shared passages\n- Ranks documents and flags pairs for review\n- 🔒 PRIVATE SCAN keeps unpublished papers in memory only")
    b.markdown("### How to use it\n1. Open the **Analyze** tab\n2. Upload documents in the sidebar, or use the demo\n3. Set the review threshold\n4. Read the ranked table and highlights\n5. Explore each algorithm in the CO tabs")
    st.markdown("### Project team")
    st.markdown('<div class="grid"><div class="card"><b>A. Saranya</b><br>2520080012</div><div class="card"><b>D. Sri Varshini</b><br>2520080013</div><div class="card"><b>D. Manya Akshitha</b><br>2520090032</div><div class="card"><b>Dr. Dyuti Banerjee</b><br>Guide · Assistant Professor, AI&amp;DS</div></div>', unsafe_allow_html=True)
    st.caption("Scores are similarity indicators only. Pairs above the threshold show: " + FLAG)

def run(user):
    st.title("🔎 SimilarityLab — Multi-Document Similarity Analysis")
    with st.sidebar:
        st.write(f"👤 **{user}**")
        if st.button("Log out"): st.session_state.pop("user"); st.rerun()
        private = st.toggle("🔒 PRIVATE SCAN", value=True, help="Unpublished papers: in-memory only, nothing saved or sent anywhere.")
        st.success("PRIVATE SCAN: documents stay in memory for this session only.") if private else st.info("Standard scan")
        thr = st.slider("High-similarity threshold (% matched text)", 5, 90, 25, help="Pairs at or above this are flagged High. Moderate starts at 40% of this value.")
        k = st.slider("Min shared passage (words)", 3, 12, 5)
        files = st.file_uploader("Upload PDF / DOCX / TXT", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        use_demo = st.checkbox("Use demo documents", value=not files)

    docs = {f.name: extract(f.name, f.read()) for f in files} if files else {}
    if use_demo and not docs:
        base = "Hyderabad is the capital of Telangana. The city is known for its pearls and biryani. The Charminar was built in 1591 by Muhammad Quli Qutb Shah."
        docs = {"paper_A.txt": base,
                "paper_B.txt": "Hyderabad is the capital of Telangana. The city is famous for its pearls and delicious food. Charminar was built in 1591 by Muhammad Quli Qutb Shah near the Musi river.",
                "paper_C.txt": "Binary search trees support insertion and lookup in logarithmic time when balanced. Red-black trees guarantee balance with rotations and colour flips."}
    names = list(docs)
    if len(names) < 2: st.warning("Add at least two documents."); st.stop()
    toks = {n: E.tokenize(t) for n, t in docs.items()}
    cos = E.tfidf_cosine([toks[n] for n in names])

    tabs = st.tabs(["🏠 Home", "📊 Analyze", "CO1 Strategy", "CO2 Strings", "CO3 DP", "CO4 Flow", "CO5 NP & Approx", "CO6 Random & Parallel"])

    with tabs[0]: home()
    with tabs[1]:
        rows = []
        for i, a in enumerate(names):
            for j in range(i + 1, len(names)):
                b = names[j]; jac = E.jaccard(set(toks[a]), set(toks[b]))
                cover = sum(L for _, _, L in E.shared_passages(toks[a], toks[b], k)) / max(1, min(len(toks[a]), len(toks[b])))
                rows.append({"A": a, "B": b, "Jaccard %": round(jac * 100, 1), "TF-IDF cosine %": round(cos[i][j] * 100, 1), "Shared-passage coverage %": round(cover * 100, 1)})
        rows.sort(key=lambda r: -r["Shared-passage coverage %"])
        top = rows[0]; st.metric(f"Overall similarity (matched text): {top['A']} ↔ {top['B']}", f"{top['Shared-passage coverage %']}%", help="Share of the shorter document made of shared passages (>= min words). Jaccard and cosine are supporting measures.")
        def band(c):
            if c >= thr: return "High", "#ef4444", FLAG
            if c >= thr * 0.4: return "Moderate", "#f59e0b", "Moderate overlap — review suggested"
            return "Low", "#22c55e", "Low overlap"
        st.subheader("Similarity by document pair"); cards = ""
        for r in rows:
            c = r["Shared-passage coverage %"]; nm, col, msg = band(c)
            cards += (f'<div class="card"><div style="display:flex;gap:16px;align-items:center">'
                      f'<div style="flex:none;width:88px;height:88px;border-radius:50%;background:conic-gradient({col} {min(c,100)*3.6}deg,#94a3b844 0);display:flex;align-items:center;justify-content:center">'
                      f'<div style="width:64px;height:64px;border-radius:50%;background:#1e293b;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700">{c}%</div></div>'
                      f'<div><b>{html.escape(r["A"])} ↔ {html.escape(r["B"])}</b><br><span class="pill" style="border-color:{col}">{nm}</span> {msg}<br>'
                      f'<small>Jaccard {r["Jaccard %"]}% · cosine {r["TF-IDF cosine %"]}%</small></div></div></div>')
        st.markdown('<div class="grid">' + cards + '</div>', unsafe_allow_html=True)
        with st.expander("Full score table"): st.dataframe(rows, use_container_width=True)
        a = st.selectbox("Highlight matches in", names); b = st.selectbox("against", [n for n in names if n != a])
        ta = docs[a].split(); tl = toks[a]; marks = E.shared_passages(tl, toks[b], k)
        # map tokens back to raw words approximately (same split granularity)
        raw = E.tokenize(docs[a]); hit = set(p + o for p, _, L in marks for o in range(L))
        st.markdown(" ".join(f"<mark>{html.escape(w)}</mark>" if i in hit else html.escape(w) for i, w in enumerate(raw)), unsafe_allow_html=True)
        rep = "\n".join(f"{r['A']} vs {r['B']}: Jaccard {r['Jaccard %']}%, cosine {r['TF-IDF cosine %']}%, coverage {r['Shared-passage coverage %']}%" for r in rows)
        st.download_button("Download text report", rep + f"\n\nNote: scores indicate similarity only. {FLAG} when above threshold.", "similarity_report.txt")

    with tabs[2]:
        st.markdown("**CO1 — Pick the right algorithm family for each query class**")
        st.table([{"Query class": q, "Problem family": f, "Strategy used here": s} for q, f, s in [
            ("Exact phrase search", "Pattern search", "KMP / Rabin-Karp / Aho-Corasick"),
            ("Fuzzy / paraphrase match", "Sequence alignment", "Edit distance, Smith-Waterman (DP)"),
            ("Longest shared passage", "Suffix structures", "Suffix array + Kasai LCP"),
            ("One-to-one sentence pairing", "Flow on a network", "Edmonds-Karp bipartite matching"),
            ("Which docs to review (min set)", "NP-hard covering", "Vertex-cover 2-approximation"),
            ("Fast approximate similarity", "Randomised", "MinHash (Monte Carlo), Miller-Rabin primes")]])

    with tabs[3]:
        st.markdown("**CO2 — KMP, Z, Rabin-Karp (double hash), Aho-Corasick, Suffix array + LCP**")
        q = st.text_input("Phrase to find", "capital of telangana"); p = E.tokenize(q)
        if p:
            c1, c2 = st.columns(2)
            for n in names:
                c1.write(f"`{n}` — KMP: {E.kmp_search(toks[n], p)} · Rabin-Karp: {E.rabin_karp(toks[n], p)}")
            z = E.z_function(p + ["\x00"] + toks[names[0]]); c2.write(f"Z-function occurrences in {names[0]}: {[i - len(p) - 1 for i, v in enumerate(z) if v == len(p)]}")
            hits = E.aho_corasick(toks[names[0]], [E.tokenize(x) for x in q.split(",")])
            c2.write(f"Aho-Corasick (comma-separated patterns): {hits}")
        s = toks[names[0]]; sa = E.suffix_array(s); lcp = E.kasai_lcp(s, sa)
        st.write("Suffix array (first 10):", sa[:10], "· LCP:", lcp[:10])

    with tabs[4]:
        st.markdown("**CO3 — Edit distance & Smith-Waterman local alignment**")
        a, b = names[0], names[1]
        sc, (i0, i1), (j0, j1) = E.smith_waterman(toks[a], toks[b])
        st.write(f"Best local alignment score **{sc}** → `{a}` words {i0}–{i1}, `{b}` words {j0}–{j1}")
        st.code(" ".join(toks[a][i0:i1]) + "\n" + " ".join(toks[b][j0:j1]))
        w1, w2 = st.text_input("Word 1", "similarity"), st.text_input("Word 2", "simplicity")
        st.write("Levenshtein distance:", E.edit_distance(w1, w2), "· Word-level LCS:", E.lcs_len(toks[a], toks[b]))

    with tabs[5]:
        st.markdown("**CO4 — Max-flow (Edmonds-Karp) as bipartite sentence matching**")
        sa_, sb_ = E.sentences(docs[names[0]]), E.sentences(docs[names[1]])
        t = st.slider("Sentence similarity", 0.2, 1.0, 0.4)
        for i, j in E.sentence_matching(sa_, sb_, t): st.write(f"• “{sa_[i]}” ↔ “{sb_[j]}”")

    with tabs[6]:
        st.markdown("**CO5 — Vertex-cover 2-approximation on the similarity graph** (a small set of documents that touches every flagged pair)")
        edges = [(r["A"], r["B"]) for r in rows if r["Jaccard %"] >= thr / 2]
        st.write("Flagged edges:", edges or "none"); st.write("Approx. review set (≤ 2·OPT):", sorted(E.vertex_cover_2approx(edges)))
        st.caption("Reduction chain: 3-SAT → Vertex Cover → Independent Set; exact minimum cover is NP-hard.")

    with tabs[7]:
        st.markdown("**CO6 — MinHash (Monte Carlo), Miller-Rabin, reservoir sampling, Blelloch scan**")
        exact = E.jaccard(set(toks[names[0]]), set(toks[names[1]]))
        est = E.minhash_jaccard(E.minhash_signature(toks[names[0]]), E.minhash_signature(toks[names[1]]))
        st.write(f"Word-Jaccard exact {exact:.2f} · 3-shingle MinHash estimate {est:.2f}")
        n = st.number_input("Primality test (Miller-Rabin)", value=1000000007); st.write("Probably prime" if E.miller_rabin(int(n)) else "Composite")
        st.write("Reservoir sample of 3 sentences:", E.reservoir_sample(E.sentences(docs[names[0]]) or ["-"], 3))
        counts = [len(E.shared_passages(toks[names[0]], toks[x], k)) for x in names]
        scan, ws = E.blelloch_scan(counts); st.write("Parallel prefix-sum of match counts:", scan, ws)
