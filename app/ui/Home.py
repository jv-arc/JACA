import streamlit as st
import os
import platform
import subprocess
from typing import List, Dict, Any


from app.core.config import Settings
from app.core.prompt_manager import PromptManager
from app.core.ai_client import GeminiClient
from app.core.data_manager import ExtractedDataManager
from app.core.project_manager import ProjectManager
from app.core.logger import Logger
from app.core.criteria_manager import CriteriaManager
from app.core.export_manager import ExportManager
from app.core.pdf_generator import PdfGenerator
from app.core.report_config_manager import ReportConfigManager

# ===============================
# 1. INICIALIZAÇÃO DOS SERVIÇOS
# ===============================

# Garante que este bloco execute apenas uma vez por sessão
@st.cache_resource
def initialize_services():
    settings = Settings()
    prompt_manager = PromptManager()
    pm_logger = Logger(name='ProjectManager')
    dm_logger = Logger(name='DataManager')
    gc_logger = Logger(name='GeminiClient')
    cm_logger = Logger(name='CriteriaManager')
    em_logger = Logger(name='ExportManager')
    pdf_logger = Logger(name='PdfGenerator')
    rcm_logger = Logger(name='ReportConfigManager')
    ui_logger = Logger(name='StreamlitUI')

    # Cliente da IA
    gemini_client = GeminiClient(
        settings=settings, 
        logger=gc_logger
    )

    # Manager de Extração
    extraction_manager = ExtractedDataManager(
        gemini_client=gemini_client,
        prompt_manager=prompt_manager,
        logger=dm_logger
    )

    # Manager de Extração
    criteria_manager = CriteriaManager(
        gemini_client=gemini_client,
        prompt_manager=prompt_manager,
        logger=cm_logger
    )

     
    report_config_manager = ReportConfigManager(
        logger=rcm_logger
    )

    pdf_generator = PdfGenerator(
        logger=pdf_logger
    )

    export_manager = ExportManager(
        logger=em_logger,
        pdf_generator=pdf_generator,
        report_config_manager=report_config_manager
    )


    # Manager de Projeto
    project_manager = ProjectManager(
        extraction_manager=extraction_manager,
        criteria_manager=criteria_manager,
        export_manager=export_manager,
        logger=pm_logger,
        projects_dir="data/projects"
    )
    
    ui_logger.info("✅ Aplicação iniciada e serviços carregados.")

    return {
            'project_manager': project_manager,
            'ui_logger': ui_logger,
            'report_config_manager': report_config_manager
        }

# Carrega os serviços
services = initialize_services()

st.session_state['project_manager'] = services['project_manager']
st.session_state['ui_logger'] = services['ui_logger']

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E FUNÇÕES UTILITÁRIAS
# ==============================================================================

st.set_page_config(
    page_title="Assistente de Outorga",
    page_icon="📑",
    layout="centered"
)

def open_file_with_default_app(file_path: str):
    """Abre um arquivo com o aplicativo padrão do sistema operacional."""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            st.error(f"Sistema operacional não suportado: {system}")
    except Exception as e:
        st.error(f"Erro ao abrir arquivo: {e}")

# ==============================================================================
# 3. FUNÇÕES DE RENDERIZAÇÃO DA UI (Para evitar repetição de código)
# ==============================================================================
def display_files_for_category(category_key: str, files: List[str], project_name: str):
    """Mostra a lista de arquivos de uma categoria com botões de ação."""
    for i, file_path in enumerate(files):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            file_name = os.path.basename(file_path)
            file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB" if os.path.exists(file_path) else "N/A"
            st.markdown(f"📄 **{file_name}** `({file_size})`")
        with col2:
            if st.button("Ver", key=f"view_{category_key}_{i}", use_container_width=True):
                open_file_with_default_app(file_path)
        with col3:
            if st.button("Remover", key=f"remove_{category_key}_{i}", type="secondary", use_container_width=True):
                if project_manager.remove_pdf_file(project_name, file_path, category_key):
                    st.toast(f"Arquivo '{file_name}' removido.")
                    st.rerun()
                else:
                    st.error("Falha ao remover o arquivo.")

def render_category_uploader(category_config: Dict[str, Any], project_data: Any):
    """Renderiza uma seção completa de upload e listagem para uma categoria."""
    st.markdown(f"### {category_config['title']}")
    st.caption(category_config['description'])

    category_key = category_config['key']
    project_name = project_data.name
    files = project_data.base_files.get(category_key, [])
    
    # Mostra os arquivos existentes
    if files:
        display_files_for_category(category_key, files, project_name)
        expander_title = "Adicionar/Substituir Arquivos"
    else:
        st.warning(f"⚠️ Nenhum arquivo para a categoria '{category_config['title']}'.")
        expander_title = f"Adicionar Arquivos de {category_config['title']}"

    # Expander para adicionar novos arquivos
    with st.expander(expander_title):
        uploaded_files = st.file_uploader(
            "Selecione os arquivos",
            key=f"upload_{category_key}",
            type=['pdf', 'docx'],
            accept_multiple_files=category_config.get('multiple', True),
            label_visibility="collapsed"
        )
        
        files_to_upload = uploaded_files if isinstance(uploaded_files, list) else [uploaded_files]
        
        if st.button(f"Salvar no Projeto", key=f"save_{category_key}", type="primary", disabled=not uploaded_files):
            success_count = 0
            for uploaded_file in files_to_upload:
                if uploaded_file: # Garante que o arquivo não é None
                    if project_manager.add_pdf_file(project_name, uploaded_file, category_key):
                        success_count += 1
            if success_count > 0:
                st.toast(f"{success_count} arquivo(s) adicionado(s) com sucesso!")
                st.rerun()

# ==============================================================================
# 4. LÓGICA PRINCIPAL DA APLICAÇÃO
# ==============================================================================
st.title("🤖 Assistente de Outorga para Rádios Comunitárias")

# Garante que a sessão está inicializada
if 'current_project' not in st.session_state:
    st.session_state.current_project = None

# ---- SE UM PROJETO ESTÁ SELECIONADO ----
if st.session_state.current_project:
    project_name = st.session_state.current_project
    
    # Cabeçalho da página do projeto
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"**Projeto Aberto:** `{project_name}`")
    with col2:
        if st.button("🔄 Trocar de Projeto", use_container_width=True):
            st.session_state.current_project = None
            st.rerun()

    st.markdown("Gerencie aqui os documentos do seu projeto. Faça o upload dos arquivos necessários para cada categoria antes de prosseguir para a extração de dados.")
    st.divider()

    # Carrega os dados do projeto UMA VEZ
    project_manager.verify_and_fix_file_paths(project_name)
    project_data = project_manager.load_project(project_name)

    if not project_data:
        st.error("Falha fatal ao carregar o projeto. Tente novamente ou crie um novo.")
        st.session_state.current_project = None
        st.stop()

    # Define a configuração para cada categoria de documento
    CATEGORIES = [
        {'key': 'estatuto', 'title': 'Estatuto da Organização', 'description': 'Faça o upload do arquivo do estatuto social, em PDF ou DOCX.', 'multiple': False},
        {'key': 'ata', 'title': 'Ata de Eleição da Última Diretoria', 'description': 'Anexe a ata de eleição e posse da diretoria atual.'},
        {'key': 'identificacao', 'title': 'Documentos de Identificação dos Diretores', 'description': 'Anexe os RGs e CPFs de todos os diretores.'},
        {'key': 'licenca', 'title': 'Licença de Funcionamento (se houver)', 'description': 'Anexe licenças prévias ou existentes.'},
        {'key': 'programacao', 'title': 'Grade de Programação', 'description': 'Anexe o documento com a grade de programação semanal.'}
    ]

    # Renderiza a UI para cada categoria usando um loop
    for category in CATEGORIES:
        render_category_uploader(category, project_data)
        st.divider()
    
    st.info("💡 **Pronto?** Prossiga para a página **Extrair Texto** no menu ao lado para iniciar a análise com IA.")

# ---- SE NENHUM PROJETO ESTÁ SELECIONADO ----
else:
    st.markdown("### Selecione um projeto ou crie um novo para começar.")
    
    # Seção para CRIAR um novo projeto
    with st.form("new_project_form"):
        new_project_name = st.text_input("Nome para o Novo Projeto")
        submitted = st.form_submit_button("Criar Projeto", type="primary", use_container_width=True, disabled=not new_project_name)
        if submitted:
            if project_manager.create_project(new_project_name):
                st.session_state.current_project = new_project_name
                st.rerun()
            else:
                st.error(f"Um projeto com o nome '{new_project_name}' já existe.")

    st.divider()

    # Seção para CARREGAR um projeto existente
    existing_projects = project_manager.list_projects()
    if existing_projects:
        with st.form("load_project_form"):
            selected_project = st.selectbox("Ou selecione um projeto existente", existing_projects)
            submitted = st.form_submit_button("Carregar Projeto", use_container_width=True)
            if submitted:
                st.session_state.current_project = selected_project
                st.rerun()
    else:
        st.info("Nenhum projeto encontrado. Crie seu primeiro projeto acima!")