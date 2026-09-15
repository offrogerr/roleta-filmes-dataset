import pandas as pd
import json
import urllib.request
import gzip
import shutil
import os

URL_BASICS = "https://datasets.imdbws.com/title.basics.tsv.gz"
URL_RATINGS = "https://datasets.imdbws.com/title.ratings.tsv.gz"

def baixar_e_descompactar(url, nome_saida):
    nome_gz = nome_saida + ".gz"
    print(f"Baixando {url}...")
    urllib.request.urlretrieve(url, nome_gz)
    print(f"Descompactando {nome_gz}...")
    with gzip.open(nome_gz, 'rb') as f_in:
        with open(nome_saida, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(nome_gz)

baixar_e_descompactar(URL_BASICS, "title.basics.tsv")
baixar_e_descompactar(URL_RATINGS, "title.ratings.tsv")

print("Carregando title.basics.tsv...")
basics = pd.read_csv(
    "title.basics.tsv", sep="\t", na_values="\\N",
    dtype={"startYear": "str"}, low_memory=False
)

print("Carregando title.ratings.tsv...")
ratings = pd.read_csv("title.ratings.tsv", sep="\t", na_values="\\N")

print("Filtrando apenas filmes...")
filmes = basics[
    (basics["titleType"] == "movie") &
    (basics["isAdult"] == 0) &
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

print("Montando o arquivo final...")
resultado = []
for posicao, (_, row) in enumerate(top250.iterrows(), start=1):
    resultado.append({
        "posicao": posicao,
        "imdbId": row["tconst"],
        "titulo": row["primaryTitle"],
        "ano": int(row["startYear"]),
        "generos": row["genres"].split(",") if pd.notna(row["genres"]) else [],
        "notaImdb": round(row["averageRating"], 1),
        "numVotos": int(row["numVotes"]),
    })

# Salva direto na raiz deste repositório (não precisa mais de "../")
with open("top250_imdb.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"Pronto! {len(resultado)} filmes salvos em top250_imdb.json")

os.remove("title.basics.tsv")
os.remove("title.ratings.tsv")