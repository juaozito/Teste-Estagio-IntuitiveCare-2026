import pandas as pd

def gerar_join():
    """
    Cruza as despesas com o cadastro.
    Trade-off: Dropna aplicado na Razão Social para remover registros sem operadora correspondente.
    """
    print("\n[UNINDO] Criando relatório detalhado...")
    # Carregamento com dtype str para preservar IDs
    desp = pd.read_csv("dados/processados/consolidado_despesas.csv", sep=';', dtype=str)
    cad = pd.read_csv("dados/processados/operadoras_limpas.csv", sep=';', dtype=str)

    # Inner join para garantir que apenas despesas com operadoras identificadas sejam listadas
    df_final = pd.merge(desp, cad, on='REGISTRO_ANS', how='left').dropna(subset=['RAZAO_SOCIAL'])
    
    # Seleção de colunas finais para o relatório detalhado
    df_final = df_final[['REGISTRO_ANS', 'RAZAO_SOCIAL', 'UF', 'VALOR']]
    
    df_final.to_csv("dados/processados/relatorio_final.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [OK] Relatorio Final gerado!")

if __name__ == "__main__":
    gerar_join()