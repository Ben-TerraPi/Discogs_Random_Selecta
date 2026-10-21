import pandas as pd
import random
import discogs_client
import streamlit as st
import re
from googleapiclient.discovery import build

#Discogs Client & User token

token = st.secrets["token"]["user_token"]

d = discogs_client.Client("ExampleApplication/0.1", user_token= token)

#>>>>>>>>>>>>>>>>>>>>>>>>>>YOUTUBE


api_key = st.secrets["youtube"]["api_key"]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>HISTORIQUE DES FONCTIONS
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> N°1 LIST ALBUMS

def list_albums(genre, year):
    list = []
    results = d.search(genre=genre,year=year)
    for el in results:
        list.append(el)
    return pd.DataFrame(list)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>N°2 RANDOM ALBUM

def random_album(genre, year):
    results = d.search(genre=genre,year=year)
    test = len(results)
    if test != 0:
        page_random = random.randint(1,results.pages)
        nb_results = len(results.page(page_random))
        k_random = random.randint(0,nb_results-1)
        return results.page(page_random)[k_random]
    else:
        return "todo"

#>>>>>>>>>>>>>>>>>>>>>>>> N°3 Random SELECTA no videos

def random_selecta(genre,style, year):
    results = d.search(genre=genre,style=style, year=year)
    test = len(results)
    if test != 0:

        #album aléatoire
        page_random = random.randint(1,results.pages)
        nb_results = len(results.page(page_random))
        k_random = random.randint(0,nb_results-1)
        album = results.page(page_random)[k_random]

        #info album
        title = album.title
        image = album.images[0]["uri"]
        link = album.url

        #youtube search
        str = title.lower()
        str2 = str.replace(" ","+")
        url = f'https://www.youtube.com/results?search_query={str2}'
        

        return title, image, url , link 
    else:
        return "todo"

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Nettoyage

def clean_string(s):
    # Nettoie la chaîne
    return re.sub(r'[^a-z0-9 ]', '', s.lower())

def artist_and_title_in_video(video_title, artist, title):
    vt = clean_string(video_title)
    return clean_string(artist) in vt and clean_string(title) in vt

def artist_in_video(video_title, artist):
    return clean_string(artist) in clean_string(video_title)

#>>>>>>>>>>>>>>>>>>>>>>>>>>> FONCTION FINALE randm selecta + youtube

def random_youtube(genre, style= None, year= None):
    # results = d.search(genre=genre, style=style, year=year)
    # test = len(results)

    if style is None and year is None:
        results = d.search(genre=genre)
    elif style is None:
        results = d.search(genre=genre, year=year)
    elif year is None:
        results = d.search(genre=genre, style=style)
    else:
        results = d.search(genre=genre, style=style, year=year)
    test = len(results)

    # Valeurs par défaut
    title = None
    artist = None
    image = "image/default_cover.png" 
    url = None
    link = None
    discogs_videos = None
    youtube_results = []
    year_val = None
    country = None
    genres = []
    styles = []
    labels = []
    tracklist = []
    track_title = None
    notes = None
    formats = []
    
    # Si des résultats sont trouvés
    if test != 0:
        # Album aléatoire
        page_random = random.randint(0, results.pages - 1)
        nb_results = len(results.page(page_random))
        k_random = random.randint(0, nb_results - 1)
        album = results.page(page_random)[k_random]

        if album:

            # Info album
            title = album.title
            artist = album.artists[0].name if hasattr(album, 'artists') and album.artists else ""

            if hasattr(album, 'images') and album.images:
                image = album.images[0]["uri"]

            link = album.url
            year_val = getattr(album, 'year', None)
            country = getattr(album, 'country', None)
            genres = getattr(album, 'genres', [])
            styles = getattr(album, 'styles', [])
            
            if hasattr(album, 'labels'):
                for label in album.labels:
                    labels.append({
                        'name': getattr(label, 'name', ''),
                        'url': getattr(label, 'url', None)
                    })

            if hasattr(album, 'tracklist'):
                for track in album.tracklist:
                    tracklist.append({
                        'position': getattr(track, 'position', ''),
                        'title': getattr(track, 'title', ''),
                        'duration': getattr(track, 'duration', '')
                    })
            notes = getattr(album, 'notes', None)
            formats = [fmt['name'] for fmt in getattr(album, 'formats', [])] if hasattr(album, 'formats') else []
            

            # Recherche Youtube (lien cliquable)
            str = title.lower()
            str2 = str.replace(" ", "+")
            str3 = str2.replace("&", "and")
            url = f'https://www.youtube.com/results?search_query={str3}+audio'

            # Vidéo Discogs par défaut
            if hasattr(album, 'videos') and album.videos:
                nb = len(album.videos)
                if nb > 0:
                    key_random = random.randint(0, nb - 1)
                    discogs_videos = album.videos[key_random].url
            else:
                if tracklist:
                    valid_tracks = [track for track in tracklist if track['title']]
                    if valid_tracks:
                        random_track = random.choice(valid_tracks)
                        track_title = random_track['title']
                if track_title:
                    query = f"{artist} - {track_title} audio"
                else:
                    query = f"{artist} - {title} audio"

                # API YouTube
                youtube = build('youtube', 'v3', developerKey=api_key)
                request = youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=7,
                    order="relevance"
                )
                try:
                    response = request.execute()
                except:
                    response = None
                
                youtube_results = []
                best_artist_and_title = None
                best_artist = None

                # Résultats recherche YouTube
                if response:
                    for item in response['items']:
                        video_id = item['id']['videoId']
                        video_title = item['snippet']['title']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        youtube_results.append({'title': video_title, 'url': video_url})
                        if not best_artist_and_title and artist_and_title_in_video(video_title, artist, title):
                            best_artist_and_title = {'title': video_title, 'url': video_url}
                        elif not best_artist and artist_in_video(video_title, artist):
                            best_artist = {'title': video_title, 'url': video_url} 

                if best_artist_and_title:
                    youtube_results = [best_artist_and_title] + [res for res in youtube_results if res != best_artist_and_title]
                elif best_artist:
                    youtube_results = [best_artist] + [res for res in youtube_results if res != best_artist]

            # dictionnaire des résultats                   
            result = {
                    'title': title,
                    'artist': artist,
                    'year': year_val,
                    'country': country,
                    'genres': genres,
                    'styles': styles,
                    'labels': labels,
                    'tracklist': tracklist,
                    'notes': notes,
                    'formats': formats,
                    'image': image,
                    'url': url,
                    'link': link,
                    'discogs_videos': discogs_videos,
                    'youtube_results': youtube_results,
                    'nb_results': test
                }
    return result


print("utils.py loaded successfully")
