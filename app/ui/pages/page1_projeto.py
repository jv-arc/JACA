import streamlit as st
import os
import platform
import subprocess
from typing import List, Dict, Any
from app.core.logger import Logger

#-----------------------------------------------------------------
# Configuração básica da página
#-----------------------------------------------------------------

project_manager = st.session_state.get("project_manager")
logger = Logger("UI-Projeto")

st.set_page_config(
    page_title="JACA - Assistente de Outorga",
    page_icon="📡",
    layout="centered"
)





#=================================================================
# Funções utilitárias da página
#-----------------------------------------------------------------
# funções para listar arquivos, abrir arquivos e renderizar listas
#=================================================================



#-----------------------------------------------------------------
# Abre um arquivo com o aplicativo padrão do sistema operacional.
#-----------------------------------------------------------------
def open_file_with_default_app(file_path: str):
    logger.info("Identificando Sistema Operacional")

    try:
        system = platform.system()

        if system == "Windows":
            logger.info("Sistem Windows Identificado")
            os.startfile(file_path)

        elif system == "Darwin":
            logger.info("Sistem Darwin Identificado")
            subprocess.run(["open", file_path], check=True)

        elif system == "Linux":
            logger.info("Sistem Linux Identificado")
            subprocess.run(["xdg-open", file_path], check=True)

        else:
            st.error(f"Sistema operacional não suportado: {system}")
            logger.error(f"Sistema Operacional não suportado: {system}")

    except Exception as e:
        st.error(f"Erro ao abrir arquivo")
        logger.error(f"Erro ao abrir arquivo: {e}")


#-----------------------------------------------------------------------
# Mostra a lista de arquivos de uma única categoria com botões de ação.
#-----------------------------------------------------------------------
def display_files_for_category(category_key: str, files: List[str], project_name: str)-> None:
    for i, file_path in enumerate(files):
        col1, col2, col3 = st.columns([4, 1, 1])

        # -- Informacoes do Arquivo --
        with col1:
            file_name = os.path.basename(file_path)
            file_size = f"{os.path.getsize(file_path) / 1024:.1f} KB" if os.path.exists(file_path) else "N/A"
            st.markdown(f"📄 **{file_name}** `({file_size})`")

        # -- Botao para abrir arquivo --
        with col2:
            if st.button("Ver", key=f"view_{category_key}_{i}", use_container_width=True):
                open_file_with_default_app(file_path)
        
        # -- Botao de Remover --
        with col3:
            if st.button("Remover", key=f"remove_{category_key}_{i}", type="secondary", use_container_width=True):
                try: 
                    project_manager.remove_file(project_name, file_path)
                    logger.info(f"Arquivo '{file_name}' do projeto '{project_name}' com caminho '{file_path}' removido da categoria '{category}'")
                    st.toast(f"Arquivo '{file_name}' removido.")
                    st.rerun()

                except Exception as e:
                    st.error("Falha ao remover o arquivo.")
                    logger.error(f"Erro ao remover arquivo '{file_name}' do projeto '{project_name}' com caminho '{file_path}' removido da categoria '{category}' \n\n {e}")


#--------------------------------------------------------------------------------------
# Renderiza um container para exibir a seção de upload e remoção de uma única categoria
#--------------------------------------------------------------------------------------
def render_category_uploader(category_config: Dict[str, Any], project_data: Any):
    st.markdown(f"### {category_config['title']}")
    st.caption(category_config['description'])

    category_key = category_config['key']
    project_name = project_data.name
    files = project_data.base_files.get(category_key, [])
    
    # -- Mostra a Listagem criada por `display_files_for_category` --
    if files:
        display_files_for_category(category_key, files, project_name)
        expander_title = "Adicionar/Substituir Arquivos"
    else:
        st.warning(f"⚠️ Nenhum arquivo para a categoria '{category_config['title']}'.")
        expander_title = f"Adicionar Arquivos de {category_config['title']}"
        logger.info(f"Categoria '{category_key}' para projeto '{project_name}' não possui nenhum arquivo")

    # --- Expander para adicionar novos arquivos ----
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

            # -- Adiciona todos os arquivos da lista --
            for uploaded_file in files_to_upload:
                if uploaded_file: # Garante que o arquivo não é None

                    if project_manager.add_file(project_name, uploaded_file, category_key):
                        logger.info(f"Arquivo '{uploaded_file}' adicionado ao projeto '{project_name}' na categoria '{category_key}' com sucesso")
                        success_count += 1
                    else:
                        logger.error(f"Erro ao adicionar arquivo '{uploaded_file}' ao projeto '{project_name}' na categoria '{category_key}'")

            # -- Usa `succes_count` para determinar mensagem --
            if success_count == 1:
                st.toast(f"{success_count} arquivo adicionado com sucesso!")
                st.rerun()
            elif success_count > 1:
                st.toast(f"{success_count} arquivos adicionados com sucesso!")
                st.rerun()
            else:
                st.warning(f"Nenhum arquivo adicionado....")
                st.rerun()




#==============================================================================
# LÓGICA PRINCIPAL DA PÁGINA
#------------------------------------------------------------------------------
# 
#==============================================================================
st.title("Assistente de Outorga para Rádios Comunitárias")

# -- Garante que a sessão está inicializada --
if 'current_project' not in st.session_state:
    st.session_state.current_project = None


#-----------------------------------------------------------------
# SÓ RODA SE UM PROJETO ESTÁ SELECIONADO 
#-----------------------------------------------------------------
if st.session_state.current_project:
    project_name = st.session_state.current_project
    
    # -- Cabeçalho simples para página do projeto --
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"**Projeto Aberto:** `{project_name}`")
    with col2:
        if st.button("🔄 Trocar de Projeto", use_container_width=True):
            st.session_state.current_project = None
            st.rerun()

    st.markdown("Gerencie aqui os documentos do seu projeto. Faça o upload dos arquivos necessários para cada categoria antes de prosseguir para a extração de dados.")
    st.divider()



    # -- Carrega os dados na memória do projeto UMA VEZ --
    try:
        project_data = project_manager.load_project(project_name)
        logger.info(f"Dados do projeto '{project_name}' foram carregados com sucesso")

    except Exception as e:
        st.error("Falha fatal ao carregar o projeto. Tente novamente ou crie um novo.")
        logger.error(f"Falaha ao tentar carregar dados do projeto '{project_name}' \n\n {e}")
        st.session_state.current_project = None
        st.stop()



    # -- Define a configuração para cada categoria de documento -- 
    CATEGORIES = [
        {'key': 'estatuto', 'title': 'Estatuto da Organização', 'description': 'Faça o upload do arquivo do estatuto social, em PDF ou DOCX.', 'multiple': False},
        {'key': 'ata', 'title': 'Ata de Eleição da Última Diretoria', 'description': 'Anexe a ata de eleição e posse da diretoria atual.'},
        {'key': 'identificacao', 'title': 'Documentos de Identificação dos Diretores', 'description': 'Anexe os RGs e CPFs de todos os diretores.'},
        {'key': 'licenca', 'title': 'Licença de Funcionamento (se houver)', 'description': 'Anexe licenças prévias ou existentes.'},
        {'key': 'programacao', 'title': 'Grade de Programação', 'description': 'Anexe o documento com a grade de programação semanal.'}
    ]



    # -- Renderiza a UI para cada categoria com um loop --
    for category in CATEGORIES:
        render_category_uploader(category, project_data)
        st.divider()
    
    st.info("💡 **Pronto?** Prossiga para a página **Extrair Texto** no menu ao lado para iniciar a análise com IA.")




#-----------------------------------------------------------------
# CASO  NENHUM PROJETO ESTEJA SELECIONADO 
#-----------------------------------------------------------------
else:
    st.markdown("### Selecione um projeto ou crie um novo para começar.")
    



    # -- Sessão Para Criar um projeto Novo --
    new_project_name = st.text_input("Nome para o Novo Projeto")
    if st.button("Criar Projeto", type="primary", use_container_width=True, disabled=not new_project_name):
        if project_manager.create_project(new_project_name):
            st.session_state.current_project = new_project_name
            logger.info(f"Projeto '{new_project_name}' criado com sucesso")
            st.rerun()
        else:
            # Preciso verificar isso daqui
            st.error(f"Um projeto com o nome '{new_project_name}' já existe.")
    st.divider()





    # -- Sessão para CARREGAR um projeto existente --
    existing_projects = project_manager.list_projects()
    if existing_projects:
        with st.form("load_project_form"):
            selected_project = st.selectbox("Ou selecione um projeto existente", existing_projects)
            submitted = st.form_submit_button("Carregar Projeto", use_container_width=True)
            if submitted:
                st.session_state.current_project = selected_project
                logger.info(f"Carregando projeto `{selected_project}`")
                st.rerun()
    else:
        # Caaso não haja projetos disponíveis
        st.info("Nenhum projeto encontrado. Crie seu primeiro projeto acima!")
        logger.info("Nenhum projeto encontrado")
