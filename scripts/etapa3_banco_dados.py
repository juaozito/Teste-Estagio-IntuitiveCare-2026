import pandas as pd
import os

def gerar_sql_carga():
    """
    ETAPA 3: Geração de Script SQL.
    OBJETIVO: Transformar os dados processados em comandos INSERT para o MySQL.
    """
    print("\n[PYTHON] Iniciando processamento automático para carga SQL...")
    
    # --- BLOCO 1: ORGANIZAÇÃO DE PASTAS ---
    caminho_sql = os.path.join("scripts", "sql")
    if not os.path.exists(caminho_sql):
        os.makedirs(caminho_sql)

    try:
        # --- BLOCO 2: CARGA E LIMPEZA DE DADOS ---
        df_cad = pd.read_csv("dados/processados/relatorio_enriquecido.csv", sep=';', dtype=str)
        
        # Limpa os formatos do Excel para deixar apenas dados puros.
        df_cad['CNPJ'] = df_cad['CNPJ'].str.replace('="', '', regex=False).str.replace('"', '', regex=False).str.strip()
        df_cad = df_cad.drop_duplicates(subset=['RegistroANS'])

        df_desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
        df_desp['CNPJ'] = df_desp['CNPJ'].str.replace('="', '', regex=False).str.replace('"', '', regex=False).str.strip()

        # --- O PULO DO GATO: INTEGRIDADE REFERENCIAL ---
        df_desp = pd.merge(df_desp, df_cad[['CNPJ', 'RegistroANS']], on='CNPJ', how='left')

        # --- BLOCO 3: TRATAMENTO FINANCEIRO ---
        df_desp['V_LIMPO'] = (df_desp['ValorDespesas']
                              .str.replace('R$', '', regex=False)
                              .str.replace('.', '', regex=False)
                              .str.replace(',', '.', regex=False)
                              .str.strip().astype(float))

        # --- BLOCO 4: ESCRITA DO ARQUIVO SQL ---
        arquivo_final = os.path.join(caminho_sql, "carga_dados.sql")
        
        # [SOLUÇÃO DO ERRO 1064]: Alterado encoding para "utf-8" (sem o -sig).
        # Isso impede que o Python insira bytes invisíveis no início do arquivo que o MySQL não reconhece.
        with open(arquivo_final, "w", encoding="utf-8") as f:
            # Cada comando f.write termina com \n para garantir que o MySQL não leia dois comandos colados.
            f.write("USE intuitivecare;\n")
            f.write("SET NAMES 'utf8mb4';\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            f.write("TRUNCATE TABLE despesas_consolidadas;\n")
            f.write("TRUNCATE TABLE operadoras;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
            
            # --- BLOCO 5: INSERTS DE OPERADORAS ---
            print("[PYTHON] Gerando inserts de Operadoras...")
            for _, row in df_cad.iterrows():
                # Escapa aspas simples para evitar erro de sintaxe em nomes como "L'Aqua".
                razao = str(row['RazaoSocial']).replace("'", "''")
                modal = str(row['Modalidade']).replace("'", "''")
                f.write(f"INSERT INTO operadoras (CNPJ, RazaoSocial, RegistroANS, Modalidade, UF) VALUES ('{row['CNPJ']}', '{razao}', '{row['RegistroANS']}', '{modal}', '{row['UF']}');\n")
            
            # --- BLOCO 6: INSERTS DE DESPESAS ---
            print("[PYTHON] Gerando inserts de Despesas...")
            for _, row in df_desp.iterrows():
                reg_ans = row['RegistroANS']
                
                if pd.notna(reg_ans):
                    f.write(f"INSERT INTO despesas_consolidadas (registro_ans, trimestre, ano, valor_despesa) "
                            f"VALUES ('{reg_ans}', {row['Trimestre']}, {row['Ano']}, {row['V_LIMPO']});\n")

        print(f"\n[SUCESSO] Script '{arquivo_final}' gerado.")
        
    except Exception as e:
        print(f"[ERRO] Falha no processamento: {e}")

if __name__ == "__main__":
    gerar_sql_carga()