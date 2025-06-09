# Web Scraping e Visualização com Base de Dados

Este repositório contém um projeto que realiza **web scraping ao Reddit**, armazena os dados num **ficheiro CSV** e numa **base de dados SQL Server**, e fornece uma **interface web local** que permite visualizar, consultar e analisar os dados recolhidos.

---

## Objetivo

- Recolher publicações recentes do subreddit `r/championsleague`.
- Guardar os dados num ficheiro CSV local.
- Inserir automaticamente os dados numa base de dados relacional (SQL Server).
- Criar uma **API web com interface gráfica** onde é possível pesquisar conteúdos e ver estatísticas em tempo real.

---

## Estrutura do Projeto

```
 scraping-project
 ┣ 📄 scraping.py                 # Script de scraping (Reddit → CSV + SQL Server)
 ┣ 📄 web_scrapping_frontend.py  # API FastAPI com interface web
 ┣ 📄 championsleague_reddit.csv # CSV com dados recolhidos (gerado automaticamente)
 ┣ 📄 requirements.txt           # Dependências do projeto
```

---

## Tecnologias Utilizadas

- **Python**
  - `asyncpraw` – API assíncrona do Reddit
  - `pandas` – tratamento de dados
  - `pyodbc` – ligação à base de dados
  - `langdetect` – deteção de idioma
  - `textblob` – análise de sentimentos
  - `fastapi` + `uvicorn` – backend e servidor web
- **SQL Server (SSMS)** – armazenamento dos dados
- **HTML/CSS** – interface web incorporada via FastAPI

---

##  Recolha de Dados: `scraping.py`

Este script conecta-se ao Reddit e recolhe publicações recentes do subreddit `r/championsleague`.

### Funcionalidades:

- Geração automática do ficheiro `championsleague_reddit.csv`.
- Detecção de idioma do título (`langdetect`).
- Cálculo de interações (upvotes + comentários).
- Inserção dos dados no SQL Server, evitando duplicações via `id_publicacao`.
- Corre num ciclo contínuo com atualização a cada 10 segundos.

### Como executar:

```bash
pip install asyncpraw pandas pyodbc langdetect
python scraping.py
```

> Garante que a base de dados SQL Server (`ETL 2`) e a tabela `reddit` já estão criadas.

---

## Interface Web: `web_scrapping_frontend.py`

Uma API local construída com **FastAPI**, que apresenta uma interface gráfica acessível via browser.

### Funcionalidades:

- Página inicial com imagem de fundo da Champions League.
- Campo de pesquisa para procurar por `título` ou `conteúdo`.
- Apresentação dos resultados com:
  - Título, link, upvotes, comentários, interações
- Estatísticas automáticas:
  - Média de upvotes, comentários e interações
  - Análise de sentimentos: Positivo / Negativo / Neutro

### Como executar:

```bash
pip install fastapi uvicorn pyodbc pandas textblob
python web_scrapping_frontend.py
```
### Aviso:

- A base de dados necessita de ser local, tudo necessita de funcionar localmente.
  
---

## Estrutura da Tabela no SQL Server

```sql
CREATE TABLE reddit (
    id NVARCHAR(50),
    id_publicacao NVARCHAR(50) PRIMARY KEY,
    titulo NVARCHAR(MAX),
    upvotes INT,
    comentarios INT,
    link NVARCHAR(MAX),
    hora_envio DATETIME,
    hora_publicacao DATETIME,
    linguagem NVARCHAR(20),
    interacoes INT,
    conteudo NVARCHAR(MAX)
)
```

---

## Exemplo de Resultado

```
[ Web Scrapping ]
Digite o termo de pesquisa: [Champions League] [Pesquisar]

Estatísticas:
- Total de resultados: 10
- Média de upvotes: 67.4
- Média de comentários: 11.2
- Média de interações: 78.6

Análise Sentimental:
- Positivo: 60.00%
- Negativo: 20.00%
- Neutro: 20.00%

Resultados:
Título: Manchester City Wins Again!
Upvotes: 123
Comentários: 34
Interações: 157
[Ver publicação]
```

---

## Funcionalidades Completas

- Recolha contínua de dados (real-time)
- CSV com registos históricos
- Inserção automática na base de dados
- Análise de sentimento com `TextBlob`
- Interface acessível localmente
- Pesquisa dinâmica por palavras-chave

## Autores

- Tomás Gomes – Nº 51726 & Tiago Marques – Nº 51653: Recolha de Dados & Base de Dados  
- Tomás Gomes – Nº 51726 & Tiago Marques – Nº 51653: Interface Web & API  
- Inteligência Artificial e Ciência de Dados (1.º ciclo)

---
```
