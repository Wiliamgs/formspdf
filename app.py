import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
import io
import os

import re # <-- ADICIONE ISSO LÁ NO TOPO JUNTO COM OS OUTROS IMPORTS

# --- SUBSTITUA A FUNÇÃO ANTIGA POR ESTA ---
def processar_pdf_forms(arquivo_pdf):
    # Lê o PDF do Forms
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto_completo = ""
    for page in doc:
        texto_completo += page.get_text()
    
    linhas = texto_completo.split('\n')
    linhas_limpas = []
    
    for linha in linhas:
        linha = linha.strip()
        
        # Ignora linhas totalmente vazias
        if not linha:
            continue
            
        # CORREÇÃO 1: Encurta linhas de sublinhado gigantes (o maior causador do erro)
        # Transforma "______________________" em apenas "____"
        linha = re.sub(r'_{15,}', '____', linha)
        
        # CORREÇÃO 2: Quebra "palavras" ou links absurdamente longos (maiores que 60 caracteres)
        palavras_seguras = []
        for palavra in linha.split(' '):
            if len(palavra) > 60:
                # Se a palavra for gigante, quebra ela em pedaços com um espaço no meio
                palavra_quebrada = ' '.join(palavra[i:i+60] for i in range(0, len(palavra), 60))
                palavras_seguras.append(palavra_quebrada)
            else:
                palavras_seguras.append(palavra)
                
        linha_segura = ' '.join(palavras_seguras)
        linhas_limpas.append(linha_segura)
        
    return linhas_limpas

# --- 1. CONFIGURAÇÃO DA INTERFACE (STREAMLIT) ---
st.set_page_config(page_title="NeuroDoc | Gerador de Anamnese", page_icon="📄", layout="centered")

st.markdown("""
    <style>
    .main-title { font-family: 'Inter', sans-serif; color: #1E2329; text-align: center; font-weight: 700; }
    .sub-title { color: #848E9C; text-align: center; margin-bottom: 30px; }
    </style>
    <h1 class="main-title">NeuroDoc Generator</h1>
    <p class="sub-title">Padronização ABNT para Anamneses Interdisciplinares</p>
""", unsafe_allow_html=True)

# --- 2. CLASSE DO PDF (PADRÃO ABNT E TIMBRADO) ---
class NeuroPDF(FPDF):
    def header(self):
        # O cabeçalho pode ficar vazio ou ter um título padrão
        self.set_font("helvetica", "B", 14)
        self.cell(0, 10, "ANAMNESE INTERDISCIPLINAR", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5) # Pula linha

    def footer(self):
        # Rodapé: Posiciona a 3 cm do final da página
        self.set_y(-30)
        
        # Adiciona o Logo da Clínica (download.png) centralizado
        # w=40 é a largura do logo. Ajuste conforme necessário.
        if os.path.exists("download.png"):
            self.image("download.png", x=85, w=40)
        
        # Numeração da página
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

# --- 3. LÓGICA DE EXTRAÇÃO E TRANSFORMAÇÃO ---
def processar_pdf_forms(arquivo_pdf):
    # Lê o PDF do Forms
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto_completo = ""
    for page in doc:
        texto_completo += page.get_text()
    
    # Aqui fazemos uma limpeza básica. O Forms costuma colocar quebras de linha estranhas.
    linhas = texto_completo.split('\n')
    linhas_limpas = [linha.strip() for linha in linhas if linha.strip() != ""]
    
    return linhas_limpas

def gerar_pdf_padronizado(linhas_texto):
    # Inicializa o PDF no formato A4
    pdf = NeuroPDF(orientation="P", unit="mm", format="A4")
    
    # Margens ABNT: Esquerda 3cm, Direita 2cm, Topo 3cm, Fundo 2cm
    pdf.set_margins(left=30, top=30, right=20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Cores
    cor_pergunta = (30, 35, 41)   # Cinza escuro (quase preto)
    cor_resposta = (100, 100, 100) # Cinza médio

    # Lógica de montagem: Assumimos que perguntas têm '?' ou são os primeiros itens
    # O Google Forms alterna Pergunta e Resposta. 
    # Como o Forms é bagunçado, vamos imprimir em blocos.
    
    for linha in linhas_texto:
        # Se a linha termina com "?" ou parece um título de pergunta (Forms)
        if linha.endswith("?") or len(linha) < 50:
            pdf.set_font("helvetica", "B", 12) # Título tamanho 12 Negrito
            pdf.set_text_color(*cor_pergunta)
            pdf.ln(4)
            pdf.multi_cell(0, 6, linha)
        else:
            pdf.set_font("helvetica", "", 12) # Resposta tamanho 12 Normal
            pdf.set_text_color(*cor_resposta)
            pdf.multi_cell(0, 6, linha)
            pdf.ln(2)

    # Retorna o PDF em memória (bytes)
    return pdf.output(dest="S").encode("latin1")

# --- 4. INTERFACE DO USUÁRIO ---
arquivo_forms = st.file_uploader("📥 Suba o PDF gerado pelo Google Forms", type="pdf")

if arquivo_forms:
    with st.spinner("Transformando e aplicando papel timbrado..."):
        try:
            # Extrai o texto sujo
            dados_extraidos = processar_pdf_forms(arquivo_forms)
            
            # Gera o PDF limpo
            pdf_final_bytes = gerar_pdf_padronizado(dados_extraidos)
            
            st.success("✨ Documento gerado com sucesso!")
            
            st.download_button(
                label="📥 Baixar Anamnese Padronizada (PDF)",
                data=pdf_final_bytes,
                file_name="Anamnese_Neurointegrando_Padrao.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
