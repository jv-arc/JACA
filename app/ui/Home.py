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
from app.core.path_manager import PathManager

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
        export_manager=export_manager,
        extraction_manager=extraction_manager,
        logger=pm_logger,
        report_config_manager=report_config_manager,
        criteria_manager=criteria_manager,
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

project_manager = st.session_state.get('project_manager')
ui_logger = st.session_state.get('ui_logger')


if 'project' not in st.session_state:
    st.session_state['project'] = None



page1 = st.Page(PathManager.get_page_str('page1_projeto.py'), title="Projetos", icon="📡", default =True) 
#...
page5 = st.Page(PathManager.get_page_str('page5_configuracao.py'), title="Configuração", icon="⚙️") 
page6 = st.Page(PathManager.get_page_str('page6_sobre.py'), title="Sobre", icon="ℹ️") 


pages = [page1, page5, page6]


if st.session_state['project'] is not None:
    page2 = st.Page(PathManager.get_page_str('page2_extracao.py'), title="Extração de Texto", icon="📄") 
    page3 = st.Page(PathManager.get_page_str('page3_verificacao.py'), title="Verificação de Critérios", icon="✔️") 
    page4 = st.Page(PathManager.get_page_str('page4_exportacao.py'), title="Exportar Requisição", icon="🚀")

    pages = [page1, page2, page3, page4, page5, page6]

pg = st.navigation(pages)
pg.run()