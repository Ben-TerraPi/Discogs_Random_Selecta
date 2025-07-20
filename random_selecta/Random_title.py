import streamlit as st
from datetime import datetime
from list_styles import genres_styles
from utils import random_youtube


#>>>>>>>>>>>>>>>>>>>>> Streamlit page

st.set_page_config(
    page_title="Discogs Random Selecta",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

#>>>>>>>>>>>>>>>>>>>>>> Streamlit sidebar

with st.sidebar:
    st.image("image/logo.jpg")
    st.divider()
    st.caption("About:")
    st.write("Discogs Random Selecta is an application developped to query the Discogs database.")
    st.write("")
    st.write("It renders a random album infos from your selections and displays an embedded music video. If no video is available, it will search directly on YouTube to find the most relevant result.")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Title

st.write(f'#### Digging for tracks on Discogs database!')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Search

col1, col2, col3 = st.columns([3,3,3])

with col1:

    genre = st.selectbox("Select genre  ( Sort by number of releases )",
                        list(genres_styles.keys()),
                        index=None
                        )

with col2:

    styles = genres_styles.get(genre, None)

    style = st.selectbox("Select style  ( Optional )",
                        styles,
                        index=None
                        )

with col3:

    current_year = datetime.now().year
    years = list(range(current_year, 1950, -1))

    year = st.selectbox("Select release year ( Optional )",
                        years,
                        index=None,
                        )

st.write("")

if st.button("Generate Track", type="primary", use_container_width=True):
    if genre is None:
        st.warning("Please select a genre before generating.")
    else:   # Appel de la fonction random_youtube
        if style is None and year is None:
            result = random_youtube(genre=genre)
        elif style is None:
            result = random_youtube(genre=genre, year=year)
        elif year is None:
            result = random_youtube(genre=genre, style=style)
        else:
            result = random_youtube(genre=genre, style=style, year=year)
        
        if not result:
            st.warning("An error occurred, no valid result returned.")
        else:
    # Accès aux infos
            title = result['title']
            artist = result['artist']
            year = result['year']
            image = result['image']
            url = result['url']
            link = result['link']
            discogs_videos = result['discogs_videos']
            youtube_results = result['youtube_results']
            test = result['nb_results']
            genres = result['genres']
            styles = result['styles']
            labels = result['labels']
            tracklist = result['tracklist']
            notes = result['notes']
            formats = result['formats']

            if test == 0:
                st.warning("No result, choose a different year")
            elif title:
                st.write("")
                col1, col2, col3 = st.columns([3,3,3])
                with col1:
                    st.write(f"Album found from **{test}** results:")

                with col2:
                    st.write(f"[Discogs Release Page]({link})")

                with col3:
                    st.write(f"[YouTube Search Results]({url})")

                col1, col2 = st.columns([0.3, 0.7], gap="large")
                with col1: 
                    st.write(f"#### **{title}**")

                    # Suppression des doublons de labels (même nom et même url)
                    seen = set()
                    unique_labels = []
                    for label in result['labels']:
                        key = (label['name'], label['url'])
                        if key not in seen:
                            unique_labels.append(label)
                            seen.add(key)
                    
                    label_links = []
                    for label in unique_labels:
                        if label['url']:
                            label_links.append(f"[{label['name']}]({label['url']})")
                        else:
                            label_links.append(label['name'])
                    label_str = ", ".join(label_links)
                    st.write(f"**Label**: {label_str}", unsafe_allow_html=True)


                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        st.image("image/vinyl_discogs.jpg")
                    # if youtube_results:
                    #     st.warning("Most Relevant Youtube Video >>>")
                with col2:
                    if youtube_results:
                        st.warning("Most Relevant Youtube Video >>>")
                    # Gestion des vidéos
                    if discogs_videos:
                        st.video(discogs_videos)
                    elif youtube_results and len(youtube_results) > 0:
                        st.video(youtube_results[0]['url'])
                    else:
                        st.warning(f"No video found for this release. Try [YouTube Search Results]({url})")

            else:
                st.warning("No results found. Try a different selection.")

    genre_str = ", ".join(genres)
    style_str = ", ".join(styles)
    st.write(f"**Genre**: {genre_str} &nbsp; | &nbsp; **Style**: {style_str} &nbsp; | &nbsp; **Year**: {year}", unsafe_allow_html=True)

    if result['tracklist']:
        st.write("**Tracklist :**")
        track_lines = [
            f"{track['position']} - {track['title']} ({track['duration']})"
            for track in result['tracklist']
        ]
        st.write("<br>".join(track_lines), unsafe_allow_html=True)