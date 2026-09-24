import pandas as pd
import json
import urllib.request
import gzip
import shutil
import os
import time
import requests

URL_BASICS = "https://datasets.imdbws.com/title.basics.tsv.gz"
URL_RATINGS = "https://datasets.imdbws.com/title.ratings.tsv.gz"

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_BASE = "https://image.tmdb.org/t/p/w1280"


def baixar_e_descompactar(url, nome_saida):
    nome_gz = nome_saida + ".gz"
    print(f"Baixando {url}...")
    urllib.request.urlretrieve(url, nome_gz)
    print(f"Descompactando {nome_gz}...")
    with gzip.open(nome_gz, 'rb') as f_in:
        with open(nome_saida, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(nome_gz)


def buscar_enriquecimento_tmdb(imdb_id):
    """Busca dados extras na TMDb para um filme, a partir do ID do IMDb."""
    resultado = {
        "tmdbId": None,
        "tituloPtBr": None,
        "sinopse": None,
        "tagline": None,
        "capaUrl": None,
        "fundoUrl": None,
        "dataLancamento": None,
        "idiomaOriginal": None,
        "orcamento": None,
        "bilheteria": None,
        "paisesProducao": [],
        "diretores": [],
        "elencoPrincipal": [],
        "trailerYoutubeId": None,
        "palavrasChave": [],
    }

    try:
        # 1. Descobre o ID da TMDb a partir do ID do IMDb
        resp_find = requests.get(
            f"{TMDB_BASE_URL}/find/{imdb_id}",
            params={"api_key": TMDB_API_KEY, "external_source": "imdb_id"},
            timeout=10,
        )
        dados_find = resp_find.json()
        movie_results = dados_find.get("movie_results", [])
        if not movie_results:
            return resultado

        tmdb_id = movie_results[0]["id"]
        resultado["tmdbId"] = tmdb_id

        # 2. Busca os detalhes completos (com elenco, vídeos e palavras-chave juntos)
        resp_detalhes = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": TMDB_API_KEY,
                "language": "pt-BR",
                "append_to_response": "credits,videos,keywords",
            },
            timeout=10,
        )
        d = resp_detalhes.json()

        resultado["tituloPtBr"] = d.get("title")
        resultado["sinopse"] = d.get("overview")
        resultado["tagline"] = d.get("tagline")
        resultado["dataLancamento"] = d.get("release_date")
        resultado["idiomaOriginal"] = d.get("original_language")
        resultado["orcamento"] = d.get("budget")
        resultado["bilheteria"] = d.get("revenue")

        if d.get("poster_path"):
            resultado["capaUrl"] = TMDB_IMAGE_BASE + d["poster_path"]
        if d.get("backdrop_path"):
            resultado["fundoUrl"] = TMDB_BACKDROP_BASE + d["backdrop_path"]

        resultado["paisesProducao"] = [
            p["name"] for p in d.get("production_countries", [])
        ]

        # Diretores (dentro de credits.crew)
        crew = d.get("credits", {}).get("crew", [])
        resultado["diretores"] = [
            c["name"] for c in crew if c.get("job") == "Director"
        ]

        # Elenco principal (top 8)
        cast = d.get("credits", {}).get("cast", [])[:8]
        resultado["elencoPrincipal"] = [
            {"ator": c["name"], "personagem": c.get("character", "")}
            for c in cast
        ]

        # Trailer do YouTube (primeiro encontrado)
        videos = d.get("videos", {}).get("results", [])
        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                resultado["trailerYoutubeId"] = v["key"]
                break

        # Palavras-chave
        keywords = d.get("keywords", {}).get("keywords", [])
        resultado["palavrasChave"] = [k["name"] for k in keywords]

    except Exception as e:
        print(f"  Aviso: falha ao buscar TMDb para {imdb_id}: {e}")

    return resultado


# ===== 1. Baixar os arquivos mais recentes do IMDb =====
baixar_e_descompactar(URL_BASICS, "title.basics.tsv")
baixar_e_descompactar(URL_RATINGS, "title.ratings.tsv")

# ===== 2. Processar com pandas =====
print("Carregando title.basics.tsv...")
basics = pd.read_csv(
    "title.basics.tsv", sep="\t", na_values="\\N",
    dtype={"startYear": "str"}, low_memory=False
)

print("Carregando title.ratings.tsv...")
ratings = pd.read_csv("title.ratings.tsv", sep="\t", na_values="\\N")

print("Filtrando apenas filmes (tipo 'movie')...")
# Não filtramos mais por isAdult aqui: incluímos o campo no resultado
# e deixamos cada projeto decidir se quer excluir ou não.
filmes = basics[
    (basics["titleType"] == "movie") &
    (basics["startYear"].notna())
].copy()

print("Juntando com as notas...")
filmes = filmes.merge(ratings, on="tconst", how="inner")

M = 25000
filmes_qualificados = filmes[filmes["numVotes"] >= M].copy()
C = filmes_qualificados["averageRating"].mean()

def calcular_wr(row):
    v = row["numVotes"]
    r = row["averageRating"]
    return (v / (v + M)) * r + (M / (v + M)) * C

filmes_qualificados["notaPonderada"] = filmes_qualificados.apply(calcular_wr, axis=1)

print("Ordenando e selecionando o Top 250...")
top250 = filmes_qualificados.sort_values("notaPonderada", ascending=False).head(250)

# ===== 3. Montar o JSON base (dados do IMDb) =====
print("Montando os dados base do IMDb...")
resultado = []
for posicao, (_, row) in enumerate(top250.iterrows(), start=1):
    resultado.append({
        "posicao": posicao,
        "imdbId": row["tconst"],
        "titulo": row["primaryTitle"],
        "tituloOriginal": row["originalTitle"],
        "ano": int(row["startYear"]),
        "generos": row["genres"].split(",") if pd.notna(row["genres"]) else [],
        "duracaoMinutos": int(row["runtimeMinutes"]) if pd.notna(row["runtimeMinutes"]) else None,
        "adulto": bool(row["isAdult"]),
        "notaImdb": round(row["averageRating"], 1),
        "numVotos": int(row["numVotes"]),
    })

# ===== 4. Enriquecer cada filme com dados da TMDb =====
if not TMDB_API_KEY:
    print("AVISO: TMDB_API_KEY não configurada. Pulando enriquecimento TMDb.")
else:
    print("Buscando dados complementares na TMDb (pode demorar alguns minutos)...")
    for i, filme in enumerate(resultado, start=1):
        print(f"  [{i}/250] {filme['titulo']}")
        extras = buscar_enriquecimento_tmdb(filme["imdbId"])
        filme.update(extras)
        time.sleep(0.3)  # evita bater no limite de requisições da TMDb

# ===== 5. Salvar o resultado final =====
with open("top250_imdb.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"Pronto! {len(resultado)} filmes salvos em top250_imdb.json")

# ===== 6. Limpeza =====
os.remove("title.basics.tsv")
os.remove("title.ratings.tsv")