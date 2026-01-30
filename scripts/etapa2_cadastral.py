import pandas as pd
import os

def limpar_cadastro():
    print("--- Etapa 2: Limpeza Cadastral (Ajuste de Colunas) ---")
    arq_bruto = "dados/raw/operadoras_ativas.csv"
    arq_limpo = "dados/processados/operadoras_limpas.csv"

    if not os.path.exists(arq_bruto):
        print(f"❌ Arquivo bruto não encontrado em: {arq_bruto}")
        return

    # Lemos o arquivo pulando as 3 linhas de lixo da ANS
    df = pd.read_csv(arq_bruto, sep=None, engine='python', encoding='latin-1', skiprows=3, header=None)
    
    # Lista com 20 nomes para bater com o seu arquivo
    colunas = [
        'REGISTRO_ANS', 'CNPJ', 'RAZAO_SOCIAL', 'NOME_FANTASIA', 'MODALIDADE', 
        'LOGRADOURO', 'NUMERO', 'COMPLEMENTO', 'BAIRRO', 'CIDADE', 'UF', 
        'CEP', 'DDD', 'TELEFONE', 'FAX', 'EMAIL', 'REPRESENTANTE', 'CARGO', 
        'DATA_REGISTRO', 'COLUNA_EXTRA' # Adicionamos a 20ª coluna aqui
    ]
    
    # Ajusta a lista dinamicamente caso o arquivo mude de novo
    if len(df.columns) != len(colunas):
        print(f"⚠️ Aviso: O arquivo tem {len(df.columns)} colunas, ajustando nomes...")
        novas_cols = colunas[:len(df.columns)]
        # Se o arquivo tiver MAIS de 20, preenche com 'EXTRA_N'
        while len(novas_cols) < len(df.columns):
            novas_cols.append(f"EXTRA_{len(novas_cols)}")
        df.columns = novas_cols
    else:
        df.columns = colunas

    os.makedirs("dados/processados/", exist_ok=True)
    df.to_csv(arq_limpo, index=False, encoding='utf-8')
    print(f"✅ Cadastro limpo e salvo com {len(df)} operadoras.")

if __name__ == "__main__":
    limpar_cadastro()