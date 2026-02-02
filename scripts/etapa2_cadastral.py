import pandas as pd
import unicodedata, re

def limpar_texto_perfeito(texto):
    """
    Remove acentos, símbolos e espaços duplos.
    Trade-off: Normalização NFKD usada para evitar que 'SAÚDE' vire 'SAADE'.
    """
    if pd.isna(texto): return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    texto_limpo = "".join([c for c in nfkd if not unicodedata.combining(c)])
    texto_limpo = texto_limpo.replace('ç', 'c').replace('Ç', 'C')
    # Mantém apenas letras, números e espaços
    texto_limpo = re.sub(r'[^A-Z0-9\s]', '', texto_limpo.upper())
    return " ".join(texto_limpo.split())

def limpar_cad():
    print("\n[LIMPANDO] Higienizando cadastro de operadoras...")
    df = pd.read_csv("dados/raw/operadoras_ativas.csv", sep=None, engine='python', encoding='latin-1', skiprows=3)
    
    # Padronização de nomes de colunas essenciais
    df = df.rename(columns={df.columns[0]: 'REGISTRO_ANS', df.columns[2]: 'RAZAO_SOCIAL', df.columns[10]: 'UF'})
    
    df['RAZAO_SOCIAL'] = df['RAZAO_SOCIAL'].apply(limpar_texto_perfeito)
    df['UF'] = df['UF'].apply(limpar_texto_perfeito)
    # Garante que o ID ANS contenha apenas números
    df['REGISTRO_ANS'] = df['REGISTRO_ANS'].astype(str).str.replace(r'[^0-9]', '', regex=True)
    
    df[['REGISTRO_ANS', 'RAZAO_SOCIAL', 'UF']].to_csv("dados/processados/operadoras_limpas.csv", index=False, sep=';', encoding='utf-8-sig')
    print("✅ [OK] Cadastro limpo e normalizado!")

if __name__ == "__main__":
    limpar_cad()