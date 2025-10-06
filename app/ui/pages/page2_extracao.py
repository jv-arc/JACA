import streamlit as st
import os
from typing import Dict, List, Any
from app.core.logger import Logger



#-------------------------------------------------------------------------------
# Configuração Básica da página
#-------------------------------------------------------------------------------

project_manager = st.session_state.get('project_manager')
current_project = st.session_state.get('current_project')
logger = Logger("UI-Extracao")

st.set_page_config(
    page_title="Extração de Texto", 
    page_icon="📄", 
    layout="centered"
)

# era uma abstrair isso em uma classe
CATEGORIES = {
    'estatuto': {'name': 'Estatuto', 'description': 'Documentos do estatuto da organização'},
    'ata': {'name': 'Ata', 'description': 'Atas de reuniões e assembleias'},
    'identificacao': {'name': 'Identificação', 'description': 'Documentos de identificação dos membros'},
    'licenca': {'name': 'Licença', 'description': 'Licenças e autorizações'},
    'programacao': {'name': 'Programação', 'description': 'Documentos de programação e cronogramas'}
}





#==============================================================================
# Funções Auxiliares
#==============================================================================


#---------------------------------------------------------------
# Função+ para chamar o backend para extrair o consolidated_text.
#---------------------------------------------------------------
#def handle_extraction(category_key: str):
#    # project_files = project_manager.list_files_in_category(current_project, category_key)
#    return project_manager.run_extraction(current_project, category_key)



#------------------------------------------------------------------
# Salva o texto editado e aciona a extração secundária dos campos.
#------------------------------------------------------------------
def handle_save_and_extract_fields(category_key: str, edited_text: str) -> bool:
    with st.spinner("Salvando texto e atualizando campos para o relatório..."):


        # -- Salva dados corrigidos --
        if not project_manager.save_edited_text(current_project, category_key, edited_text):
            st.error("Erro ao salvar o texto principal.")
            return False


        # -- Roda extracao secundaria --
        if not project_manager.run_secondary_extraction(current_project, category_key):
            st.warning("Texto salvo, mas falha ao pré-extrair campos para o relatório.")
            return False


    st.toast("✅ Texto salvo e campos do relatório atualizados com sucesso!", icon="🎉")
    return True

#---------------------------------------------------------------
# Renderiza a UI para quando a extração ainda não foi feita.
#---------------------------------------------------------------
def render_extraction_interface(category_key: str, category_info: Dict, files: List):
    st.success(f"✅ {len(files)} arquivo(s) encontrado(s) para extração:")

    # -- Loop pelos arquivos --
    for i, file_path in enumerate(files, 1):
        st.markdown(f"&nbsp;&nbsp;&nbsp; {i}. `{os.path.basename(file_path)}`")
    
    st.write("") # Espaçamento
    
    # -- Botão --
    if st.button(f"🤖 Iniciar Extração de IA para **{category_info['name']}**", key=f"extract_{category_key}", type="primary", use_container_width=True):
        with st.spinner(f"Analisando documentos e extraindo dados de '{category_info['name']}'..."):

            success = project_manager.run_extraction(current_project, category_key) #<-- Chama extracao

            if success:
                st.success(f"✅ Extração de '{category_info['name']}' concluída!")
                logger.info(f"Extração de '{category_info['name']}' concluída com sucesso")
                st.rerun()
            else:
                st.error(f"❌ Erro ao extrair dados de '{category_info['name']}'. Tente de novo mais tarde")
                logger.info(f"Erro na extração de '{category_info['name']}'")



#--------------------------------------------------------------------
# Renderiza a seção interativa para gerenciar a lista de dirigentes.
#--------------------------------------------------------------------
def render_director_editor():
    # -- Cabecalho simples --
    st.markdown(f"#### 👥 Qualificação dos Dirigentes")
    st.caption("Verifique, corrija e complete os dados dos dirigentes. Use os botões para adicionar ou remover membros da lista.")


    # -- Se nao tiver dirigentes --
    if 'dirigentes_editor' not in st.session_state:
        # Lista de IA como ponto de partida
        initial_list = project_manager.get_director_list_from_content(current_project) or []
        st.session_state.dirigentes_editor = initial_list if isinstance(initial_list, list) else []


    # -- Loop pelos dirigentes para renderizacao --
    for i in range(len(st.session_state.dirigentes_editor)):
        if i >= len(st.session_state.dirigentes_editor): #Evita acessar um índice removido
            break
        
        dirigente = st.session_state.dirigentes_editor[i]

        #Renderiza dirigente
        with st.container(border=True):
            cols_1 = st.columns([4, 4, 1])
            dirigente['nome'] = cols_1[0].text_input("Nome Completo", value=dirigente.get('nome', ''), key=f"dir_nome_{i}")
            dirigente['cargo'] = cols_1[1].text_input("Cargo", value=dirigente.get('cargo', ''), key=f"dir_cargo_{i}")
            if cols_1[2].button("🗑️", key=f"remove_dir_{i}", help="Remover Dirigente"):
                st.session_state.dirigentes_editor.pop(i)
                st.rerun()



    # -- Botão Para adicionar Dirigentes --
    if st.button("➕ Adicionar Dirigente", type="secondary"):
        st.session_state.dirigentes_editor.append({'nome': '', 'cargo': ''})
        logger.info("Drigente adicionado")
        st.rerun()



#---------------------------------------------------------------
# Renderiza a UI para quando os dados já foram extraídos.
#---------------------------------------------------------------
def render_editing_interface(category_key: str, category_info: Dict, files: List):
    extracted_text = project_manager.load_extracted_text(current_project, category_key)
    if extracted_text is None:
        st.error(f"Erro ao carregar o texto extraído de {category_info['name']}.")
        logger.error(f"Erro ao carregar o texto extraído de {category_info['name']}.")
        return


    # -- Exibe arquivos fonte --
    with st.expander(f"📁 Ver arquivos fonte ({len(files)})"):
        for i, file_path in enumerate(files, 1):
            st.markdown(f"&nbsp;&nbsp;&nbsp; {i}. `{os.path.basename(file_path)}`")
    
    # -- Campo para edicao --
    st.write("**Texto Consolidado (Revisável):**")
    edited_text = st.text_area(
        label="Revise o texto extraído pela IA. Suas correções aqui serão a base para a análise de critérios e para o preenchimento do relatório final.",
        value=extracted_text,
        height=300,
        key=f"text_{category_key}"
    )
    


    # -- Seção do Editor de Dirigentes (se a categoria for 'ata') --
    if category_key == 'ata':
        st.divider()
        render_director_editor()
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Salvar Texto e Atualizar Campos", key=f"save_{category_key}", type="primary", use_container_width=True):
            handle_save_and_extract_fields(category_key, edited_text) # <-- Roda IA para extracao secundaria

    with col2:
        # Botao para extrair com IA
        if st.button("🔄 Re-extrair Texto com IA", key=f"reextract_{category_key}", use_container_width=True):
            st.session_state.reextract_confirmed = True


            # Funcao aninhada aqui nao e um erro
            # -- Dialogo para reextracao --
            @st.dialog("Confirmar Re-extração")
            def confirm_reextraction():
                st.warning("⚠️ Isso irá sobrescrever o texto atual e as edições manuais. Confirme para continuar.")
                if st.button("Confirmar e Re-extrair", type="primary"):
                    st.session_state.reextract_confirmed = False

                    # -- Realiza a Rextracao --
                    with st.spinner(f"Re-extraindo texto de '{category_info['name']}'..."):
                        success = handle_extraction(category_key)

                        if success:
                            logger.info(f"Texto de '{category_info['name']}' reextraído com sucesso.")
                            st.rerun()
                        else:
                            st.error(f"❌ Erro ao re-extrair dados de '{category_info['name']}'.")
                            logger.error(f"Erro ao re-extrair dados de '{category_info['name']}'")
            
            # roda o dialogo
            confirm_reextraction()


#---------------------------------------------------------------
# Renderiza uma seção completa para uma categoria de documento.
#---------------------------------------------------------------
def render_category_section(category_key: str, category_info: Dict):
    with st.container(border=True):
        
        # -- Cabecalho Simples --
        st.subheader(f"📄 {category_info['name']}")
        st.caption(category_info['description'])

        project_files = project_manager.list_files_in_category(current_project, category_key)


        # -- Caso a Categoria Esteja Vazia -- 
        if not project_files:
            st.warning(f"Nenhum arquivo encontrado. Vá para a página `Home` para fazer o upload dos documentos de '{category_info['name']}'.")
            return


        # -- Caso Tenha dados Extraidos --
        if project_manager.has_extraction_for_category(current_project, category_key):
            render_editing_interface(category_key, category_info, project_files)
            return 

        # -- Caso nao tenham dados --
        else:
            render_extraction_interface(category_key, category_info, project_files)
            return 


# ==============================================================================
# Lógica Principal da Página
# ==============================================================================


# -- Caso a página não tenha sido criada corretamente -- 
if not all([project_manager, current_project]):

    st.error("⚠️ Erro Inesperado no Fluxo de Execução.")
    st.info("Por favor, volte para a página `Home` e selecione ou crie um projeto para continuar.")

    if not current_project:
        logger.error("Usuário chegou na página de Extração sem ter um projeto selecionado, será que a sessão expirou?")

    if not project_manager:
        logger.error("Usuário chegou na página de Extração mas não tem um project_manager na sessão!!! será que a sessão expirou?")
    st.stop()

# -- Caso Normal --
else:
    st.title("📄 Extração e Revisão de Texto")
    logger.info(f"Página de extração carregada com sucesso para o projeto '{current_project}'")
    st.info(f"**Projeto Aberto:** `{current_project}`")
    st.caption("Nesta seção, você pode iniciar a extração de dados com a IA para cada categoria de documento e, posteriormente, revisar e editar o texto consolidado.")
    st.divider()


    for key, info in CATEGORIES.items():
        render_category_section(key, info)