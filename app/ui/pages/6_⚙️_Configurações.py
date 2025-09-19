import streamlit as st
from app.core.config import Settings

# Inicializa configurações
settings = Settings()

# Configuração da página
st.set_page_config(page_title="Configurações Gerais", page_icon="⚙️", layout="wide")
st.title("Configurações Gerais")

# Verifica serviços
projectmanager = st.session_state.get("projectmanager")
uilogger = st.session_state.get("uilogger")
if not projectmanager or not uilogger:
    st.error("Serviços não inicializados. Por favor, volte para a página Home.")
    st.stop()

def render_api_section():
    st.subheader("Chave de API do Google Gemini")
    st.caption(
        "Sua chave de API necessária para todas as funcionalidades de IA. "
        "Ela é salva localmente em src/config/config.json e no armazenamento compartilhado."
    )
    current_key = settings.apikey
    new_key = st.text_input(
        "Sua Chave de API",
        value=current_key,
        type="password",
        help="Obtenha sua chave no Google AI Studio."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Salvar Chave de API",
            type="primary",
            use_container_width=True,
            disabled=(new_key == current_key)
        ):
            settings.updateapikey(new_key)
            st.success("Chave de API salva com sucesso! A aplicação irá recarregar para usar a nova chave.")
            st.info("Pode ser necessário reiniciar o Streamlit para que as alterações tenham efeito completo.")
            st.experimental_rerun()
    with col2:
        if st.button("Testar Conexão", use_container_width=True, disabled=(not current_key)):
            with st.spinner("Testando conexão com a API..."):
                success, message = projectmanager.testapiconnection()
                if success:
                    st.success(message)
                else:
                    st.error(message)

def render_defaults_section():
    st.subheader("Padrões do Relatório de Requisição")
    st.caption(
        "Edite os valores padrão que serão usados ao gerar um novo relatório de requisição. "
        "Essas alterações serão salvas para todos os projetos."
    )
    reportconfig = projectmanager.getreportconfiguration()
    with st.form("defaults_form"):
        newconfig = reportconfig.copy()
        for table in newconfig.gettables():
            with st.container():
                st.markdown(f"### {table.getheader()}")
                for field in table.getfields():
                    if field.getsource() == "userinput":
                        fid = field.getid()
                        val = st.text_input(
                            field.getlabel(),
                            value=field.getdefault(),
                            key=f"default_{fid}"
                        )
                        newconfig.updatefielddefault(fid, val)
        submitted = st.form_submit_button(
            "Salvar Padrões do Relatório",
            type="primary",
            use_container_width=True
        )
        if submitted:
            if projectmanager.savereportconfiguration(newconfig):
                st.success("Valores padrão do relatório salvos com sucesso!")
            else:
                st.error("Ocorreu um erro ao salvar a configuração.")

def render_advanced_section():
    with st.expander("Configurações Avançadas"):
        # Modelos de IA
        st.markdown("### Modelos de IA")
        st.caption("Selecione os modelos Gemini a serem usados para diferentes tarefas.")
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
        col1, col2 = st.columns(2)
        with col1:
            extraction_model = st.selectbox(
                "Modelo para Extração de Dados",
                options=models,
                index=models.index(settings.extractionmodel)
            )
        with col2:
            criteria_model = st.selectbox(
                "Modelo para Análise de Critérios",
                options=models,
                index=models.index(settings.criteriamodel)
            )
        if st.button("Salvar Modelos de IA"):
            settings.updateextractionmodel(extraction_model)
            settings.updatecriteriamodel(criteria_model)
            st.success("Modelos de IA atualizados!")
        st.divider()

        # Banco de Critérios
        st.markdown("### Banco de Dados de Critérios")
        st.caption(
            "Abaixo está o conteúdo do arquivo src/criteria/criteriadatabase.json. "
            "Para editar, altere o arquivo diretamente e recarregue a aplicação."
        )
        try:
            import json
            with open("src/criteria/criteriadatabase.json", "r", encoding="utf-8") as f:
                criteriacontent = json.load(f)
            st.json(criteriacontent, expanded=False)
        except Exception as e:
            st.error(f"Não foi possível carregar o arquivo de critérios: {e}")
        st.divider()

        # Modo Debug
        st.markdown("### Modo de Depuração")
        debug_mode = st.checkbox(
            "Habilitar modo de depuração",
            value=settings.debugmode,
            help="Mostra logs mais detalhados no console para solução de problemas."
        )
        if debug_mode != settings.debugmode:
            settings.updatedebugmode(debug_mode)
            st.success(f"Modo de depuração {'ativado' if debug_mode else 'desativado'}.")
            st.experimental_rerun()

# Renderização principal
render_api_section()
st.divider()
render_defaults_section()
st.divider()
render_advanced_section()
