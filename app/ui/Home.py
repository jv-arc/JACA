import streamlit as st

from app.core.ai_client import GeminiClient
from app.core.project_manager import ProjectManager
from app.core.logger import Logger
from app.core.export_manager import ExportManager
from app.core.path_manager import PathManager
from app.core.project_data_service import ProjectDataService
from app.core.project_workflow_orchestrator import ProjectWorkflowOrchestrator
from app.core.project_crud_service import ProjectCRUDService
from app.core.project_file_manager import ProjectFileManager
from app.core.project_configuration_service import ProjectConfigurationService
from app.core.document_package_service import DocumentPackageService

@st.cache_resource
def initialize_services():
    ui_logger = Logger(name='Init-Home')

    ai = GeminiClient()

    crud = ProjectCRUDService()
    file = ProjectFileManager()
    path = PathManager()
    export = ExportManager()
    config = ProjectConfigurationService()
    package = DocumentPackageService()

    data = ProjectDataService(gemini_client=ai)
    workflow = ProjectWorkflowOrchestrator(gemini_client=ai)


    project_manager = ProjectManager(
        data_service = data,
        workflow_orchestrator = workflow,
        crud_service = crud,
        file_manager = file,
        path_manager = path,
        export_manager = export,
        config_service = config,
        document_package_service = package 
    )
    
    ui_logger.info("✅ Aplicação iniciada e serviços carregados.")

    return {
            'project_manager': project_manager,
            'ui_logger': ui_logger,
        }

# Carrega os serviços
services = initialize_services()


pm = services['project_manager']
ui_log = services['ui_logger']

st.session_state['project_manager'] = pm
st.session_state['ui_logger'] = ui_log



if 'current_project' not in st.session_state:
    st.session_state['current_project'] = None



page1 = st.Page(PathManager.get_page_str('page1_projeto.py'), title="Projetos", icon="📡", default =True) 

page5 = st.Page(PathManager.get_page_str('page5_configuracao.py'), title="Configuração", icon="⚙️") 
page6 = st.Page(PathManager.get_page_str('page6_sobre.py'), title="Sobre", icon="ℹ️") 


pages = [page1, page5, page6]


if st.session_state['current_project'] is not None:
    page2 = st.Page(PathManager.get_page_str('page2_extracao.py'), title="Extração de Texto", icon="📄") 
    page3 = st.Page(PathManager.get_page_str('page3_verificacao.py'), title="Verificação de Critérios", icon="✔️") 
    page4 = st.Page(PathManager.get_page_str('page4_exportacao.py'), title="Exportar Requisição", icon="🚀")

    pages = [page1, page2, page3, page4, page5, page6]

pg = st.navigation(pages)
pg.run()