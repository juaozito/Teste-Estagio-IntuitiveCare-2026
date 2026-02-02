import pandas as pd

def gerar_join():
    print("\n[UNINDO] Criando relatório detalhado...")
    desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
    cad = pd.read_csv("dados/processados/operadoras_limpas.csv", sep=';', dtype=str)

    df_final = pd.merge(desp, cad, on='REGISTRO_ANS', how='left').dropna(subset=['RAZAO_SOCIAL'])
    df_final = df_final[['REGISTRO_ANS', 'RAZAO_SOCIAL', 'UF', 'VALOR']]
    
    df_final.to_csv("dados/processados/relatorio_final.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [OK] Relatorio Final pronto!")

if __name__ == "__main__":
    gerar_join()