import pandas as pd
import os

def gerar_sql_carga():
    print("\n[PYTHON] Iniciando processamento automático para carga SQL...")
    
    caminho_sql = os.path.join("scripts", "sql")
    if not os.path.exists(caminho_sql):
        os.makedirs(caminho_sql)

    try:
        # 1. Carrega Operadoras
        df_cad = pd.read_csv("dados/processados/relatorio_enriquecido.csv", sep=';', dtype=str)
        df_cad['CNPJ'] = df_cad['CNPJ'].str.replace('="', '', regex=False).str.replace('"', '', regex=False).str.strip()
        df_cad = df_cad.drop_duplicates(subset=['RegistroANS'])

        # 2. Carrega Despesas
        df_desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
        df_desp['CNPJ'] = df_desp['CNPJ'].str.replace('="', '', regex=False).str.replace('"', '', regex=False).str.strip()

        # --- O PULO DO GATO: CRUZAMENTO DE DADOS (MERGE) ---
        # Adicionamos o 'RegistroANS' correto na tabela de despesas usando o CNPJ como ponte
        df_desp = pd.merge(df_desp, df_cad[['CNPJ', 'RegistroANS']], on='CNPJ', how='left')

        # 3. Limpeza do valor financeiro
        df_desp['V_LIMPO'] = (df_desp['ValorDespesas']
                              .str.replace('R$', '', regex=False)
                              .str.replace('.', '', regex=False)
                              .str.replace(',', '.', regex=False)
                              .str.strip().astype(float))

        arquivo_final = os.path.join(caminho_sql, "carga_dados.sql")
        
        with open(arquivo_final, "w", encoding="utf-8-sig") as f:
            f.write("USE intuitivecare;\n")
            f.write("SET NAMES 'utf8mb4';\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            f.write("TRUNCATE TABLE despesas_consolidadas;\n")
            f.write("TRUNCATE TABLE operadoras;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
            
            # Inserir Operadoras
            print("[PYTHON] Gerando inserts de Operadoras...")
            for _, row in df_cad.iterrows():
                razao = str(row['RazaoSocial']).replace("'", "''")
                modal = str(row['Modalidade']).replace("'", "''")
                f.write(f"INSERT INTO operadoras (CNPJ, RazaoSocial, RegistroANS, Modalidade, UF) VALUES ('{row['CNPJ']}', '{razao}', '{row['RegistroANS']}', '{modal}', '{row['UF']}');\n")
            
            # Inserir Despesas
            print("[PYTHON] Gerando inserts de Despesas...")
            for _, row in df_desp.iterrows():
                # Agora usamos o RegistroANS que veio do merge, garantindo que ele existe na tabela pai
                reg_ans = row['RegistroANS']
                
                # Só insere se o merge encontrou uma operadora correspondente
                if pd.notna(reg_ans):
                    f.write(f"INSERT INTO despesas_consolidadas (registro_ans, trimestre, ano, valor_despesa) "
                            f"VALUES ('{reg_ans}', {row['Trimestre']}, {row['Ano']}, {row['V_LIMPO']});\n")

        print(f"\n[SUCESSO] Script '{arquivo_final}' gerado perfeitamente.")
        print("Agora é só dar 'Run' no MySQL Workbench e correr para o abraço!")
        
    except Exception as e:
        print(f"[ERRO] Falha no processamento: {e}")

if __name__ == "__main__":
    gerar_sql_carga()