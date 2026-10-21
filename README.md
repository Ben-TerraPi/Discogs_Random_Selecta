![image](https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Discogs_logo_black.svg/1920px-Discogs_logo_black.svg.png)

Discogs est l'une des plus grandes bases de données en ligne répertoriant les productions musicales de tous genres publiées sur tous les types de supports, vinyles, CD, cassettes audio, 78 tours, etc.

En 2025, tous genres et formats confondus, le site catalogue plus de 18 millions de productions. Il propose aussi des informations sur plus de 9 millions d'artistes et plus de 2 millions de labels.

Le contenu de la base de données est généré par les utilisateurs et a été décrit par The New York Times comme étant « semblable à Wikipédia ».

SITE: https://www.discogs.com/

API: https://api.discogs.com/

DOCS:

https://www.discogs.com/developers/

https://python3-discogs-client.readthedocs.io/en/latest/index.html


Étant passionné de musique et collectionneur de vinyles. Discogs est un site où je passe beaucoup de temps. Suite à une formation de Data Analyst, il était évident que, pour mon premier projet personnel, j'allais combiner ces deux centres d'intérêt.

Au départ, ma volonté était de pouvoir extraire une liste de ma collection en utilisant Python et l'API de Discogs (voir [Discogs_collection](https://github.com/Ben-TerraPi/Discogs_collection)). 

Il s'est vite avéré que j'avais envie d'aller plus loin.

# Fonction de départ

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


# Fonction random_album

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


# Fonction random_selecta

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

# > [random_selecta](https://github.com/Ben-TerraPi/Discogs/tree/main/random_selecta) : 

Dans ce dossier on retrouve:

* [utils.py](https://github.com/Ben-TerraPi/Discogs/blob/main/src/utils.py), regroupe toutes mes fonctions issues de la même base.

* [Random_title.py](https://github.com/Ben-TerraPi/Discogs/blob/main/src/random_title.py), sert au lancement de l'application Streamlit.

* [list_styles.py](https://github.com/Ben-TerraPi/Discogs/blob/main/src/dict_styles.py), dans lequelle j'ai créé les listes et un dictionnaire pour chaques styles musicaux présent dans chaques genres musicaux référencés par Discogs, cela sera intégré pour les selectbox sur streamlit.

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
Est créé le [tableau_genre.csv](https://github.com/Ben-TerraPi/Discogs/blob/main/data/tableau_genre.csv)

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

Arrivé à ce stade je vous laisse analyser la struture du fichier streamlit [Random_title.py](https://github.com/Ben-TerraPi/Discogs/blob/main/src/random_title.py)  et tester le résultat:

https://discogs-random-selecta.streamlit.app/















