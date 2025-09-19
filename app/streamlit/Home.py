import streamlit as st
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Any

from src.callouts import Callouts
from src.config import Settings
from src.prompt_manager import PromptManager
from src.ai_client import GeminiClient
from src.data_manager import ExtractedDataManager
from src.project_manager import ProjectManager
from src.logger import Logger

# Garante que este bloco execute apenas uma vez por sessão
@st.cacheresource
def initializeservices():
    # 1. Componentes base
    logger = Logger(name="DocAI-App")
    settings = Settings()
    promptmanager = PromptManager()

    # 2. Cliente da IA
    geminiclient = GeminiClient(settings=settings, logger=logger)

    # 3. Manager de Extração
    extractionmanager = ExtractedDataManager(
        geminiclient=geminiclient,
        promptmanager=promptmanager,
        logger=logger
    )

    # 4. Manager de Projeto
    projectmanager = ProjectManager(
        extractionmanager=extractionmanager,
        logger=logger,
        projectsdir="data/projects"
    )

    logger.info("Todos os serviços foram inicializados com sucesso.")
    return projectmanager

# Carrega o gerenciador de projetos na sessão
projectmanager = initializeservices()
st.session_state.projectmanager = projectmanager

# Configura a página
st.set_page_config(
    page_title="Assistente de Outorga",
    page_icon="📑",
    layout="centered"
)

def openfilewithdefaultapp(filepath: str) -> bool:
    try:
        if not os.path.exists(filepath):
            st.error(f"Arquivo não encontrado: {filepath}")
            return False

        system = platform.system()
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":
            subprocess.call(["open", filepath])
        elif system == "Linux":
            subprocess.call(["xdg-open", filepath])
        else:
            st.error(f"Sistema operacional não suportado: {system}")
            return False

        return True
    except Exception as e:
        st.error(f"Erro ao abrir arquivo: {e}")
        return False

# Inicializa sessão
if "currentproject" not in st.session_state:
    st.session_state.currentproject = None

st.title("Assistente de Outorga para Rádios Comunitárias")

if st.session_state.currentproject:
    projectname = st.session_state.currentproject
    col1, col2 = st.columns(3)[0], st.columns(3)[1]

    with col1:
        st.info(f"Projeto Atual: {projectname}")

    with col2:
        if st.button("Trocar de Projeto", type="secondary"):
            st.session_state.currentproject = None
            st.experimental_rerun()

    projectmanager.verify_and_fix_filepaths(projectname)
    projectdata = projectmanager.loadproject(projectname)
    if not projectdata:
        st.error("Falha ao carregar arquivos do projeto.")
        st.stop()

    st.markdown("Nesta página você pode editar e modificar quais arquivos fazem parte do projeto. Selecione os arquivos de ata, estatuto, identificação etc.")
    st.markdown("---")

    def displaycategoryfiles(categoryname: str, files: List[str], categorykey: str):
        if files:
            for i, filepath in enumerate(files):
                col1, col2, col3 = st.columns(4)[0], st.columns(4)[1], st.columns(4)[2]
                with col1:
                    filename = os.path.basename(filepath)
                    if os.path.exists(filepath):
                        size = os.path.getsize(filepath)
                        filesize = f"{size/1024:.1f} KB"
                    else:
                        filesize = "NA"
                    st.markdown(f"{filename} — {filesize}")
                with col2:
                    if st.button("Ver arquivo", key=f"view-{categorykey}-{i}", use_container_width=True):
                        openfilewithdefaultapp(filepath)
                with col3:
                    if st.button("Remover", key=f"remove-{categorykey}-{i}", type="secondary"):
                        if projectmanager.removepdffile(projectname, filepath, categorykey):
                            st.success(f"{filename} removido")
                            st.experimental_rerun()
                        else:
                            st.error(f"Falha ao remover {filename}")

    def handlefileupload(uploadedfiles, categorykey: str):
        if uploadedfiles:
            col1, col2 = st.columns(3)[0], st.columns(3)[1]
            with col2:
                if st.button(f"Add Files to Project", key=f"add-{categorykey}", type="primary"):
                    successcount = 0
                    for uploadedfile in uploadedfiles:
                        if projectmanager.addpdffile(projectname, uploadedfile, categorykey):
                            successcount += 1
                    if successcount > 0:
                        st.success(f"Successfully added {successcount} files to project!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add files to project.")

    basefiles = projectdata.basefiles if hasattr(projectdata, "basefiles") and projectdata.basefiles else {}

    # 1. Estatuto
    st.markdown("**Arquivo do Estatuto**")
    st.markdown("Faça upload do arquivo do estatuto, você deve fazer upload de apenas um arquivo em PDF ou DOCX.")
    estatutofiles = basefiles.get("estatuto", [])
    if not estatutofiles:
        with st.expander("Adicionar Estatuto"):
            uploaded = st.file_uploader("Escolha o arquivo", key="estatuto", type=["pdf", "docx"], accept_multiple_files=False)
            handlefileupload(uploaded, "estatuto")
    else:
        displaycategoryfiles("Estatuto", estatutofiles, "estatuto")
        with st.expander("Substituir Estatuto"):
            uploaded = st.file_uploader("Escolha o arquivo", key="estatuto-replace", type=["pdf", "docx"], accept_multiple_files=False)
            handlefileupload(uploaded, "estatuto")

    st.markdown("---")

    # 2. Ata de Eleição
    st.markdown("**Ata de Eleição da última diretoria**")
    atafiles = basefiles.get("ata", [])
    if not atafiles:
        with st.expander("Adicionar Ata"):
            uploaded = st.file_uploader("Escolha o Arquivo", key="ata", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "ata")
    else:
        displaycategoryfiles("Ata de Eleição", atafiles, "ata")
        with st.expander("Adicionar Mais Atas"):
            uploaded = st.file_uploader("Escolha o Arquivo", key="ata-add", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "ata")

    st.markdown("---")

    # 3. Documentos de Identificação
    st.markdown("**Documentos de Identificação**")
    idfiles = basefiles.get("identificacao", [])
    if not idfiles:
        with st.expander("Adicionar Documentos"):
            uploaded = st.file_uploader("Choose PDF files", key="identificacao", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "identificacao")
    else:
        displaycategoryfiles("Documentos de Identificação", idfiles, "identificacao")
        with st.expander("Adicionar Mais Documentos"):
            uploaded = st.file_uploader("Choose PDF files", key="identificacao-add", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "identificacao")

    st.markdown("---")

    # 4. Licença de Funcionamento
    st.markdown("**Licença de Funcionamento**")
    licfiles = basefiles.get("licenca", [])
    if not licfiles:
        with st.expander("Adicionar Licença"):
            uploaded = st.file_uploader("Choose PDF files", key="licenca", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "licenca")
    else:
        displaycategoryfiles("Licença de Funcionamento", licfiles, "licenca")
        with st.expander("Adicionar Mais Licenças"):
            uploaded = st.file_uploader("Choose PDF files", key="licenca-add", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "licenca")

    st.markdown("---")

    # 5. Grade da Programação
    st.markdown("**Grade da Programação**")
    progfiles = basefiles.get("programacao", [])
    if not progfiles:
        with st.expander("Adicionar Grade"):
            uploaded = st.file_uploader("Choose PDF files", key="programacao", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "programacao")
    else:
        displaycategoryfiles("Grade da Programação", progfiles, "programacao")
        with st.expander("Adicionar Mais Grades"):
            uploaded = st.file_uploader("Choose PDF files", key="programacao-add", type=["pdf"], accept_multiple_files=True)
            handlefileupload(uploaded, "programacao")

    st.markdown("---")
    st.info("Você pode analisar os conteúdos na próxima seção “Extrair Texto” no menu ao lado para iniciar a análise com IA.")

else:
    st.markdown("Selecione um projeto ou crie um novo para começar.")

    with st.form("newprojectform"):
        newprojectname = st.text_input("Nome para o Novo Projeto")
        submitted = st.form_submit_button("Criar Projeto", type="primary")
        if submitted:
            if projectmanager.createproject(newprojectname):
                st.session_state.currentproject = newprojectname
                st.experimental_rerun()
            else:
                st.error(f"Um projeto com o nome {newprojectname} já existe.")

    st.divider()

    existing = projectmanager.listprojects()
    if existing:
        with st.form("loadprojectform"):
            selected = st.selectbox("Ou selecione um projeto existente", existing)
            submitted = st.form_submit_button("Carregar Projeto")
            if submitted:
                st.session_state.currentproject = selected
                st.experimental_rerun()
    else:
        st.info("Nenhum projeto encontrado. Crie seu primeiro projeto acima!")
