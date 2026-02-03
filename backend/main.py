import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from typing import Optional
import uvicorn

# Carrega as variáveis do arquivo .env
load_dotenv()

app = FastAPI(title="API de Operadoras ANS")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar_banco():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco: {err}")
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados.")

# --- ROTAS DA API ---

@app.get("/api/operadoras")
def listar_operadoras(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), q: Optional[str] = ""):
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    offset = (page - 1) * limit
    
    query = "SELECT * FROM operadoras WHERE RazaoSocial LIKE %s OR CNPJ LIKE %s ORDER BY RazaoSocial ASC LIMIT %s OFFSET %s"
    search = f"%{q}%"
    cursor.execute(query, (search, search, limit, offset))
    data = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total FROM operadoras")
    total = cursor.fetchone()['total']
    
    conn.close()
    return {"data": data, "total": total}

@app.get("/api/estatisticas/por-uf")
@app.get("/api/estatisticas")
def obter_estatisticas():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT o.UF, SUM(d.valor_despesa) as total 
        FROM despesas_consolidadas d
        JOIN operadoras o ON d.registro_ans = o.RegistroANS
        GROUP BY o.UF
        ORDER BY total DESC
    """)
    stats = cursor.fetchall()
    conn.close()
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)