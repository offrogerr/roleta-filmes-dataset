# 🎬 Roleta de Filmes — Dataset (Top 250 IMDb)

Este repositório contém uma versão processada e simplificada do **Top 250 de filmes do IMDb**, atualizada automaticamente toda semana, pronta para uso em qualquer aplicação.

## O que é este projeto

Os dados brutos do IMDb (disponíveis em [datasets.imdbws.com](https://datasets.imdbws.com)) trazem informações de **milhões de títulos** (filmes, séries, episódios), sem o cálculo do ranking Top 250 pronto. Este repositório automatiza esse processo:

1. Baixa os datasets oficiais do IMDb
2. Filtra apenas filmes (excluindo séries, episódios e conteúdo adulto)
3. Calcula o ranking usando a mesma **fórmula de média ponderada** que o próprio IMDb utiliza (leva em conta nota média e número de votos)
4. Publica o resultado em `top250_imdb.json`, sempre atualizado

## Atualização automática

Um workflow do GitHub Actions roda **semanalmente**, refazendo todo o processo e commitando o resultado aqui, sem intervenção manual.

## Formato do arquivo (`top250_imdb.json`)

Uma lista com 250 objetos, cada um representando um filme:

```json
{
  "posicao": 1,
  "imdbId": "tt0111161",
  "titulo": "The Shawshank Redemption",
  "ano": 1994,
  "generos": ["Drama"],
  "notaImdb": 9.3,
  "numVotos": 3000000
}
```

| Campo | Descrição |
|---|---|
| `posicao` | Posição no ranking (1 = melhor) |
| `imdbId` | ID oficial do filme no IMDb (compatível com TMDb e outras APIs) |
| `titulo` | Título original |
| `ano` | Ano de lançamento |
| `generos` | Lista de gêneros |
| `notaImdb` | Nota média (0 a 10) |
| `numVotos` | Número de votos |

## Como usar em outros projetos

Basta consumir o arquivo diretamente pela URL "raw" do GitHub: https://raw.githubusercontent.com/offrogerr/roleta-filmes-dataset/main/top250_imdb.json



Qualquer app, script ou site pode buscar esse link para sempre ter acesso ao Top 250 atualizado, sem precisar processar os dados brutos do IMDb por conta própria.

## Origem deste projeto

Este dataset foi criado originalmente para o app [Roleta de Filmes](#) (uma roleta para sortear filmes para assistir), mas foi desacoplado para ser reutilizável em qualquer outro projeto que precise desses dados.

## Licença

O código/processo deste repositório está sob licença MIT. Os dados brutos utilizados como fonte pertencem ao IMDb, sob os termos de uso não-comercial descritos em [imdb.com/interfaces](https://www.imdb.com/interfaces/).