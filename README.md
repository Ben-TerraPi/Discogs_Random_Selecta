# À propos :  ![image](https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Discogs_logo_black.svg/1920px-Discogs_logo_black.svg.png)

Discogs est l'une des plus grandes bases de données en ligne répertoriant les productions musicales de tous genres publiées sur tous les types de supports, vinyles, CD, cassettes audio, 78 tours, etc.

En 2025, tous genres et formats confondus, le site catalogue plus de 18 millions de productions. Il propose aussi des informations sur plus de 9 millions d'artistes et plus de 2 millions de labels.

Le contenu de la base de données est généré par les utilisateurs et a été décrit par The New York Times comme étant « semblable à Wikipédia ».

SITE: https://www.discogs.com/

API: https://api.discogs.com/

DOCS:

https://www.discogs.com/developers/

https://python3-discogs-client.readthedocs.io/en/latest/index.html


Étant passionné de musique et collectionneur de vinyles. Discogs est un site où je passe beaucoup de temps. Suite à une formation de Data Analyst, il était évident que, pour mon premier projet personnel, j'allais combiner ces deux centres d'intérêt.

Au départ, ma volonté était de simplement lister ma collection en utilisant Python et l'API de Discogs. Il s'est vite avéré que j'avais envie d'aller plus loin.

3 étapes, 3 dossiers.


# [my_collection](https://github.com/Ben-TerraPi/Discogs/tree/main/my_collection) : 1er dossier

## [scrap_discogs.py](https://github.com/Ben-TerraPi/Discogs/tree/main/my_collection/scrap_discogs.py)

J'ai commencé en utilisant **google collab** avec cette première ligne de code:

`pip install python3-discogs-client`

C'était le début d'un projet qui m'a passionné.

### Discogs Client & User token

Je me suis connecté à mon compte grâce à la génération d'un **token** développeur qui me permet de naviguer dans l'API discogs.

```
import discogs_client

d = discogs_client.Client("ExampleApplication/0.1", user_token= "secret")
me = d.identity()
```

### Mon compte

Avec `print(dir(me))` j'avais les attributs disponible pour mon compte client:

['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_known_invalid_keys', 'changes', 'client', 'collection_folders', 'collection_items', 'collection_value', 'data', 'delete', 'fetch', 'home_page', 'id', 'inventory', 'lists', 'location', 'name', 'num_collection', 'num_lists', 'num_wantlist', 'orders', 'previous_request', 'profile', 'rank', 'rating_avg', 'refresh', 'registered', 'releases_contributed', 'save', 'url', 'username', 'wantlist']

```
print(me.id)
print(me.location)
print(me.name)
print(me.url)
print(me.collection_folders)
```
A savoir:

* 2794711
* Rennes
* TerraPi
* https://www.discogs.com/user/Little.Red.Roquet
* [<CollectionFolder 0 'All'>, <CollectionFolder 1 'Uncategorized'>, ...

Avoir la liste de tous mes vinyles était aussi simple que cela:

```
data = []
for item in me.collection_folders[0].releases:
      data.append(item)
```
### Import de ma Collection

Il était temps de créer le tableau .csv avec les informations de mon choix:

| id  | title | artist | year | genre | style | master_id | release_country | labels | format | rating | have | want | url | image_url |
|-----|-------|--------|------|-------|-------|-----------|-----------------|--------|--------|--------|------|------|-----|-----------|

```
def export_collection_to_csv(me):
    # list collection
    data = []
    for item in me.collection_folders[0].releases:
        data.append(item)

    # Import de ma Collection

    # Création du CSV
    with open('collection.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'id',
            'title',
            'artist',
            'year',
            'genre',
            'style',
            'master_id',
            'release_country',
            'labels',
            'format',
            'rating',
            'have',
            'want',
            'url',
            'image_url'
        ])

        for release in data:

            release_data = release.release

            artist_name = release_data.artists[0].name
            artist_name = re.sub(r'\(\d+\)', '', artist_name).strip()
            genres = ", ".join(release_data.genres) if release_data.genres else "N/A"
            styles = ", ".join(release_data.styles) if release_data.styles else "N/A"
            master_id = release_data.master.id if release_data.master else "N/A"
            labels = ", ".join([label.name for label in release_data.labels]) if release_data.labels else "N/A"
            formats = ", ".join([", ".join(fmt['descriptions']) for fmt in release_data.formats]) if release_data.formats else "N/A"
            image_url = release_data.images[0]["uri"] if release_data.images else "N/A"

            writer.writerow([
                release.id,
                release_data.title,
                artist_name,
                release_data.year,
                genres,
                styles,
                master_id,
                release_data.country,
                labels,
                formats,
                release_data.community.rating.average,
                release_data.community.have,
                release_data.community.want,
                release_data.url,
                image_url
            ])

    print("Collection importée dans 'collection.csv'.")
```
Mon tableau était créé : [collection.csv](https://github.com/Ben-TerraPi/Discogs/blob/main/collection.csv)

## [Stats_coll.py](https://github.com/Ben-TerraPi/Discogs/tree/main/my_collection/Stats_coll.py)

Ayant découvert le commentaire **#%%** permettant des cellules de code Jupyter-like sur **VS code** j'arrète de travailler avec **google collab** et fais des tests dans cette nouvelle fenêtre interactive.

## [tracks.py](https://github.com/Ben-TerraPi/Discogs/tree/main/my_collection/tracks.py)

En plus du fichier complet de mes albums, je souhaite maintenant, à des fins d'analyses et de classement ultérieur, créer un fichier regroupant l'intégralité des morceaux de chaque album dans un tableau plus sommaire.

| album_id  | artist | album | track_id | title |
|-----------|--------|-------|----------|-------|

Le principe est le même que pour l'importation du précédent tableau, mais la tracklist est une ligne de caractères unique, comme on peut le constater sur cette nouvelle importation de données :[collection_tracks.csv](https://github.com/Ben-TerraPi/Discogs/blob/main/collection_tracks.csv)

Pour résoudre ce problème, j'ai codé une fonction pour extraire le nom de chaque morceau dans un nouveau DataFrame et j'en profite pour leur créer un ID unique.

```
def extract_tracks(row):
    tracklist_str = row["tracklist"]
    pattern = r"<Track '([^']+)' '([^']+)'>"  
    matches = re.findall(pattern, tracklist_str)
    new_rows = []
    for track_id, track_name in matches:
        new_rows.append({
            "album_id": row["id"],
            "artist": row["artist"],
            "album": row["album"],
            "track_id": f"{row['id']}_{track_id}",
            "title": track_name
        })
    
    return new_rows
```
Ensuite je peux créer mon csv

```
def create_my_tracks_csv(df, output_file="my_tracks.csv"):
    """Transforme et reconstruit le DataFrame en utilisant les données de pistes extraites,
    puis enregistre le résultat dans un fichier CSV."""

    tracklist_data = []
    for index, row in df.iterrows():
        try:
            tracklist_data.extend(extract_tracks(row))
        except Exception as e:
            print(f"Erreur {index}: {e}")

    df_tracklist = pd.DataFrame(tracklist_data)

    df_tracklist.to_csv(output_file, index=False)

    print(f"tracks importée dans {output_file}")
```
Le résultat: [my_tracks.csv](https://github.com/Ben-TerraPi/Discogs/blob/main/my_tracks.csv)

# [export_gbq.py](https://github.com/Ben-TerraPi/Discogs/blob/main/export_gbq.py)

Pour sauvegarder et analyser ces nouveaux tableaux avec SQL je souhaite les exporter vers BigQuery.

```
import pandas as pd
import pandas_gbq

collection = pd.read_csv("collection.csv")
collection_tracks = pd.read_csv("collection_tracks.csv")
my_tracks = pd.read_csv("my_tracks.csv")
tableau_genre = pd.read_csv("tableau_genre.csv")

project_id = "discogs-random-selecta"
dataset = "my_data"

dfs = [collection,
       collection_tracks,
       my_tracks,
       tableau_genre
       ]

def get_var_name(var):
    for name, value in globals().items():
        if value is var:
            return name

for df in dfs:
  table_id = f"{project_id}.{dataset}.{get_var_name(df)}"
  pandas_gbq.to_gbq(df, table_id, project_id)
  
print("tableaux exportés")

```

Les étapes de travail sur BigQuery sont visibles sur cette page [Notion](https://www.notion.so/BigQuerry-DISCOGS-17f3c2440f4d8058b48ccba890050601?pvs=4)

Le dashboard réalisé est visible directement sur [Looker Studio](https://lookerstudio.google.com/reporting/9555dbd8-4aef-4ba4-8924-44840306f7b6)


# [tests](https://github.com/Ben-TerraPi/Discogs/tree/main/tests) : 2ème dossier

J'utilise ce dossier pour tester différentes recherches et fonctions.

## Fonction de départ

Cette première fonction répond au besoin de rechercher l'ensemble des albums d'un genre précis et d'une année donnée.

```
def list_albums(genre, year):
    list = []
    results = d.search(genre=genre,year=year)
    for el in results:
        list.append(el)
    return pd.DataFrame(list)
```

En testant `list_albums("Hip Hop",1986)` le résultat est de **4156** lignes avec en ligne 0 <Master 42835 'Whodini - Funky Beat'>

Pourquoi un dataframe?
Un simple `return results` ne donne comme résultats qu'un message semblable à celui-ci: <discogs_client.models.MixedPaginatedList at 0x1bbcb513230>


## Fonction random_album

Maintenant que j'ai une liste exhaustive selon mes critères et que j'ai compris que mes recherches sont regroupées en plusieurs pages, j'aimerais, à l'image d'un bac à vinyles que l'on fouille, tomber sur un album aléatoirement.

```
import random 

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
```

Cette fois-ci je n'ai plus qu'un seul résultat comme par exemple: <Release 7261574 'Run DMC* - Walk This Way'>


## Fonction random_selecta

C'est bien d'avoir un album aléatoire, c'est encore mieux de pouvoir l'écouter!

```
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
```

Grâce à cette MAJ j'ai plus d'informations sur l'album sous forme de liens.

Exemple `random_selecta('hip hop', 'Boom Bap', 1986)` avec le résultat:

('Beastie Boys - (You Gotta) Fight For Your Right (To Party!)',
'https://i.discogs.com/9fJEL5bjdRIgKyxJjhK_R9TWVxgWYkBAebUmZA8IsrU/rs:fit/g:sm/q:90/h:600/w:584/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTY0MTA2/OC0xNjEwNjY3NDIx/LTEyMDEuanBlZw.jpeg',
 
'https://www.youtube.com/results?search_query=beastie+boys+-+(you+gotta)+fight+for+your+right+(to+party!)',
 
'https://www.discogs.com/master/1007458-Beastie-Boys-You-Gotta-Fight-For-Your-Right-To-Party')


# Création d'un STREAMLIT 

Le but est d'avoir une interface utilisateur simple où l'on sélectionne un **genre**, un **style** et une **année** avant de générer la requête.

Au cours de ma formation de Data Analyst, j'ai réalisé un projet sur Streamlit, et pour ce que je souhaite faire, cette application est suffisante.

Je reste donc sur VS Code et crée un **repository GitHub** en lien avec mon application Streamlit.


## Set-up [.streamlit](https://github.com/Ben-TerraPi/Discogs/tree/main/.streamlit)

Rien de compliqué ici, le fichier **config.toml** pour la charte graphique mais surtout un fichier **secrets.toml** caché par **.gitignore** pour garder privé ma clé API discogs et une autre clé YouTube.

```
token = st.secrets["token"]["user_token"]

d = discogs_client.Client("ExampleApplication/0.1", user_token= token)

api_key = st.secrets["youtube"]["api_key"]
```

Et [requirements.txt](https://github.com/Ben-TerraPi/Discogs/blob/main/requirements.txt) à la racine du projet.

# [random_selecta](https://github.com/Ben-TerraPi/Discogs/tree/main/random_selecta) : 3ème dossier

Dans ce dossier on retrouve:

* [utils.py](https://github.com/Ben-TerraPi/Discogs/blob/main/random_selecta/utils.py), regroupe toutes mes fonctions issues de la même base.

* [Random_title.py](https://github.com/Ben-TerraPi/Discogs/blob/main/random_selecta/Random_title.py), sert au lancement de l'application Streamlit.

* [list_styles.py](https://github.com/Ben-TerraPi/Discogs/blob/main/random_selecta/list_styles.py), dans lequelle j'ai créé les listes et un dictionnaire pour chaques styles musicaux présent dans chaques genres musicaux référencés par Discogs, cela sera intégré pour les selectbox sur streamlit.

```
genres_styles = {
    "Rock" : rock_style,
    "Electronic" : electronic_style,
    "Pop" : pop_style,
    "Folk, World, & Country" : world_style,
    "Jazz" : jazz_style,
    "Funk / Soul" : funk_soul_style,
    "Classical" : classical_style,
    "Hip Hop" : hip_hop_style,
    "Latin" : latin_style,
    "Stage & Screen" : stage_style,
    "Reggae" : reggae_style,
    "Blues" : blues_style,
    "Non-Music" : non_music_style,
    "Children's" : children_style,
    "Brass & Military " : military_style
    }

#Création tableau
tableau_genre = pd.DataFrame.from_dict(genres_styles, orient='index').transpose()

tableau_genre.to_csv("tableau_genre.csv")
```
Est créé le [tableau_genre.csv](https://github.com/Ben-TerraPi/Discogs/blob/main/tableau_genre.csv)

## Fonction final pour Streamlit

```
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
    image = "image/default_cover.png" 
    url = None
    link = None
    discogs_videos = None
    youtube_results = []
    
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
            if hasattr(album, 'images') and album.images:
                image = album.images[0]["uri"]
            link = album.url

            # Recherche Youtube
            str = title.lower()
            str2 = str.replace(" ", "+")
            str3 = str2.replace("&", "and")
            url = f'https://www.youtube.com/results?search_query={str3}'

            # Vidéo Discogs
            if hasattr(album, 'videos') and album.videos:
                nb = len(album.videos)
                if nb > 0:
                    key_random = random.randint(0, nb - 1)
                    discogs_videos = album.videos[key_random].url
            else:
                # API YouTube
                youtube = build('youtube', 'v3', developerKey=api_key)
                request = youtube.search().list(
                    part="snippet",
                    q=str3,
                    type="video",
                    maxResults=1
                )
                try:
                    response = request.execute()
                except:
                    response = None

                # Résultats recherche YouTube
                if response:
                    youtube_results = []
                    for item in response['items']:
                        video_id = item['id']['videoId']
                        video_title = item['snippet']['title']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        youtube_results.append({'title': video_title, 'url': video_url})

    return title, image, url, link, discogs_videos, youtube_results, test


print("utils.py loaded successfully")
```

# Conclusion

Arrivé à ce stade je vous laisse analyser la struture du fichier streamlit [Random_title.py](https://github.com/Ben-TerraPi/Discogs/blob/main/random_selecta/Random_title.py)  et tester le résultat:

https://discogs-random-selecta.streamlit.app/















