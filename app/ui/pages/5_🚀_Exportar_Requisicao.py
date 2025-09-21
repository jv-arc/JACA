import streamlit as st
import os

# ==============================================================================
# 1. INICIALIZAÇÃO E VERIFICAÇÃO DE ESTADO (sem alterações)
# ==============================================================================

st.set_page_config(page_title="Exportar Requisição", page_icon="🚀", layout="wide")
st.title("🚀 Exportar Pacote de Requisição")

project_manager = st.session_state.get('project_manager')
current_project = st.session_state.get('current_project')
ui_logger = st.session_state.get('ui_logger')

if not all([project_manager, current_project, ui_logger]):
    st.error("⚠️ Nenhum projeto selecionado ou a sessão expirou.")
    st.info("Por favor, volte para a página `Home` e selecione ou crie um projeto para continuar.")
    st.stop()

st.info(f"**Projeto Aberto:** `{current_project}`")
st.caption("Esta é a etapa final. Se todos os critérios de conformidade foram atendidos, você poderá gerar o pacote de documentos completo para a requisição de outorga.")
st.divider()

# ==============================================================================
# 2. FUNÇÕES DE RENDERIZAÇÃO DA UI (Reestruturadas)
# ==============================================================================

def render_download_screen(package_path: str):
    """Renderiza a tela para baixar ou apagar um pacote já existente."""
    st.success("✅ **Pacote de Requisição Pronto para Download!**")
    st.markdown("Um pacote de requisição já foi gerado para este projeto. Você pode baixá-lo diretamente ou, se necessário, apagá-lo para gerar um novo com informações atualizadas.")

    with open(package_path, "rb") as f:
        st.download_button(
            label="📥 Baixar Pacote de Requisição (.pdf)",
            data=f,
            file_name=os.path.basename(package_path),
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    
    st.divider()

    with st.expander("⚠️ Opções Avançadas"):
        st.warning("Atenção: A ação abaixo irá apagar permanentemente o arquivo gerado.")
        if st.button("Apagar para Gerar Novamente", use_container_width=True):
            ui_logger.info(f"Usuário solicitou a deleção do pacote existente para '{current_project}'.")
            if project_manager.delete_exported_package(current_project):
                st.toast("Arquivo apagado. Você já pode gerar um novo.")
                st.rerun()
            else:
                st.error("Ocorreu um erro ao apagar o arquivo.")

def render_generation_screen():
    """Renderiza a tela para gerar um novo pacote (código da versão anterior)."""
    # Verifica se o projeto está aprovado
    all_criteria = project_manager.get_all_criteria()
    project_data = project_manager.load_project(current_project)
    results = project_data.criteria_results if project_data else []
    results_map = {res['id']: res for res in results}
    
    failed_criteria = [res for res in results if res.get('status') != 'Conforme']
    pending_criteria = [c for c in all_criteria if c['id'] not in results_map]

    if failed_criteria or pending_criteria:
        st.error("🚫 **Projeto Ainda Não Aprovado para Exportação**")
        # (Opcional: adicionar a lógica de render_approval_blocker aqui)
        st.warning("Volte à página de 'Verificação de Critérios' e resolva todas as pendências.")
        st.stop()

    st.success("✅ **Projeto Aprovado!** Preencha os dados abaixo para gerar o pacote de requisição.")
    
    report_config = project_manager.get_report_configuration()
    user_overrides = {}

    with st.form("requisição_form"):
        # (Lógica do formulário, igual à versão anterior)
        st.subheader("📝 Preencha os Dados da Requisição")
        for table in report_config.get('tables', []):
            st.markdown(f"**{table['header']}**")
            for field in table.get('fields', []):
                if field.get('source') == 'user_input':
                    user_overrides[field['id']] = st.text_input(label=field['label'], value=field.get('default', ''))
            st.markdown("---")
        user_overrides['nome_tecnico_responsavel'] = st.text_input("Nome do Técnico Responsável")
        user_overrides['crea_tecnico'] = st.text_input("CREA/CFT do Técnico")
        
        submitted = st.form_submit_button("Gerar Pacote de Requisição", type="primary", use_container_width=True)
    
    if submitted:
        with st.spinner("Gerando formulário e unindo documentos..."):
            final_pdf_path = project_manager.export_project_package(current_project, user_overrides)
        
        if final_pdf_path:
            st.balloons()
            st.toast("Pacote gerado com sucesso!")
            st.rerun()
        else:
            st.error("Ocorreu um erro ao gerar o pacote.")

# ==============================================================================
# 3. LÓGICA PRINCIPAL DA PÁGINA (If/Else)
# ==============================================================================

# Verifica se o pacote de exportação já existe.
existing_package_path = project_manager.get_exported_package_path(current_project)

if existing_package_path:
    # Se existe, mostra a tela de download.
    render_download_screen(existing_package_path)
else:
    # Se não existe, mostra a tela de geração.
    render_generation_screen()