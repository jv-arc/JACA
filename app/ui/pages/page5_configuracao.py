import streamlit as st
import json

# ==============================================================================
# FUNÇÕES DE RENDERIZAÇÃO DA UI
# ==============================================================================


#----------------------------------------------------------------------------
# Renderiza a seção para configurar a chave de API do Google.
#----------------------------------------------------------------------------
def render_api_section(project_manager):
    st.subheader("🔑 Chave de API do Google Gemini")
    st.caption(
        "Sua chave de API é necessária para todas as funcionalidades de IA. "
        "Ela é salva localmente no arquivo `src/config/config.json` e não é compartilhada."
    )

    current_key = project_manager.get_current_api_key()
    new_key = st.text_input(
        "Sua Chave de API",
        value=current_key,
        type="password",
        help="Obtenha sua chave no Google AI Studio."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salvar Chave de API", type="primary", use_container_width=True, disabled=new_key == current_key):
            project_manager.update_api_key(new_key)
            st.rerun()

    with col2:
        if st.button("🧪 Testar Conexão", use_container_width=True, disabled=not current_key):
            with st.spinner("Testando conexão com a API..."):
                success, message = project_manager.test_api_connection()
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")



#----------------------------------------------------------------------------
# Renderiza a seção para editar os valores padrão do relatório.
#----------------------------------------------------------------------------
def render_defaults_section(project_manager) -> None:
    st.subheader("📝 Padrões do Relatório de Requisição")
    st.caption("Edite os valores padrão que serão usados ao gerar um novo relatório de requisição. Essas alterações serão salvas para todos os projetos.")

    report_config = project_manager.get_report_config()
    
    with st.form("defaults_form"):
        new_config = report_config.copy()
        
        # Itera sobre as tabelas para encontrar os campos de 'user_input'
        for table in new_config.get('tables', []):
            with st.container(border=True):
                st.markdown(f"**{table['header']}**")
                for field in table.get('fields', []):
                    if field.get('source') == 'user_input':
                        field_id = field['id']
                        # Atualiza o valor no dicionário com o que o usuário digitar
                        field['default'] = st.text_input(
                            label=field['label'],
                            value=field.get('default', ''),
                            key=f"default_{field_id}"
                        )
        
        submitted = st.form_submit_button("Salvar Padrões do Relatório", type="primary", use_container_width=True)
        if submitted:
            if project_manager.save_report_configuration(new_config):
                st.success("Valores padrão do relatório salvos com sucesso!")
            else:
                st.error("Ocorreu um erro ao salvar a configuração.")




#----------------------------------------------------------------------------
# Renderiza a seção de configurações avançadas em um expansor.
#----------------------------------------------------------------------------
def render_advanced_section(project_manager, criteria_db_path:str)-> None:
    with st.expander("🔧 Configurações Avançadas"):
        st.markdown("**Modelos de IA**")
        st.caption("Selecione os modelos Gemini a serem usados para diferentes tarefas.")
        
        col1, col2 = st.columns(2)
        with col1:
            extraction_model = st.selectbox(
                "Modelo para Extração de Dados",
                options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
                index=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-2.5-flash", "gemini-2.0-flash"].index(project_manager.get_extraction_model() or "gemini-1.5-flash")
            )
        with col2:
            criteria_model = st.selectbox(
                "Modelo para Análise de Critérios",
                options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-2.5-flash", "gemini-2.0-flash"],
                index=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-2.5-flash", "gemini-2.0-flash"].index(project_manager.get_criteria_model() or "gemini-1.5-flash")
            )

        if st.button("Salvar Modelos de IA"):
            project_manager.update_extraction_model(extraction_model)
            project_manager.update_criteria_model(criteria_model)
            st.success("Modelos de IA atualizados!")

        st.divider()

        # --- Banco de Critérios ---
        st.markdown("**Banco de Dados de Critérios**")
        st.caption(f"Abaixo está o conteúdo do arquivo `{criteria_db_path}`. Para editar, altere o arquivo diretamente e recarregue a aplicação.")
        
        try:
            with open(f"{criteria_db_path}", "r", encoding="utf-8") as f:
                criteria_content = json.load(f)
            st.json(criteria_content, expanded=False)
        except Exception as e:
            st.error(f"Não foi possível carregar o arquivo de critérios: {e}")
        
        st.divider()

        # --- Modo Debug ---
        #st.markdown("**Modo de Depuração (Logging)**")
        #debug_mode = st.checkbox("Habilitar modo de depuração", value=settings.debug_mode, help="Mostra logs mais detalhados no console para solução de problemas.")
        #if debug_mode != settings.debug_mode:
        #    settings.update_debug_mode(debug_mode)
        #    st.success(f"Modo de depuração {'ativado' if debug_mode else 'desativado'}.")
        #    st.rerun()


# ==============================================================================
#  EXECUÇÃO DA PÁGINA
# ==============================================================================

st.set_page_config(page_title="Configurações", page_icon="⚙️", layout="wide")
st.title("⚙️ Configurações Gerais")

# Carrega os serviços da sessão
project_manager = st.session_state.get('project_manager')
ui_logger = st.session_state.get('ui_logger')

if not all([project_manager, ui_logger]):
    st.error("⚠️ Serviços não inicializados. Por favor, volte para a página Home.")
    st.stop()
else:
    render_api_section(project_manager)
    st.divider()
    render_defaults_section(project_manager)
    st.divider()
    render_advanced_section(project_manager, project_manager.get_criteria_db_path())
