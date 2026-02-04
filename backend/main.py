import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import mysql.connector
from typing import Optional
import uvicorn

# Carrega as variáveis do arquivo .env
load_dotenv()

app = FastAPI(title="API de Operadoras ANS")

# Middleware CORS - Permite que o Frontend acesse a API
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
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )
    except mysql.connector.Error as err:
        print(f"❌ Erro ao conectar ao banco: {err}")
        return None

# --- ROTAS DA API ---

@app.get("/api/operadoras")
def listar_operadoras(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), q: Optional[str] = ""):
    conn = conectar_banco()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco.")
    
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

@app.get("/api/estatisticas")
def obter_estatisticas():
    conn = conectar_banco()
    if not conn:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco.")
        
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

# --- SERVIR FRONTEND ---
# Resolve o caminho para a pasta frontend (um nível acima da pasta backend)
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)

# Ordem de preferência: 1. Pasta 'dist' (build), 2. Pasta 'frontend' raiz
frontend_path = os.path.join(project_root, "frontend", "dist")
if not os.path.exists(frontend_path):
    frontend_path = os.path.join(project_root, "frontend")

if os.path.exists(os.path.join(frontend_path, "index.html")):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ Servindo frontend de: {frontend_path}")
else:
    print(f"⚠️ Alerta: index.html não encontrado em {frontend_path}")

if __name__ == "__main__":
    # Roda o servidor na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)