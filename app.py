def processar_pdf_forms(arquivo_pdf):
    # Lê o PDF do Forms
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto_completo = ""
    for page in doc:
        texto_completo += page.get_text()
    
    linhas = texto_completo.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        # 1. Limpeza básica nas pontas
        linha = linha.strip()
        
        if not linha:
            continue
            
        # 2. Transforma espaços invisíveis estranhos (como \xa0) em espaços normais
        linha = linha.replace('\xa0', ' ')
        
        # 3. Mata os repetidores crônicos do Google Forms (Underlines, Traços e Pontos)
        linha = re.sub(r'_{10,}', '____', linha)
        linha = re.sub(r'-{10,}', '----', linha)
        linha = re.sub(r'\.{10,}', '....', linha)
        
        # 4. A MARRETA DE DADOS: Força a quebra de QUALQUER sequência maior que 55 caracteres.
        # O A4 aguenta cerca de 70-80 caracteres por linha. Se uma "palavra" passar de 55, 
        # o Python vai forçar um espaço nela. Isso impede o erro do FPDF 100% das vezes.
        linha = re.sub(r'(\S{55})', r'\1 ', linha)
        
        linhas_limpas.append(linha)
        
    return linhas_limpas
