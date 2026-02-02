import pandas as pd

def cruzar_dados():
    print("--- Eu estou unindo as despesas com os nomes das empresas ---")
    
    # Eu carrego os dois arquivos que eu preparei antes
    despesas = pd.read_csv("dados/processados/consolidado_despesas.csv")
    cadastro = pd.read_csv("dados/processados/operadoras_limpas.csv")

    # AQUI ESTÁ O MEU SEGREDO: Eu limpo o Registro ANS para garantir que '00123' e '123' sejam iguais
    # Eu transformo em texto, tiro espaços e removo o '0' da esquerda
    despesas['CHAVE'] = despesas['CNPJ'].astype(str).str.strip().str.lstrip('0')
    cadastro['CHAVE'] = cadastro['REGISTRO_ANS'].astype(str).str.strip().str.lstrip('0')

    # Eu faço o MERGE (o cruzamento). Eu uso 'left' para manter todas as despesas que eu encontrei
    relatorio = pd.merge(despesas, cadastro, on='CHAVE', how='left')

    # Eu salvo o relatório final que vai alimentar o meu Banco de Dados
    relatorio.to_csv("dados/processados/relatorio_final.csv", index=False, encoding='utf-8')
    print("Relatório final gerado com sucesso!")

if __name__ == "__main__":
    cruzar_dados()