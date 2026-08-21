#!/usr/bin/env python3
"""
Group a Claude.ai data export into topic clusters and render a browsable HTML page.

Usage:
    python3 organize_chats.py <export.zip | conversations.json | export_dir> [-o out.html]

Takes the `conversations.json` from a Claude.ai data export
(claude.ai -> Settings -> Privacy -> Export data), clusters conversations by
topic, and writes a single self-contained HTML file.

Pure standard library: no numpy, no sklearn, no network access.
"""

import argparse
import json
import math
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from heapq import heappush, heappop

# ---------------------------------------------------------------- loading


def _find_conversations(payload):
    """Pull the conversation list out of whatever shape the export used."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("conversations", "chat_conversations", "data", "items"):
            val = payload.get(key)
            if isinstance(val, list):
                return val
    raise ValueError("could not find a conversation list in that JSON")


def load_export(path):
    """Accept a .zip, a conversations.json, or a directory containing one."""
    if os.path.isdir(path):
        candidate = os.path.join(path, "conversations.json")
        if not os.path.exists(candidate):
            matches = [f for f in os.listdir(path) if f.endswith(".json")]
            if not matches:
                raise SystemExit(f"no .json file found in {path}")
            candidate = os.path.join(path, sorted(matches)[0])
        with open(candidate, encoding="utf-8") as fh:
            return _find_conversations(json.load(fh))

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            target = next(
                (n for n in names if n.endswith("conversations.json")),
                None,
            ) or next((n for n in names if n.endswith(".json")), None)
            if target is None:
                raise SystemExit(f"no conversations.json inside {path}")
            with zf.open(target) as fh:
                return _find_conversations(json.load(fh))

    with open(path, encoding="utf-8") as fh:
        return _find_conversations(json.load(fh))


# ---------------------------------------------------------------- normalising

def message_text(msg):
    """Claude exports put text in `text`, or in a `content` block list."""
    if isinstance(msg, str):
        return msg
    if not isinstance(msg, dict):
        return ""
    direct = msg.get("text")
    if isinstance(direct, str) and direct.strip():
        return direct
    parts = []
    for block in msg.get("content") or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            # skip thinking blocks: they are model scratch, not user topic signal
            if block.get("type") in (None, "text") and block.get("text"):
                parts.append(block["text"])
    return "\n".join(parts)


def parse_time(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.replace("Z", "+00:00")
    # trim over-long fractional seconds that fromisoformat rejects on 3.10
    cleaned = re.sub(r"\.(\d{6})\d+", r".\1", cleaned)
    try:
        dt = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def normalise(raw):
    """One export record -> the fields we actually use."""
    msgs_raw = raw.get("chat_messages") or raw.get("messages") or []
    messages = []
    for m in msgs_raw:
        text = message_text(m).strip()
        sender = (m.get("sender") or m.get("role") or "") if isinstance(m, dict) else ""
        stamp = parse_time(m.get("created_at")) if isinstance(m, dict) else None
        if text:
            messages.append({"sender": sender.lower(), "text": text, "at": stamp})

    created = parse_time(raw.get("created_at"))
    updated = parse_time(raw.get("updated_at"))
    stamps = [m["at"] for m in messages if m["at"]]
    if created is None and stamps:
        created = min(stamps)
    if updated is None and stamps:
        updated = max(stamps)

    title = (raw.get("name") or raw.get("title") or "").strip()
    if not title:
        first_human = next(
            (m["text"] for m in messages if m["sender"].startswith("human")), ""
        )
        title = (first_human[:60].strip() or "Untitled conversation")
        if len(first_human) > 60:
            title += "..."

    return {
        "uuid": raw.get("uuid") or raw.get("id") or "",
        "title": title,
        "created": created,
        "updated": updated,
        "messages": messages,
        "n_messages": len(messages),
    }


# ---------------------------------------------------------------- text signal

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because
been before being below between both but by can cannot could couldn't did didn't
do does doesn't doing don't down during each few for from further had hadn't has
hasn't have haven't having he he'd he'll he's her here here's hers herself him
himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself
let's me more most mustn't my myself no nor not of off on once only or other
ought our ours ourselves out over own same shan't she she'd she'll she's should
shouldn't so some such than that that's the their theirs them themselves then
there there's these they they'd they'll they're they've this those through to
too under until up very was wasn't we we'd we'll we're we've were weren't what
what's when when's where where's which while who who's whom why why's with won't
would wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())

# words that show up in almost every chat and carry no topic signal
CHAT_NOISE = set("""
claude chatgpt gpt ai assistant hi hello hey thanks thank please sure okay ok
yes yeah nope yep just like get got make made want need help helping helped
know think thing things something anything nothing use using used try trying
tried give given tell told say said see look looking able maybe really actually
also however basically bit lot lots one two three new good great nice better
best way ways time times work works working question questions answer answers
example examples let lets going go goes went come comes came take takes took
put puts add adds added write writes wrote written find finds found show shows
showed based here's there's what's it's i'm don't can't won't didn't doesn't
sorry great perfect awesome cool hmm well ah oh yeah's much many still even
back around still already always never sometimes often quite rather pretty
explain explanation describe summarize summarise rewrite draft outline
brainstorm suggest recommend advice compare choose decide understand learn
teach guide tip tips idea ideas option options approach step steps walk
quick simple easy hard difficult wondering curious
yet http https www com org net href link links
""".split())

TOKEN_RE = re.compile(r"[a-z][a-z0-9+#.\-']{1,}")


def stem(word):
    """Very light suffix normalisation so plurals/tenses collapse together."""
    for suffix, keep in (
        ("ations", 3), ("ation", 2), ("ingly", 5), ("edly", 4),
        ("ments", 4), ("ment", 4), ("ness", 4), ("ities", 3), ("ity", 3),
        ("ies", 1), ("ing", 3), ("ers", 2), ("er", 2), ("ed", 2), ("s", 1),
    ):
        if word.endswith(suffix) and len(word) - keep >= 4:
            base = word[: len(word) - keep]
            if suffix == "ies":
                base += "y"
            return base
    return word


def tokenize(text):
    """Yield (surface, stem) pairs, dropping stopwords and conversational filler.

    Filler is checked against the stem as well as the raw word, so "explaining"
    is caught by "explain" rather than surviving as a topic term.
    """
    for raw in TOKEN_RE.findall(text.lower()):
        cleaned = raw.strip(".-'")
        if len(cleaned) < 3 or cleaned.isdigit():
            continue
        if cleaned in STOPWORDS or cleaned in CHAT_NOISE:
            continue
        root = stem(cleaned)
        if root in STOPWORDS or root in CHAT_NOISE:
            continue
        yield cleaned, root


# How much of each conversation to read. The title and the user's own words say
# what a chat is about; assistant prose is long, repetitive, and mostly restates
# the question, so it is read briefly and at half weight.
TITLE_WEIGHT = 6
FIRST_TURN_WEIGHT = 3
HUMAN_CHARS = 4000
ASSISTANT_CHARS = 800
ASSISTANT_WEIGHT = 0.5


def topic_tokens(conv, surface):
    """Weighted bag of stems for one conversation, plus the stems in its title."""
    counts = Counter()
    title_stems = set()

    def absorb(text, weight, collect=None):
        for word, root in tokenize(text):
            counts[root] += weight
            surface[root][word] += 1
            if collect is not None:
                collect.add(root)

    absorb(conv["title"], TITLE_WEIGHT, title_stems)

    human, assistant, seen = [], [], set()
    for msg in conv["messages"]:
        fingerprint = msg["text"][:200]
        if fingerprint in seen:
            continue                      # quoted or re-sent text should not count twice
        seen.add(fingerprint)
        (human if msg["sender"].startswith("human") else assistant).append(msg)

    if human:
        absorb(human[0]["text"][:1500], FIRST_TURN_WEIGHT)

    budget = HUMAN_CHARS
    for msg in human[1:]:
        if budget <= 0:
            break
        absorb(msg["text"][:budget], 1)
        budget -= len(msg["text"])

    # a little assistant text helps when the human turns are terse ("do it", "yes")
    budget = ASSISTANT_CHARS
    for msg in assistant:
        if budget <= 0:
            break
        absorb(msg["text"][:budget], ASSISTANT_WEIGHT)
        budget -= len(msg["text"])

    return counts, title_stems


def build_vectors(convs):
    """TF-IDF, L2-normalised, as sparse dicts.

    Returns (vectors, surface_forms, title_stems, idf).
    """
    surface = defaultdict(Counter)
    extracted = [topic_tokens(c, surface) for c in convs]
    raw_counts = [pair[0] for pair in extracted]
    title_stems = [pair[1] for pair in extracted]

    doc_freq = Counter()
    for counts in raw_counts:
        doc_freq.update(counts.keys())

    n_docs = len(convs)
    # a term in one doc can't group anything; a term in most docs can't separate
    min_df = 2 if n_docs > 12 else 1
    max_df = max(min_df, int(n_docs * 0.5)) if n_docs > 12 else n_docs

    idf = {
        term: math.log((n_docs + 1) / (df + 1)) + 1.0
        for term, df in doc_freq.items()
    }

    vectors = []
    for counts in raw_counts:
        vec = {}
        for term, tf in counts.items():
            df = doc_freq[term]
            if df < min_df or df > max_df:
                continue
            vec[term] = (1.0 + math.log(max(tf, 0.1))) * idf[term]
        norm = math.sqrt(sum(w * w for w in vec.values()))
        vectors.append({t: w / norm for t, w in vec.items()} if norm else {})

    best_surface = {
        root: forms.most_common(1)[0][0] for root, forms in surface.items()
    }
    return vectors, best_surface, title_stems, idf


# ---------------------------------------------------------------- clustering

MERGE_THRESHOLD = 0.30      # cosine needed to join two groups
ATTACH_THRESHOLD = 0.18     # looser bar for pulling a leftover into a group
CONSOLIDATE_RATIO = 0.70    # second pass runs at this fraction of the threshold
MAX_GROUP_FRACTION = 0.10   # no topic may hold more than this share of the archive
MAX_GROUP_CEILING = 20      # ...nor more than this many, however large the archive
MIN_GROUP_CEILING = 8       # ...nor fewer than this, however small
TOP_TERMS_INDEXED = 40      # terms per centroid used for candidate lookup
NEIGHBOURS_PER_CLUSTER = 20


def default_cap(total):
    """Largest a topic may grow.

    An unbounded centroid-linkage run chains loosely-related groups into one
    blob: on a real archive the top group swallowed a fifth of it and mixed
    unrelated subjects. Capping the size stops the chain, and a group larger
    than a couple of dozen conversations is not a browsable unit anyway.
    """
    return max(
        MIN_GROUP_CEILING,
        min(MAX_GROUP_CEILING, int(total * MAX_GROUP_FRACTION)),
    )


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b.get(term, 0.0) for term, w in a.items())


def normalise_vec(vec):
    norm = math.sqrt(sum(w * w for w in vec.values()))
    return {t: w / norm for t, w in vec.items()} if norm else {}


def top_terms(vec, limit=TOP_TERMS_INDEXED):
    return sorted(vec.items(), key=lambda kv: -kv[1])[:limit]


def cluster(vectors, threshold=MERGE_THRESHOLD, size_cap=None, weights=None):
    """Centroid-linkage agglomerative clustering over a sparse candidate graph.

    `weights` gives the number of conversations each vector stands for, so the
    size cap means the same thing whether the input is conversations or the
    centroids of already-formed groups.
    """
    n = len(vectors)
    if n == 0:
        return []
    if weights is None:
        weights = [1] * n
    if size_cap is None:
        size_cap = default_cap(sum(weights))

    centroids = {i: vectors[i] for i in range(n)}
    members = {i: [i] for i in range(n)}
    mass = {i: weights[i] for i in range(n)}
    alive = set(range(n))
    index = defaultdict(list)          # term -> [(cluster_id, weight), ...]
    heap = []
    next_id = n

    def register(cid):
        for term, weight in top_terms(centroids[cid]):
            index[term].append((cid, weight))

    def push_neighbours(cid):
        acc = defaultdict(float)
        for term, weight in top_terms(centroids[cid]):
            for other, other_weight in index.get(term, ()):
                if other != cid and other in alive:
                    acc[other] += weight * other_weight
        ranked = sorted(acc.items(), key=lambda kv: -kv[1])[:NEIGHBOURS_PER_CLUSTER]
        for other, _approx in ranked:
            sim = cosine(centroids[cid], centroids[other])
            if sim >= threshold:
                heappush(heap, (-sim, cid, other))

    for i in range(n):
        register(i)
    for i in range(n):
        push_neighbours(i)

    while heap:
        neg_sim, a, b = heappop(heap)
        if a not in alive or b not in alive:
            continue                                  # stale entry
        if -neg_sim < threshold:
            break
        if mass[a] + mass[b] > size_cap:
            continue                                  # keep groups browsable

        merged = next_id
        next_id += 1
        combined = defaultdict(float)
        for source in (a, b):
            for term, weight in centroids[source].items():
                combined[term] += weight * mass[source]
        centroids[merged] = normalise_vec(combined)
        members[merged] = members[a] + members[b]
        mass[merged] = mass[a] + mass[b]

        alive.discard(a)
        alive.discard(b)
        alive.add(merged)
        register(merged)
        push_neighbours(merged)

    return [sorted(members[cid]) for cid in alive]


def group_centroid(indices, vectors):
    combined = defaultdict(float)
    for idx in indices:
        for term, weight in vectors[idx].items():
            combined[term] += weight
    return normalise_vec(combined)


def consolidate(groups, vectors, threshold, size_cap=None):
    """Rejoin topic fragments that split on wording but share a subject.

    Clustering conversations directly stops at the merge threshold, which leaves
    one subject spread over several small groups when its chats use different
    vocabulary -- a DCF question and a sensitivity-table question share a topic
    but few words. Re-clustering the group centroids at a looser threshold
    rejoins those without letting individual stray conversations chain together,
    which is what simply lowering the first threshold would do.
    """
    if len(groups) < 2:
        return groups
    centroids = [group_centroid(g, vectors) for g in groups]
    weights = [len(g) for g in groups]
    bundles = cluster(
        centroids, threshold=threshold, size_cap=size_cap, weights=weights
    )

    merged = []
    for bundle in bundles:
        rejoined = []
        for slot in bundle:
            rejoined.extend(groups[slot])
        merged.append(sorted(rejoined))
    return merged


def attach_leftovers(groups, vectors, threshold=ATTACH_THRESHOLD, size_cap=None):
    """Pull one-off conversations into the closest group when they clearly belong."""
    grouped = [g for g in groups if len(g) > 1]
    singles = [g[0] for g in groups if len(g) == 1]
    if not grouped or not singles:
        return groups

    if size_cap is None:
        size_cap = default_cap(sum(len(g) for g in groups))
    centroids = [group_centroid(g, vectors) for g in grouped]

    still_alone = []
    for idx in singles:
        best, best_sim = -1, threshold
        for slot, centroid in enumerate(centroids):
            if len(grouped[slot]) >= size_cap:
                continue
            sim = cosine(vectors[idx], centroid)
            if sim >= best_sim:
                best, best_sim = slot, sim
        if best >= 0:
            grouped[best].append(idx)
        else:
            still_alone.append(idx)

    return [sorted(g) for g in grouped] + [[i] for i in still_alone]


# ---------------------------------------------------------------- labelling

ACRONYMS = set("""
sql api css html http https json csv xml yaml url ui ux ai ml llm nlp gpu cpu
aws gcp api's dcf wacc npv irr roi kpi crm erp hr ceo cto cfo cv seo sem saas
b2b b2c pdf gif png jpg svg ide cli sdk orm jwt ssh ssl tls dns vpn ios sdk npm
""".split())


def pretty(word):
    """Capitalise a label word.

    Uses manual capitalisation rather than str.title(), which mangles
    apostrophes -- "china's" would become "China'S".
    """
    if word in ACRONYMS:
        return word.upper()
    return "-".join(
        part[:1].upper() + part[1:] for part in word.split("-") if part
    )


def label_group(indices, vectors, surface, title_stems, idf, used_labels):
    """Name a group after the words its own titles share.

    A term the user wrote into several titles names the group far better than
    the highest-weighted term mined from message bodies, which tends to be
    assistant phrasing rather than the subject.
    """
    shared = Counter()
    for idx in indices:
        for root in title_stems[idx]:
            shared[root] += 1

    from_titles = sorted(
        (root for root, hits in shared.items() if hits >= 2),
        key=lambda root: (-shared[root], -idf.get(root, 1.0)),
    )

    combined = defaultdict(float)
    in_group = Counter()
    for idx in indices:
        for term, weight in vectors[idx].items():
            combined[term] += weight
            in_group[term] += 1

    # a term running through most of the group's conversations describes it
    # better than one that is merely heavy inside a single conversation
    quorum = max(2, (len(indices) + 1) // 2)
    widespread = sorted(
        (t for t, hits in in_group.items() if hits >= quorum),
        key=lambda t: (-in_group[t], -combined[t]),
    )
    by_mass = [t for t, _ in sorted(combined.items(), key=lambda kv: -kv[1])]

    ranked, seen_terms = [], set()
    for bucket in (from_titles, widespread, by_mass):
        for term in bucket:
            if term not in seen_terms:
                seen_terms.add(term)
                ranked.append(term)
    words = [surface.get(term, term) for term in ranked[:14]]
    # drop near-duplicates like "resume" / "resumes" that stem apart
    deduped = []
    for word in words:
        if not any(word.startswith(seen[:4]) for seen in deduped):
            deduped.append(word)

    for size in (2, 3, 4):
        label = " · ".join(pretty(w) for w in deduped[:size])
        if label and label not in used_labels:
            used_labels.add(label)
            return label, deduped[:8]

    fallback = " · ".join(pretty(w) for w in deduped[:2]) or "Assorted"
    suffix = 2
    while f"{fallback} ({suffix})" in used_labels:
        suffix += 1
    label = f"{fallback} ({suffix})"
    used_labels.add(label)
    return label, deduped[:8]


# ---------------------------------------------------------------- assembly

CHAT_URL = "https://claude.ai/chat/{}"


def iso_day(dt):
    return dt.strftime("%Y-%m-%d") if dt else ""


def preview_of(conv, limit=240):
    first = next(
        (m["text"] for m in conv["messages"] if m["sender"].startswith("human")),
        "",
    )
    if not first:
        first = conv["messages"][0]["text"] if conv["messages"] else ""
    flat = re.sub(r"\s+", " ", first).strip()
    return flat[:limit] + ("..." if len(flat) > limit else "")


def summarise(convs, groups, vectors, surface, title_stems, idf):
    used_labels = set()
    payload_groups = []

    ordered = sorted(groups, key=len, reverse=True)
    multi = [g for g in ordered if len(g) > 1]
    singles = [g[0] for g in ordered if len(g) == 1]

    for indices in multi:
        label, keywords = label_group(
            indices, vectors, surface, title_stems, idf, used_labels
        )
        items = sorted(
            (convs[i] for i in indices),
            key=lambda c: c["updated"] or c["created"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        stamps = [c["updated"] or c["created"] for c in items if (c["updated"] or c["created"])]
        payload_groups.append({
            "label": label,
            "keywords": keywords,
            "count": len(items),
            "messages": sum(c["n_messages"] for c in items),
            "first": iso_day(min(stamps)) if stamps else "",
            "last": iso_day(max(stamps)) if stamps else "",
            "standalone": False,
            "conversations": [conv_payload(c) for c in items],
        })

    if singles:
        items = sorted(
            (convs[i] for i in singles),
            key=lambda c: c["updated"] or c["created"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        stamps = [c["updated"] or c["created"] for c in items if (c["updated"] or c["created"])]
        payload_groups.append({
            "label": "One-offs",
            "keywords": [],
            "count": len(items),
            "messages": sum(c["n_messages"] for c in items),
            "first": iso_day(min(stamps)) if stamps else "",
            "last": iso_day(max(stamps)) if stamps else "",
            "standalone": True,
            "conversations": [conv_payload(c) for c in items],
        })

    all_stamps = [c["updated"] or c["created"] for c in convs if (c["updated"] or c["created"])]
    stats = {
        "conversations": len(convs),
        "messages": sum(c["n_messages"] for c in convs),
        "groups": len(multi),
        "standalone": len(singles),
        "first": iso_day(min(all_stamps)) if all_stamps else "",
        "last": iso_day(max(all_stamps)) if all_stamps else "",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    return {"stats": stats, "groups": payload_groups}


def conv_payload(conv):
    return {
        "title": conv["title"],
        "url": CHAT_URL.format(conv["uuid"]) if conv["uuid"] else "",
        "created": iso_day(conv["created"]),
        "updated": iso_day(conv["updated"]),
        "messages": conv["n_messages"],
        "preview": preview_of(conv),
    }


# ---------------------------------------------------------------- entry point

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Group a Claude.ai export into topic clusters and render HTML."
    )
    parser.add_argument("export", help="export .zip, conversations.json, or export directory")
    parser.add_argument("-o", "--out", default="chat-history.html", help="output HTML file")
    parser.add_argument("--json", help="also write the grouped data as JSON")
    parser.add_argument(
        "--threshold", type=float, default=MERGE_THRESHOLD,
        help=f"merge similarity 0-1; lower = fewer, broader groups (default {MERGE_THRESHOLD})",
    )
    parser.add_argument(
        "--max-group", type=int, default=None,
        help="largest number of conversations one topic may hold",
    )
    parser.add_argument(
        "--sample", action="store_true",
        help="mark the output as built from sample data",
    )
    args = parser.parse_args(argv)

    raw = load_export(args.export)
    convs = [normalise(r) for r in raw]
    convs = [c for c in convs if c["n_messages"] > 0]
    if not convs:
        raise SystemExit("no conversations with messages found in that export")

    print(f"Read {len(convs)} conversations", file=sys.stderr)

    vectors, surface, title_stems, idf = build_vectors(convs)
    cap = args.max_group or default_cap(len(convs))
    groups = cluster(vectors, threshold=args.threshold, size_cap=cap)
    groups = consolidate(
        groups, vectors, args.threshold * CONSOLIDATE_RATIO, size_cap=cap
    )
    groups = attach_leftovers(groups, vectors, size_cap=cap)
    payload = summarise(convs, groups, vectors, surface, title_stems, idf)
    payload["stats"]["sample"] = bool(args.sample)

    stats = payload["stats"]
    print(
        f"Grouped into {stats['groups']} topics "
        f"({stats['standalone']} one-offs)",
        file=sys.stderr,
    )

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"Wrote {args.json}", file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render_html(payload))
    print(f"Wrote {args.out}", file=sys.stderr)


# ---------------------------------------------------------------- rendering

PAGE = r"""<title>Conversation Archive</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,600&display=swap">
<style>
:root{
  color-scheme: light dark;
  --paper:#F2F5F4;
  --surface:#FFFFFF;
  --sunk:#E7EDEB;
  --ink:#15282E;
  --muted:#5A6F76;
  --rule:#D6E0DD;
  --accent:#2C6E7C;
  --accent-ink:#FFFFFF;
  --wash:rgba(44,110,124,.09);
  --shadow:0 1px 2px rgba(21,40,46,.05), 0 10px 30px -22px rgba(21,40,46,.45);
  --serif:"Newsreader", Georgia, "Times New Roman", serif;
  --sans:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0E1618;
    --surface:#151F22;
    --sunk:#1B282B;
    --ink:#E2EAE9;
    --muted:#8FA4A9;
    --rule:#253538;
    --accent:#68B8C7;
    --accent-ink:#08181C;
    --wash:rgba(104,184,199,.12);
    --shadow:0 1px 2px rgba(0,0,0,.45), 0 10px 30px -22px rgba(0,0,0,.9);
  }
}
:root[data-theme="dark"]{
  --paper:#0E1618;
  --surface:#151F22;
  --sunk:#1B282B;
  --ink:#E2EAE9;
  --muted:#8FA4A9;
  --rule:#253538;
  --accent:#68B8C7;
  --accent-ink:#08181C;
  --wash:rgba(104,184,199,.12);
  --shadow:0 1px 2px rgba(0,0,0,.45), 0 10px 30px -22px rgba(0,0,0,.9);
}

*{box-sizing:border-box}
body{
  margin:0;
  background:var(--paper);
  color:var(--ink);
  font-family:var(--sans);
  font-size:16px;
  line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}
@media (prefers-reduced-motion: reduce){*{transition:none !important;animation:none !important}}

.shell{max-width:1140px;margin:0 auto;padding:clamp(28px,5vw,64px) clamp(16px,4vw,40px) 112px}

/* ---- masthead ---- */
.masthead{display:flex;flex-direction:column;gap:14px;padding-bottom:26px;border-bottom:1px solid var(--rule)}
.eyebrow{
  margin:0;font-family:var(--mono);font-size:.7rem;font-weight:500;
  letter-spacing:.18em;text-transform:uppercase;color:var(--accent);
}
h1{
  margin:0;font-family:var(--serif);font-weight:600;
  font-size:clamp(2.1rem,5.2vw,3.15rem);line-height:1.05;
  letter-spacing:-.02em;text-wrap:balance;
}
.lede{margin:0;max-width:62ch;color:var(--muted);font-size:1.03rem}
.colophon{
  display:flex;flex-wrap:wrap;gap:8px 30px;margin:6px 0 0;padding:0;
  font-family:var(--mono);font-size:.78rem;font-variant-numeric:tabular-nums;
}
.colophon div{display:flex;gap:8px;align-items:baseline}
.colophon dt{color:var(--muted);letter-spacing:.06em;text-transform:uppercase;font-size:.68rem}
.colophon dd{margin:0;font-weight:500}

/* ---- notice ---- */
.notice{
  margin:26px 0 0;padding:14px 18px;border-radius:3px;
  background:var(--wash);border-left:3px solid var(--accent);
  font-size:.9rem;color:var(--ink);
}
.notice strong{font-weight:600}

/* ---- controls ---- */
.controls{
  display:flex;flex-wrap:wrap;gap:12px;align-items:center;
  margin:30px 0 34px;
}
.search{position:relative;flex:1 1 280px;min-width:0}
.search input{
  width:100%;padding:11px 14px 11px 38px;
  font-family:var(--sans);font-size:.94rem;color:var(--ink);
  background:var(--surface);border:1px solid var(--rule);border-radius:3px;
}
.search input::placeholder{color:var(--muted)}
.search svg{
  position:absolute;left:13px;top:50%;transform:translateY(-50%);
  width:15px;height:15px;stroke:var(--muted);fill:none;stroke-width:2;
}
.pick{
  display:flex;align-items:center;gap:8px;
  font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);
}
.pick select{
  font-family:var(--sans);font-size:.88rem;letter-spacing:0;text-transform:none;
  color:var(--ink);background:var(--surface);
  border:1px solid var(--rule);border-radius:3px;padding:8px 10px;
}
.ghost{
  font-family:var(--sans);font-size:.88rem;color:var(--ink);
  background:var(--surface);border:1px solid var(--rule);border-radius:3px;
  padding:9px 14px;cursor:pointer;
}
.ghost:hover{border-color:var(--accent);color:var(--accent)}

/* ---- two-pane body ---- */
.panes{display:grid;grid-template-columns:212px minmax(0,1fr);gap:44px;align-items:start}
.rail{position:sticky;top:24px;display:flex;flex-direction:column;gap:2px;max-height:calc(100vh - 48px);overflow-y:auto}
.rail-head{
  font-family:var(--mono);font-size:.68rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted);padding:0 0 10px;
}
.rail a{
  display:flex;justify-content:space-between;gap:10px;align-items:baseline;
  padding:7px 10px;border-radius:3px;text-decoration:none;
  color:var(--ink);font-size:.88rem;line-height:1.35;
  border-left:2px solid transparent;
}
.rail a:hover{background:var(--wash);border-left-color:var(--accent)}
.rail a .n{font-family:var(--mono);font-size:.76rem;color:var(--muted);font-variant-numeric:tabular-nums}
.rail a.solo{color:var(--muted);font-style:italic}

/* ---- groups ---- */
.groups{display:flex;flex-direction:column;gap:16px;min-width:0}
.group{
  background:var(--surface);border:1px solid var(--rule);border-radius:4px;
  box-shadow:var(--shadow);overflow:hidden;
}
.group[open] > .cap{border-bottom:1px solid var(--rule)}
.cap{
  display:flex;gap:16px;align-items:flex-start;justify-content:space-between;
  padding:18px 22px;cursor:pointer;list-style:none;
}
.cap::-webkit-details-marker{display:none}
.cap:hover{background:var(--wash)}
.cap-main{display:flex;flex-direction:column;gap:9px;min-width:0}
.cap h2{
  margin:0;font-family:var(--serif);font-weight:600;font-size:1.32rem;
  line-height:1.2;letter-spacing:-.01em;text-wrap:balance;
}
.keys{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.keys li{
  font-family:var(--mono);font-size:.68rem;color:var(--muted);
  background:var(--sunk);border-radius:2px;padding:2px 7px;
}
.cap-meta{
  display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex:none;
  font-family:var(--mono);font-size:.72rem;color:var(--muted);
  font-variant-numeric:tabular-nums;text-align:right;
}
.cap-meta .count{color:var(--accent);font-size:1.05rem;font-weight:500}
.chev{flex:none;width:11px;height:11px;stroke:var(--muted);fill:none;stroke-width:2.2;transition:transform .15s ease}
.group[open] .chev{transform:rotate(90deg)}

.rows{display:flex;flex-direction:column}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 20px;padding:14px 22px;border-top:1px solid var(--rule)}
.rows > .row:first-child{border-top:none}
.row:hover{background:var(--wash)}
.row[hidden]{display:none}
.row .t{margin:0;font-size:.97rem;font-weight:500;line-height:1.35}
.row .t a{color:var(--ink);text-decoration:none;text-decoration-color:var(--rule)}
.row .t a:hover{color:var(--accent);text-decoration:underline}
.row .p{grid-column:1;margin:0;font-size:.85rem;color:var(--muted);line-height:1.5;max-width:72ch}
.row .m{
  grid-row:1 / span 2;grid-column:2;align-self:start;text-align:right;
  font-family:var(--mono);font-size:.72rem;color:var(--muted);
  font-variant-numeric:tabular-nums;white-space:nowrap;
}
.row .m span{display:block}

.empty{
  padding:52px 22px;text-align:center;color:var(--muted);
  background:var(--surface);border:1px dashed var(--rule);border-radius:4px;
}
.empty p{margin:0 0 6px}
.empty .big{font-family:var(--serif);font-size:1.25rem;color:var(--ink)}

footer{
  margin-top:44px;padding-top:20px;border-top:1px solid var(--rule);
  font-family:var(--mono);font-size:.72rem;color:var(--muted);
}
footer a{color:var(--accent)}

@media (max-width:880px){
  .panes{grid-template-columns:1fr;gap:22px}
  .rail{position:static;max-height:none;flex-direction:row;flex-wrap:wrap;gap:6px}
  .rail-head{width:100%;padding-bottom:2px}
  .rail a{border-left:none;border:1px solid var(--rule);padding:6px 11px}
  .cap{flex-direction:column;gap:12px}
  .cap-meta{align-items:flex-start;text-align:left;flex-direction:row;gap:14px}
}
@media (max-width:560px){
  .row{grid-template-columns:minmax(0,1fr)}
  .row .m{grid-row:auto;grid-column:1;text-align:left;display:flex;gap:14px}
}
</style>

<div class="shell">
  <header class="masthead">
    <p class="eyebrow">Claude &middot; chat history</p>
    <h1>Conversation Archive</h1>
    <p class="lede" id="lede"></p>
    <dl class="colophon" id="colophon"></dl>
  </header>

  <div id="notice"></div>

  <div class="controls">
    <div class="search">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
      <input id="q" type="search" placeholder="Search titles, previews, keywords" aria-label="Search conversations">
    </div>
    <label class="pick">Order
      <select id="order">
        <option value="size">Largest topics</option>
        <option value="recent">Most recent</option>
        <option value="alpha">A&ndash;Z</option>
      </select>
    </label>
    <button class="ghost" id="toggle-all" type="button">Collapse all</button>
  </div>

  <div class="panes">
    <nav class="rail" id="rail" aria-label="Topics"></nav>
    <main class="groups" id="groups"></main>
  </div>

  <footer>
    Grouped by term overlap across titles and message text &middot; generated <span id="gen"></span>
  </footer>
</div>

<script id="payload" type="application/json">__DATA__</script>
<script>
(function(){
  "use strict";
  var DATA = JSON.parse(document.getElementById("payload").textContent);
  var S = DATA.stats;

  function esc(s){
    return String(s == null ? "" : s)
      .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
  }
  function plural(n, one, many){ return n + " " + (n === 1 ? one : many); }

  /* ---- masthead ---- */
  var span = (S.first && S.last) ? (S.first + " to " + S.last) : "an unknown span";
  document.getElementById("lede").textContent =
    plural(S.conversations, "conversation", "conversations") + " spanning " + span +
    ", sorted into " + plural(S.groups, "topic", "topics") +
    (S.standalone ? " plus " + plural(S.standalone, "one-off", "one-offs") : "") + ".";

  var colo = [
    ["Conversations", S.conversations],
    ["Messages", S.messages.toLocaleString()],
    ["Topics", S.groups],
    ["One-offs", S.standalone]
  ];
  document.getElementById("colophon").innerHTML = colo.map(function(p){
    return "<div><dt>" + esc(p[0]) + "</dt><dd>" + esc(p[1]) + "</dd></div>";
  }).join("");
  document.getElementById("gen").textContent = S.generated;

  if (S.sample) {
    document.getElementById("notice").innerHTML =
      '<div class="notice"><strong>Preview built from sample data.</strong> ' +
      'These conversations are synthetic, generated to show the grouping and layout. ' +
      'Re-run the script on your real export and this page fills with your actual history.</div>';
  }

  /* ---- render ---- */
  DATA.groups.forEach(function(g, i){ g._id = "topic-" + i; });

  var groupsEl = document.getElementById("groups");
  var railEl = document.getElementById("rail");

  function sorted(mode){
    var list = DATA.groups.slice();
    var solo = list.filter(function(g){ return g.standalone; });
    var real = list.filter(function(g){ return !g.standalone; });
    if (mode === "alpha") {
      real.sort(function(a,b){ return a.label.localeCompare(b.label); });
    } else if (mode === "recent") {
      real.sort(function(a,b){ return (b.last || "").localeCompare(a.last || ""); });
    } else {
      real.sort(function(a,b){ return b.count - a.count; });
    }
    return real.concat(solo);
  }

  function rowHTML(c, hay){
    var when = c.updated || c.created || "";
    var title = c.url
      ? '<a href="' + esc(c.url) + '" target="_blank" rel="noopener">' + esc(c.title) + "</a>"
      : esc(c.title);
    return '<article class="row" data-hay="' + esc(hay) + '">' +
      '<h3 class="t">' + title + "</h3>" +
      (c.preview ? '<p class="p">' + esc(c.preview) + "</p>" : '<p class="p"></p>') +
      '<div class="m"><span>' + esc(when) + "</span><span>" +
      plural(c.messages, "msg", "msgs") + "</span></div>" +
      "</article>";
  }

  function groupHTML(g){
    var keyBlob = " " + g.label.toLowerCase() + " " + g.keywords.join(" ");
    var rows = g.conversations.map(function(c){
      var hay = (c.title + " " + c.preview + keyBlob).toLowerCase();
      return rowHTML(c, hay);
    }).join("");
    var range = (g.first && g.last)
      ? (g.first === g.last ? g.first : g.first + " &ndash; " + g.last) : "";
    var keys = g.keywords.length
      ? '<ul class="keys">' + g.keywords.slice(0,6).map(function(k){
          return "<li>" + esc(k) + "</li>"; }).join("") + "</ul>"
      : "";
    var blurb = g.standalone
      ? '<ul class="keys"><li>no close match to another conversation</li></ul>' : keys;

    return '<details class="group" id="' + g._id + '" open>' +
      '<summary class="cap">' +
        '<div class="cap-main"><h2>' +
          '<svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M4 2l4 4-4 4"/></svg> ' +
          esc(g.label) + "</h2>" + blurb + "</div>" +
        '<div class="cap-meta">' +
          '<span class="count"><span class="shown">' + g.count + "</span>" +
          "<span class='of'></span></span>" +
          "<span>" + plural(g.messages, "message", "messages") + "</span>" +
          (range ? "<span>" + range + "</span>" : "") +
        "</div>" +
      "</summary>" +
      '<div class="rows">' + rows + "</div>" +
    "</details>";
  }

  function railHTML(g){
    return '<a href="#' + g._id + '" data-for="' + g._id + '"' +
      (g.standalone ? ' class="solo"' : "") + ">" +
      "<span>" + esc(g.label) + '</span><span class="n">' + g.count + "</span></a>";
  }

  function build(){
    var list = sorted(document.getElementById("order").value);
    groupsEl.innerHTML = list.map(groupHTML).join("") +
      '<div class="empty" id="empty" hidden>' +
      '<p class="big">Nothing matches that search.</p>' +
      "<p>Try a shorter word, or clear the box to see everything.</p></div>";
    railEl.innerHTML = '<div class="rail-head">Topics</div>' + list.map(railHTML).join("");
    filter();
  }

  function filter(){
    var needle = document.getElementById("q").value.trim().toLowerCase();
    var anyShown = false;
    DATA.groups.forEach(function(g){
      var sec = document.getElementById(g._id);
      if (!sec) return;
      var shown = 0;
      var rows = sec.querySelectorAll(".row");
      for (var i = 0; i < rows.length; i++){
        var hit = !needle || rows[i].getAttribute("data-hay").indexOf(needle) !== -1;
        rows[i].hidden = !hit;
        if (hit) shown++;
      }
      sec.hidden = shown === 0;
      if (shown) anyShown = true;
      sec.querySelector(".shown").textContent = shown;
      sec.querySelector(".of").textContent = (needle && shown !== g.count) ? " / " + g.count : "";
      var railItem = railEl.querySelector('[data-for="' + g._id + '"]');
      if (railItem){
        railItem.hidden = shown === 0;
        railItem.querySelector(".n").textContent = shown;
      }
      if (needle && shown) sec.open = true;
    });
    var empty = document.getElementById("empty");
    if (empty) empty.hidden = anyShown;
  }

  var allOpen = true;
  document.getElementById("toggle-all").addEventListener("click", function(){
    allOpen = !allOpen;
    var all = groupsEl.querySelectorAll(".group");
    for (var i = 0; i < all.length; i++) all[i].open = allOpen;
    this.textContent = allOpen ? "Collapse all" : "Expand all";
  });
  document.getElementById("q").addEventListener("input", filter);
  document.getElementById("order").addEventListener("change", function(){
    build();
    allOpen = true;
    document.getElementById("toggle-all").textContent = "Collapse all";
  });

  build();
})();
</script>
"""


def render_html(payload):
    blob = json.dumps(payload, ensure_ascii=False)
    # keep the JSON from terminating the host <script> element
    blob = blob.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return PAGE.replace("__DATA__", blob)


if __name__ == "__main__":
    main()
