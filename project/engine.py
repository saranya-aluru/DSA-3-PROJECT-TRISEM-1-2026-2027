"""Hand-built DSA engine (no library shortcuts). Sequences may be str or token lists."""
import re, math, random
from collections import defaultdict, deque, Counter

def tokenize(t): return [w for w in re.split(r"[\s.,;:!?\"'()\[\]{}<>/\\|\u0964\u2013\u2014-]+", t.lower()) if w]   # Unicode-safe (keeps Indic combining marks)
def sentences(t): return [s.strip() for s in re.split(r"(?<=[.!?।])\s+|\n+", t) if len(s.split()) >= 4]
def _enc(x):
    if isinstance(x, int): return x
    h = 7
    for c in x: h = (h * 131 + ord(c)) % (2**61 - 1)
    return h

# ---------------- CO2: strings ----------------
def kmp_search(text, pat):
    if not pat: return []
    f, k = [0] * len(pat), 0
    for i in range(1, len(pat)):
        while k and pat[i] != pat[k]: k = f[k - 1]
        if pat[i] == pat[k]: k += 1
        f[i] = k
    out, k = [], 0
    for i, c in enumerate(text):
        while k and c != pat[k]: k = f[k - 1]
        if c == pat[k]: k += 1
        if k == len(pat): out.append(i - k + 1); k = f[k - 1]
    return out

def z_function(s):
    n = len(s); z = [0] * n; l = r = 0
    for i in range(1, n):
        if i < r: z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]: z[i] += 1
        if i + z[i] > r: l, r = i, i + z[i]
    return z

def rabin_karp(text, pat, B=911382323, M=(1000000007, 998244353)):
    """Rolling hash, double-hashed; hash hits are verified (Las Vegas)."""
    n, m = len(text), len(pat)
    if m == 0 or m > n: return []
    T, P = [_enc(x) for x in text], [_enc(x) for x in pat]
    hp = [pow(B, m - 1, q) for q in M]; ph, th = [0, 0], [0, 0]
    for i in range(m):
        for j, q in enumerate(M): ph[j] = (ph[j] * B + P[i]) % q; th[j] = (th[j] * B + T[i]) % q
    res = []
    for i in range(n - m + 1):
        if ph == th and T[i:i + m] == P: res.append(i)
        if i < n - m:
            for j, q in enumerate(M): th[j] = ((th[j] - T[i] * hp[j]) * B + T[i + m]) % q
    return res

def aho_corasick(text, patterns):
    """Multi-pattern search. Returns list of (end_index, pattern_index)."""
    go, fail, out = [{}], [0], [[]]
    for pi, p in enumerate(patterns):
        s = 0
        for c in p:
            if c not in go[s]: go.append({}); fail.append(0); out.append([]); go[s][c] = len(go) - 1
            s = go[s][c]
        out[s].append(pi)
    q = deque(go[0].values())
    while q:
        u = q.popleft()
        for c, v in go[u].items():
            f = fail[u]
            while f and c not in go[f]: f = fail[f]
            fail[v] = go[f].get(c, 0) if go[f].get(c, 0) != v else 0
            out[v] = out[v] + out[fail[v]]; q.append(v)
    s, hits = 0, []
    for i, c in enumerate(text):
        while s and c not in go[s]: s = fail[s]
        s = go[s].get(c, 0)
        for pi in out[s]: hits.append((i, pi))
    return hits

def suffix_array(s):
    """Prefix doubling, O(n log^2 n)."""
    n = len(s); rank = [_enc(x) for x in s]; sa = list(range(n)); k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key); nr = [0] * n
        for i in range(1, n): nr[sa[i]] = nr[sa[i - 1]] + (key(sa[i]) != key(sa[i - 1]))
        rank = nr
        if rank[sa[-1]] == n - 1: break
        k *= 2
    return sa

def kasai_lcp(s, sa):
    n = len(s); rank = [0] * n
    for i, p in enumerate(sa): rank[p] = i
    lcp, h = [0] * n, 0                      # lcp[i] = LCP(sa[i-1], sa[i])
    for i in range(n):
        if rank[i]:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]: h += 1
            lcp[rank[i]] = h
            if h: h -= 1
        else: h = 0
    return lcp

def shared_passages(a, b, k=5):
    """Maximal shared word runs (>=k words) between token lists via SA + LCP. -> [(startA, startB, len)]"""
    s = a + ["\x00"] + b; sa = suffix_array(s); lcp = kasai_lcp(s, sa); na = len(a); best = {}
    for i in range(1, len(s)):
        x, y = sa[i - 1], sa[i]
        if (x < na) != (y < na) and lcp[i] >= k and x != na and y != na:
            pa, pb = (x, y - na - 1) if x < na else (y, x - na - 1)
            if pa not in best or best[pa][1] < lcp[i]: best[pa] = (pb, lcp[i])
    out, end = [], -1
    for pa in sorted(best):
        pb, L = best[pa]
        if pa + L > end: out.append((pa, pb, L)); end = pa + L
    return out

# ---------------- CO3: dynamic programming ----------------
def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, len(b) + 1):
            cur = dp[j]; dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] != b[j - 1])); prev = cur
    return dp[-1]

def smith_waterman(a, b, match=2, mis=-1, gap=-1):
    n, m = len(a), len(b); H = [[0] * (m + 1) for _ in range(n + 1)]; best = (0, 0, 0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            H[i][j] = max(0, H[i-1][j-1] + (match if a[i-1] == b[j-1] else mis), H[i-1][j] + gap, H[i][j-1] + gap)
            if H[i][j] > best[0]: best = (H[i][j], i, j)
    sc, i, j = best; ei, ej = i, j
    while i and j and H[i][j] > 0:
        if H[i][j] == H[i-1][j-1] + (match if a[i-1] == b[j-1] else mis): i -= 1; j -= 1
        elif H[i][j] == H[i-1][j] + gap: i -= 1
        else: j -= 1
    return sc, (i, ei), (j, ej)

def lcs_len(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(dp[i-1][j], dp[i][j-1])
    return dp[-1][-1]

# ---------------- CO4: network flow ----------------
def edmonds_karp(cap, s, t):
    """cap: {u:{v:c}}. Returns (maxflow, residual, S-side of min cut)."""
    res = defaultdict(lambda: defaultdict(int))
    for u in cap:
        for v, c in cap[u].items(): res[u][v] += c; res[v][u] += 0
    flow = 0
    while True:
        par = {s: None}; q = deque([s])
        while q and t not in par:
            u = q.popleft()
            for v, c in list(res[u].items()):
                if c > 0 and v not in par: par[v] = u; q.append(v)
        if t not in par: return flow, res, set(par)
        b, v = float("inf"), t
        while par[v] is not None: b = min(b, res[par[v]][v]); v = par[v]
        v = t
        while par[v] is not None: u = par[v]; res[u][v] -= b; res[v][u] += b; v = u
        flow += b

def sentence_matching(sa, sb, thr=0.5):
    """Bipartite max matching (as max-flow) of similar sentences between two docs."""
    A, B = [set(tokenize(x)) for x in sa], [set(tokenize(x)) for x in sb]
    cap = defaultdict(dict)
    for i in range(len(A)):
        cap["S"][("a", i)] = 1
        for j in range(len(B)):
            if jaccard(A[i], B[j]) >= thr: cap[("a", i)][("b", j)] = 1
    for j in range(len(B)): cap[("b", j)]["T"] = 1
    flow, res, _ = edmonds_karp(cap, "S", "T")
    return [(i, j) for i in range(len(A)) for j in range(len(B)) if cap[("a", i)].get(("b", j)) and res[("a", i)][("b", j)] == 0]

# ---------------- CO5: NP-hardness / approximation ----------------
def vertex_cover_2approx(edges):
    """Maximal-matching 2-approximation: |cover| <= 2*OPT."""
    cover = set()
    for u, v in edges:
        if u not in cover and v not in cover: cover |= {u, v}
    return cover

# ---------------- CO6: randomised & parallel ----------------
def miller_rabin(n, rounds=12):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for _ in range(rounds):
        x = pow(random.randrange(2, n - 1), d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def random_prime(bits=31):
    while True:
        c = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(c): return c

def minhash_signature(tokens, k=3, perms=128, seed=1):
    """Universal hashing h(x)=((ax+b) mod p); Monte-Carlo estimate of shingle-Jaccard."""
    rng = random.Random(seed); p = 2147483647  # Mersenne prime (checked by miller_rabin)
    H = [(rng.randrange(1, p), rng.randrange(p)) for _ in range(perms)]
    sh = {_enc(" ".join(tokens[i:i + k])) % p for i in range(max(1, len(tokens) - k + 1))}
    return [min((a * x + b) % p for x in sh) for a, b in H]

def minhash_jaccard(s1, s2): return sum(x == y for x, y in zip(s1, s2)) / len(s1)

def reservoir_sample(stream, k, seed=None):
    rng, res = random.Random(seed), []
    for i, x in enumerate(stream):
        if i < k: res.append(x)
        else:
            j = rng.randint(0, i)
            if j < k: res[j] = x
    return res

def blelloch_scan(arr):
    """Exclusive prefix-sum: up-sweep + down-sweep. Work O(n), span O(log n)."""
    n = 1
    while n < len(arr): n *= 2
    a = list(arr) + [0] * (n - len(arr)); d = 1
    while d < n:
        for i in range(0, n, 2 * d): a[i + 2 * d - 1] += a[i + d - 1]
        d *= 2
    a[-1] = 0; d = n // 2
    while d:
        for i in range(0, n, 2 * d):
            t = a[i + d - 1]; a[i + d - 1] = a[i + 2 * d - 1]; a[i + 2 * d - 1] += t
        d //= 2
    return a[:len(arr)], {"work": 2 * (n - 1), "span": 2 * int(math.log2(n)) if n > 1 else 0}

# ---------------- similarity measures ----------------
def jaccard(a, b): return len(a & b) / len(a | b) if (a | b) else 0.0

def tfidf_cosine(docs):
    toks = [Counter(d) for d in docs]; N = len(docs); df = Counter()
    for c in toks: df.update(c.keys())
    vec = [{w: (c[w] / max(1, sum(c.values()))) * (math.log((1 + N) / (1 + df[w])) + 1) for w in c} for c in toks]
    norm = [math.sqrt(sum(v * v for v in x.values())) or 1 for x in vec]
    return [[sum(w * vec[j].get(t, 0) for t, w in vec[i].items()) / (norm[i] * norm[j]) for j in range(N)] for i in range(N)]
