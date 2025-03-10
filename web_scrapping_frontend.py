from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn
import pyodbc
import pandas as pd
from textblob import TextBlob

# Configuração da conexão com o banco de dados SQL Server
server = '25.33.157.133'
database = 'ETL 2'
username = 'sa'
password = 'sa'
table_name = 'reddit'

# String de conexão com o SQL Server
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

app = FastAPI(title="Web Scrapping API")

# Permitir CORS para permitir acesso via frontend (se necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectar ao banco de dados na inicialização da aplicação
def get_db_connection():
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Página principal com o frontend da aplicação
@app.get("/", response_class=HTMLResponse)
async def frontend():
    return '''
    <html>
        <head>
            <title>Web Scrapping</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    background: url('https://www.gravitymedia.com/wp-content/uploads/2022/04/uefa-champions-league-1024x538.jpg.webp') no-repeat center center fixed;
                    background-size: cover;
                    color: white;
                    text-align: center;
                }
                #searchContainer {
                    background-color: rgba(0, 0, 0, 0.7);
                    padding: 20px;
                    border-radius: 10px;
                }
                input, button {
                    padding: 10px;
                    margin: 10px;
                    border: none;
                    border-radius: 5px;
                }
                button {
                    background-color: #007bff;
                    color: white;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <div id="searchContainer">
                <h1>Web Scrapping</h1>
                <form method="get" action="/search">
                    <input type="text" name="query" placeholder="Digite o termo de pesquisa...">
                    <button type="submit">Pesquisar</button>
                </form>
                <div id="results"></div>
            </div>
        </body>
    </html>
    '''

# Rota para buscar dados da API
@app.get("/search", response_class=HTMLResponse)
async def search(query: str = Query(None, description="Pesquisar dados sobre...")):
    if not query:
        return "Insira um termo de pesquisa."

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados.")

    query_str = f"SELECT * FROM {table_name} WHERE titulo LIKE ? OR conteudo LIKE ?"
    params = [f'%{query}%', f'%{query}%']
    df = pd.read_sql(query_str, conn, params=params)

    if df.empty:
        return "Nenhum dado encontrado para o termo pesquisado."

    stats = {
        "total_resultados": len(df),
        "media_upvotes": df['upvotes'].mean(),
        "media_comentarios": df['comentarios'].mean(),
        "media_interacoes": df['interacoes'].mean()
    }

    sentimentos = df['conteudo'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    positivo = len([s for s in sentimentos if s > 0]) / len(sentimentos) * 100
    negativo = len([s for s in sentimentos if s < 0]) / len(sentimentos) * 100
    neutro = len([s for s in sentimentos if s == 0]) / len(sentimentos) * 100

    html = f"""
    <h2>Estatísticas:</h2>
    <p>Total de resultados: {stats['total_resultados']}</p>
    <p>Média de upvotes: {stats['media_upvotes']:.2f}</p>
    <p>Média de comentários: {stats['media_comentarios']:.2f}</p>
    <p>Média de interações: {stats['media_interacoes']:.2f}</p>
    <h3>Análise Sentimental:</h3>
    <p>Positivo: {positivo:.2f}%</p>
    <p>Negativo: {negativo:.2f}%</p>
    <p>Neutro: {neutro:.2f}%</p>
    <h2>Resultados:</h2>
    """
    for _, row in df.iterrows():
        html += f"""
        <div>
            <h3>{row['titulo']}</h3>
            <p>Upvotes: {row['upvotes']}</p>
            <p>Comentários: {row['comentarios']}</p>
            <p>Interações: {row['interacoes']}</p>
            <a href="{row['link']}" target="_blank">Ver publicação</a>
        </div>
        """
    return HTMLResponse(content=html)

if __name__ == '__main__':
    uvicorn.run(app, host="192.168.1.134", port=8000)
