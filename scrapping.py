import asyncio
import os
from datetime import datetime

import asyncpraw
import pandas as pd
import pyodbc
from langdetect import detect

# Nosso ID (pode ser o nome do usuário ou um ID do projeto)
NOSSO_ID = "Key_Regular_4484"
CSV_PATH = "championsleague_reddit.csv"

# Configuração da conexão com o banco de dados SQL Server
server = '25.33.157.133'
database = 'ETL 2'
username = 'sa'
password = 'sa'
table_name = 'reddit'

# String de conexão com o SQL Server
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

async def fetch_reddit():
    async with asyncpraw.Reddit(
        client_id="G8EoPQ5zzeX46lpaNuIv0g",
        client_secret="Kntl_Kt-AsZpTBWUCecbMHWWHIjCJA",
        user_agent="Lab 2:v1.0 (by u/Key_Regular_4484)"
    ) as reddit:

        subreddit = await reddit.subreddit("championsleague")
        print("Monitorando o subreddit em tempo real...")

        last_seen_id = None

        # Se o CSV já existir, carregar o último ID salvo para evitar duplicações
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            if not df.empty:
                last_seen_id = df["id_publicacao"].iloc[-1]

        while True:
            posts = []
            hora_envio_csv = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            async for post in subreddit.new(limit=50):
                if post.id == last_seen_id:
                    break

                try:
                    linguagem = detect(post.title)
                except:
                    linguagem = "desconhecida"

                hora_publicacao = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                interacoes = post.score + post.num_comments

                posts.append([
                    NOSSO_ID,
                    post.id,
                    post.title,
                    post.score,
                    post.num_comments,
                    post.url,
                    hora_envio_csv,
                    hora_publicacao,
                    linguagem,
                    interacoes
                ])

            if posts:
                df_new = pd.DataFrame(posts, columns=[
                    "id",
                    "id_publicacao",
                    "titulo",
                    "upvotes",
                    "comentarios",
                    "link",
                    "hora_envio",
                    "hora_publicacao",
                    "linguagem",
                    "interacoes"
                ])

                if os.path.exists(CSV_PATH):
                    df_old = pd.read_csv(CSV_PATH)
                    # Remove dados duplicados com base no 'id_publicacao'
                    df_combined = pd.concat([df_old, df_new], ignore_index=True)
                    df_combined.drop_duplicates(subset=["id_publicacao"], keep='last', inplace=True)

                else:
                    df_combined = df_new

                df_combined.to_csv(CSV_PATH, index=False, encoding="utf-8")
                print(f"{len(posts)} novas publicações salvas em {CSV_PATH}!")

                # Atualiza o último ID visto
                last_seen_id = posts[0][1]

                # Insere os novos dados no banco de dados
                insert_data_to_sql()

            # Espera 60 segundos antes de buscar novas publicações
            await asyncio.sleep(60)

# Função para inserir dados do CSV na tabela do SQL Server
def insert_data_to_sql():
    # Conectar ao banco de dados
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Ler o CSV atualizado
    df = pd.read_csv(CSV_PATH)

    # Inserir dados na tabela do banco de dados sem duplicações
    for index, row in df.iterrows():
        cursor.execute(f"""
            IF NOT EXISTS (SELECT 1 FROM {table_name} WHERE [id_publicacao] = ?)
            BEGIN
                INSERT INTO {table_name} (
                    [id], [id_publicacao], [titulo], [upvotes], [comentarios],
                    [link], [hora_envio], [hora_publicacao], [linguagem], [interacoes]
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            END
        """,
                       row['id_publicacao'], row['id'], row['id_publicacao'], row['titulo'], row['upvotes'],
                       row['comentarios'],
                       row['link'], row['hora_envio'], row['hora_publicacao'], row['linguagem'], row['interacoes']
                       )

    conn.commit()
    cursor.close()
    conn.close()
    print(f'Dados inseridos na tabela {table_name} com sucesso!')

# Executar a função assíncrona diretamente
asyncio.run(fetch_reddit())
