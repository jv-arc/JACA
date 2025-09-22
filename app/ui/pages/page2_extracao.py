import streamlit as st
import os
from app.core.logger import Logger
from app.core.config import Settings
from app.core.prompt_manager import PromptManager
from app.core.ai_client import GeminiClient
from app.core.project_manager import ProjectManager

# Inicialização dos serviços
def initialize_services():
    logger = Logger()
    settings = Settings()
    prompt_manager = PromptManager()
    gemini_client = GeminiClient(settings, logger)
    project_manager = ProjectManager(logger, settings, prompt_manager, gemini_client)
    return logger, settings, prompt_manager, gemini_client, project_manager

logger, settings, prompt_manager, gemini_client, project_manager = initialize_services()

st.set_page_config(page_title="2. Extração de Texto", layout="wide")
st.title("2. Extração de Texto")

# Seleção de projeto
projects = project_manager.list_projects()
selected = st.selectbox("Selecione o projeto", projects)
if not selected:
    st.warning("Nenhum projeto selecionado.")
    st.stop()
project_manager.load_project(selected)

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Envie os arquivos PDF/DOCX para extração", type=["pdf", "docx"], accept_multiple_files=True
)
if uploaded_files:
    if st.button("Iniciar Extração"):
        with st.spinner("Extraindo texto bruto..."):
            paths = []
            for uf in uploaded_files:
                save_path = os.path.join(project_manager.project_files_dir, selected, uf.name)
                with open(save_path, "wb") as f:
                    f.write(uf.getbuffer())
                paths.append(save_path)
            ok = project_manager.extract_raw_text(selected, paths)
        if ok:
            st.success("Texto extraído com sucesso!")
        else:
            st.error("Falha na extração de texto.")

# Exibir texto consolidado e permitir edição
categories = project_manager.get_categories(selected)
for cat in categories:
    st.subheader(f"Categoria: {cat}")
    if project_manager.has_extracted_text(selected, cat):
        text = project_manager.load_extracted_text(selected, cat)
        edited = st.text_area(
            label="Revise o texto extraído pela IA antes de prosseguir para verificação",
            value=text,
            height=300,
            key=f"text_{cat}"
        )

        cols = st.columns(3)
        if cols[0].button("Salvar Alterações", key=f"save_{cat}"):
            if project_manager.save_extracted_text(selected, cat, edited):
                st.success("Texto editado salvo com sucesso.")
            else:
                st.error("Erro ao salvar edição.")

        if cols[1].button("Re-extrair Texto", key=f"reextract_{cat}"):
            with st.spinner("Re-extraindo texto..."):
                if project_manager.run_extraction_for_category(selected, cat):
                    st.success("Reextração concluída.")
                else:
                    st.error("Falha na reextração.")

        if cols[2].button("Avançar para Verificação", key=f"next_{cat}"):
            st.experimental_set_query_params(page="4_Verificação_de_Critérios")
            st.experimental_rerun()
    else:
        st.info("Aguardando extração de texto para esta categoria.")
