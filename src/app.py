import streamlit as st
from datetime import datetime
from dict_styles import genres_styles
from helpers import draw, list_folders, load_seen, save_seen

st.set_page_config(page_title="Discogs Random Selecta", page_icon="🎧",
                   layout="wide", initial_sidebar_state="expanded")

# ---------- État de session : survit aux reruns de Streamlit ----------
ss = st.session_state
ss.setdefault("current", None)               # résultat affiché
ss.setdefault("history", [])                 # derniers résultats (le plus récent en premier)
ss.setdefault("seen", load_seen())           # IDs déjà tirés (persistés dans data/seen_ids.json)

@st.cache_data(ttl=600, show_spinner=False)
def cached_folders(username):
    return list_folders(username or None)


# ---------- Sidebar ----------
with st.sidebar:
    st.image("image/logo.jpg")
    st.divider()
    st.caption("About:")
    st.write("Discogs Random Selecta queries the Discogs database and shows a random release "
             "with an embedded video (Discogs first, YouTube as a fallback).")
    st.divider()
    st.caption("History (click to reopen)")
    for i, r in enumerate(ss.history[:15]):
        if st.button(f"{r['artist']} – {r['title']}", key=f"hist_{i}", use_container_width=True):
            ss.current = r
    if st.button("Reset seen albums"):
        ss.seen = set()
        save_seen(ss.seen)

# ---------- Formulaire ----------
st.write("#### Digging for tracks on Discogs database!")
mode_label = st.radio("Source", ["Discogs database", "User collection"], horizontal=True)
mode = {"Discogs database": "database", "User collection": "collection"}[mode_label]

genre = style = year = username = None
folder_id = 0
if mode == "database":
    c1, c2, c3 = st.columns(3)
    genre = c1.selectbox("Select genre", list(genres_styles.keys()), index=None)
    style = c2.selectbox("Select style (optional)", genres_styles.get(genre, []), index=None)
    year = c3.selectbox("Select release year (optional)",
                        list(range(datetime.now().year, 1950, -1)), index=None)
else:
    username = st.text_input("Discogs username (empty = creator collection)",
                             help="Visible in the profile URL: discogs.com/user/<username>. "
                                  "The collection must be public.")
    try:
        folders = cached_folders(username)
        choice = st.selectbox("Folder", folders, format_func=lambda f: f"{f[1]} ({f[2]})")
        folder_id = choice[0]
    except Exception as e:
        st.warning(f"Could not load folders: {e}")

# ---------- Action ----------
if st.button("Generate Track", type="primary", use_container_width=True):
    if mode == "database" and genre is None:
        st.warning("Please select a genre before generating.")
    else:
        with st.spinner("Digging..."):
            try:
                result = draw(mode, ss.seen, genre=genre, style=style,
                              year=year, username=username,
                              folder_id=folder_id)
            except Exception as e:             # à affiner (HTTPError 429, 404...)
                result = None
                st.error(f"Discogs error: {e}")
        if result:
            ss.current = result
            ss.history.insert(0, result)
            ss.seen.add(result["id"])
            save_seen(ss.seen)
        elif result is None:
            st.warning("No result: empty or private collection, or no match for this selection.")

# ---------- Affichage (toujours depuis ss.current, donc stable aux reruns) ----------
r = ss.current
if r:
    c1, c2, c3 = st.columns(3)
    c1.write(f"Album found from **{r['nb_results']}** results")
    c2.write(f"[Discogs Release Page]({r['link']})")
    c3.write(f"[YouTube Search Results]({r['url']})")

    left, right = st.columns([0.3, 0.7], gap="large")
    with left:
        st.write(f"#### {r['artist']} – {r['title']}")
        labels = {(l["name"], l["url"]) for l in r["labels"]}
        st.write("**Label**: " + ", ".join(f"[{n}]({u})" if u else n for n, u in sorted(labels)))
        st.image(r["image"], use_container_width=True)
    with right:
        if r["discogs_videos"]:
            st.video(r["discogs_videos"])
        elif r["youtube_results"]:
            st.warning("Most relevant YouTube video >>>")
            st.video(r["youtube_results"][0]["url"])
        else:
            st.warning(f"No video found. Try [YouTube Search Results]({r['url']})")

    st.write(f"**Genre**: {', '.join(r['genres'])} | **Style**: {', '.join(r['styles'])} "
             f"| **Year**: {r['year']}")
    if r["tracklist"]:
        with st.expander("Tracklist", expanded=True):
            st.table([{"#": t["position"], "Title": t["title"], "Duration": t["duration"]}
                      for t in r["tracklist"]])
