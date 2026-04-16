import streamlit as st
import fitz  # PyMuPDF
from fpdf import FPDF
import io
import os
import re
from datetime import date

# --- 1. CONFIGURAÇÃO DA INTERFACE ---
# Isso deve ser a primeira coisa no código
st.set_page_config(
    page_title="NeuroDoc | Gerador de Anamnese", 
    page_icon="📄", 
    layout="centered"
)

# Estilo visual moderno
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    .main-title { font-family: 'Inter', sans-serif; color: #1E2329; text-align: center; font-weight: 700; margin-top: 20px; }
    .sub-title { font-family: 'Inter', sans-serif; color: #848E9C; text-align: center; margin-bottom: 30px; }
    .stDownloadButton > button { width: 100%; background-color: #0071e3 !important; color: white !important; border-radius: 10px !important; height: 50px; font-weight: 600; }
    </style>
    <h1 class="main-title">NeuroDoc Generator.</h1>
    <p class="sub-title">Padronização ABNT para Clínica Neurointegrando</p>
""", unsafe_allow_html=True)

# --- 2. CLASSE DO PDF (PADRÃO ABNT) ---
class NeuroPDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 14)
        self.set_text_color(30, 35, 41)
        self.cell(0, 10, "ANAMNESE INTERDISCIPLINAR", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-30)
        # Tenta carregar o logo download.png
        if os.path.exists("download.png"):
            try:
                self.image("download.png", x=85, w=40)
            except:
                pass
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

# --- 3. LÓGICA DE PROCESSAMENTO ---
def limpar_texto_forms(arquivo_pdf):
    doc = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto = ""
    for page in doc:
        texto += page.get_text()
    
    linhas = texto.split('\n')
    resultado = []
    
    for l in linhas:
        l = l.strip()
        if not l: continue
        
        # Remove caracteres problemáticos e limpa sequências longas
        l = l.replace('\xa0', ' ')
        l = re.sub(r'_{10,}', '____', l)
        l = re.sub(r'\.{10,}', '....', l)
        
        # QUEBRA FORÇADA: Evita o erro de "horizontal space" cortando qualquer palavra > 50 chars
        l = re.sub(r'(\S{50})', r'\1 ', l)
        resultado.append(l)
    return resultado

def criar_documento(dados):
    pdf = NeuroPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_margins(left=30, top=30, right=20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    for linha in dados:
        # Se for pergunta (curta ou com ?)
        if linha.endswith("?") or len(linha) < 45:
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(30, 35, 41)
            pdf.ln(4)
            pdf.multi_cell(0, 6, linha)
        else:
            pdf.set_font("helvetica", "", 12)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 6, linha)
            pdf.ln(2)
            
    # Gera o PDF como bytes
    return pdf.output()

# --- 4. FLUXO DO APP ---
upload = st.file_uploader("📥 Arraste o PDF do Google Forms aqui", type="pdf")

if upload:
    try:
        with st.spinner("Gerando documento..."):
            texto_limpo = limpar_texto_forms(upload)
            pdf_final = criar_documento(texto_limpo)
            
            st.success("✨ Documento pronto!")
            st.download_button(
                label="📥 Baixar Anamnese Padronizada",
                data=bytes(pdf_final),
                file_name=f"Anamnese_Neuro_{date.today()}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Erro no processamento: {e}")

st.markdown("<br><hr><center><p style='color:#848E9C; font-size:12px;'>NeuroDoc System • Clínica Neurointegrando</p></center>", unsafe_allow_html=True)
