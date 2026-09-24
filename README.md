# 🎬 Roleta de Filmes — Dataset (Top 250 IMDb)

Este repositório contém uma versão processada e enriquecida do **Top 250 de filmes do IMDb**, atualizada automaticamente toda semana, pronta para uso em qualquer aplicação.

## O que é este projeto

Os dados brutos do IMDb (disponíveis em [datasets.imdbws.com](https://datasets.imdbws.com)) trazem informações de **milhões de títulos** (filmes, séries, episódios), sem o cálculo do ranking Top 250 pronto, e sem detalhes como sinopse, elenco ou imagens. Este repositório automatiza esse processo:

1. Baixa os datasets oficiais do IMDb
2. Filtra apenas filmes (excluindo séries e episódios). Conteúdo adulto **não é filtrado**, apenas identificado por um campo (`adulto`), deixando essa decisão a cargo de cada projeto que consumir os dados
3. Calcula o ranking usando a mesma **fórmula de média ponderada** que o próprio IMDb utiliza (leva em conta nota média e número de votos)
4. Enriquece cada um dos 250 filmes com dados complementares da **TMDb** (The Movie Database): sinopse, elenco, diretor, imagens, trailer e mais
5. Publica o resultado em `top250_imdb.json`, sempre atualizado

## Atualização automática

Um workflow do GitHub Actions roda **semanalmente**, refazendo todo o processo (IMDb + TMDb) e commitando o resultado aqui, sem intervenção manual.

## Formato do arquivo (`top250_imdb.json`)

Uma lista com 250 objetos, cada um representando um filme, combinando dados oficiais do IMDb com enriquecimento da TMDb:

```json
{
  "posicao": 1,
  "imdbId": "tt0111161",
  "titulo": "The Shawshank Redemption",
  "tituloOriginal": "The Shawshank Redemption",
  "ano": 1994,
  "generos": ["Drama"],
  "duracaoMinutos": 142,
  "adulto": false,
  "notaImdb": 9.3,
  "numVotos": 3000000,
  "tmdbId": 278,
  "tituloPtBr": "Um Sonho de Liberdade",
  "sinopse": "Andy Dufresne é condenado à prisão perpétua...",
  "tagline": "Fear can hold you prisoner. Hope can set you free.",
  "capaUrl": "https://image.tmdb.org/t/p/w500/...",
  "fundoUrl": "https://image.tmdb.org/t/p/w1280/...",
  "dataLancamento": "1994-09-23",
  "idiomaOriginal": "en",
  "orcamento": 25000000,
  "bilheteria": 16000000,
  "paisesProducao": ["United States of America"],
  "diretores": ["Frank Darabont"],
  "elencoPrincipal": [
    { "ator": "Tim Robbins", "personagem": "Andy Dufresne" },
    { "ator": "Morgan Freeman", "personagem": "Ellis Boyd 'Red' Redding" }
  ],
  "trailerYoutubeId": "6hB3S9bIaco",
  "palavrasChave": ["prison", "friendship", "hope"]
}
```

| Campo | Origem | Descrição |
|---|---|---|
| `posicao` | Calculado | Posição no ranking (1 = melhor), fórmula ponderada do IMDb |
| `imdbId` | IMDb | ID oficial do filme no IMDb |
| `titulo` | IMDb | Título principal/mais popular |
| `tituloOriginal` | IMDb | Título no idioma original de produção |
| `ano` | IMDb | Ano de lançamento |
| `generos` | IMDb | Lista de gêneros |
| `duracaoMinutos` | IMDb | Duração em minutos (pode ser `null`) |
| `adulto` | IMDb | `true`/`false`; **não filtrado**, decisão fica a cargo de quem consome os dados |
| `notaImdb` | IMDb | Nota média (0 a 10) |
| `numVotos` | IMDb | Número de votos |
| `tmdbId` | TMDb | ID do filme na TMDb (pode ser `null` se não encontrado) |
| `tituloPtBr` | TMDb | Título traduzido para português |
| `sinopse` | TMDb | Sinopse em português |
| `tagline` | TMDb | Frase de efeito/slogan do filme |
| `capaUrl` | TMDb | URL da imagem de pôster (500px de largura) |
| `fundoUrl` | TMDb | URL da imagem de fundo/backdrop (1280px de largura) |
| `dataLancamento` | TMDb | Data de lançamento (AAAA-MM-DD) |
| `idiomaOriginal` | TMDb | Código do idioma original |
| `orcamento` | TMDb | Orçamento em dólares (pode ser 0 se não informado) |
| `bilheteria` | TMDb | Bilheteria em dólares (pode ser 0 se não informado) |
| `paisesProducao` | TMDb | Lista de países de produção |
| `diretores` | TMDb | Lista de nomes dos diretores |
| `elencoPrincipal` | TMDb | Lista com os 8 primeiros atores (nome + personagem) |
| `trailerYoutubeId` | TMDb | ID do vídeo no YouTube (monte a URL como `youtube.com/watch?v=ID`) |
| `palavrasChave` | TMDb | Lista de palavras-chave temáticas |

**Nota:** campos vindos da TMDb podem vir vazios/nulos caso o filme não seja encontrado na base deles (raro, mas possível).

## Como usar em outros projetos

O arquivo é servido como um JSON público, sem necessidade de autenticação. Basta buscar via HTTP: https://raw.githubusercontent.com/offrogerr/roleta-filmes-dataset/main/top250_imdb.json



### Exemplo em JavaScript (navegador ou Node.js)

```javascript
fetch('https://raw.githubusercontent.com/offrogerr/roleta-filmes-dataset/main/top250_imdb.json')
  .then(res => res.json())
  .then(filmes => {
    console.log(filmes[0].titulo); // primeiro filme do ranking
  });
```

### Exemplo em Python

```python
import requests

resposta = requests.get(
    "https://raw.githubusercontent.com/offrogerr/roleta-filmes-dataset/main/top250_imdb.json"
)
filmes = resposta.json()
print(filmes[0]["titulo"])
```

### Exemplo em Dart/Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

final resposta = await http.get(Uri.parse(
  'https://raw.githubusercontent.com/offrogerr/roleta-filmes-dataset/main/top250_imdb.json',
));
final filmes = json.decode(resposta.body);
print(filmes[0]['titulo']);
```

### Boas práticas para quem for consumir

- **Cache local:** salve uma cópia local (arquivo ou banco de dados) depois do primeiro download, e só busque de novo periodicamente (o dataset só muda uma vez por semana, então não há necessidade de buscar a cada abertura do app).
- **Trate campos ausentes:** campos vindos da TMDb (`tmdbId`, `capaUrl`, `sinopse` etc.) podem vir como `null` em casos raros onde o filme não foi encontrado na base deles. Sempre verifique antes de usar.
- **Imagens:** os campos `capaUrl` e `fundoUrl` já vêm como link completo e pronto para uso direto em `<img>` ou equivalente, não precisa montar a URL manualmente.
- **Trailer:** o campo `trailerYoutubeId` é só o ID do vídeo. Monte a URL completa assim: `https://www.youtube.com/watch?v=` + o ID.
- **Filtro de conteúdo adulto:** o campo `adulto` não é filtrado por este dataset; aplique seu próprio filtro se necessário para o seu caso de uso.

## Origem deste projeto

Este dataset foi criado originalmente para o app [Roleta de Filmes](#) (uma roleta para sortear filmes para assistir), mas foi desacoplado para ser reutilizável em qualquer outro projeto que precise desses dados.

## Licença

O código/processo deste repositório está sob licença MIT. Os dados brutos utilizados como fonte pertencem ao IMDb, sob os termos de uso não-comercial descritos em [imdb.com/interfaces](https://www.imdb.com/interfaces/). As imagens e informações complementares são fornecidas pela [TMDb](https://www.themoviedb.org/), sob os termos de uso da API deles.