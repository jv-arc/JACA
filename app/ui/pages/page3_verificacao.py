import streamlit as st
from typing import Dict, List
# ==============================================================================
# 1. INICIALIZAÇÃO E VERIFICAÇÃO DE ESTADO
# ==============================================================================

st.set_page_config(page_title="Verificação de Critérios", page_icon="✔️", layout="wide")
st.title("✔️ Verificação de Conformidade")

# Pega os serviços e o projeto da sessão
project_manager = st.session_state.get('project_manager')
current_project = st.session_state.get('current_project')
ui_logger = st.session_state.get('ui_logger')

if not all([project_manager, current_project, ui_logger]):
    st.error("⚠️ Nenhum projeto selecionado ou a sessão expirou.")
    st.info("Por favor, volte para a página `Home` e selecione ou crie um projeto para continuar.")
    st.stop()

st.info(f"**Projeto Aberto:** `{current_project}`")
st.caption("Execute a verificação de critérios com a IA. A IA analisará os textos extraídos contra um conjunto de regras pré-definidas para avaliar a conformidade dos documentos.")
st.divider()

# ==============================================================================
# 2. LÓGICA DE BACKEND
# ==============================================================================

def handle_run_all_checks():
    """Chama o backend para verificar todos os critérios pendentes."""
    ui_logger.info(f"Usuário iniciou a verificação de todos os critérios para '{current_project}'.")
    return project_manager.execute_criteria_verification(current_project)

def handle_run_single_check(criterion_id: str):
    """Chama o backend para verificar um único critério."""
    ui_logger.info(f"Usuário iniciou a verificação do critério '{criterion_id}' para '{current_project}'.")
    return project_manager.execute_single_criterion_verification(current_project, criterion_id)

def handle_manual_override(criterion_id: str, new_status: str, new_justification: str):
    """Chama o backend para aplicar uma correção manual."""
    ui_logger.info(f"Usuário aplicou override no critério '{criterion_id}' para o status '{new_status}'.")
    return project_manager.update_manual_override(current_project, criterion_id, new_status, new_justification)

def get_grouped_criteria(all_criteria: List[Dict]) -> Dict[str, List[Dict]]:
    """Agrupa critérios por fonte de documento para exibição em abas."""
    grouped = {}
    for c in all_criteria:
        docs = c.get('source_documents', [])
        group_key = "Consistência e Regras Gerais"
        if len(docs) == 1:
            group_key = f"Critérios do {docs[0].capitalize()}"
        
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(c)
    return grouped

# ==============================================================================
# 3. FUNÇÕES DE RENDERIZAÇÃO DA UI
# ==============================================================================

def render_criterion_status(result: Dict):
    """Renderiza o status (Conforme, Não Conforme, etc.) de um critério."""
    status_map = {
        "Conforme": ("success", "✅ Conforme"),
        "Não Conforme": ("error", "❌ Não Conforme"),
        "Inconclusivo": ("warning", "⚠️ Inconclusivo"),
    }
    default_style = ("error", f"🚨 Erro ({result.get('status', 'Desconhecido')})")
    
    style, text = status_map.get(result.get("status"), default_style)
    getattr(st, style)(text)
    
    justificativa = result.get('justificativa', 'Nenhuma justificativa fornecida.')
    st.caption("Justificativa da Análise:")
    st.markdown(f"> {justificativa.replace(chr(10), '<br>')}", unsafe_allow_html=True) # Mantém quebras de linha
    
    if result.get('overridden_at'):
        st.info("Este resultado foi alterado manualmente.")

def render_override_options(criterion: Dict, result: Dict):
    """Renderiza as opções avançadas para um critério (re-verificar, corrigir)."""
    with st.expander("Opções Avançadas"):
        # Re-verificar
        if st.button("🤖 Verificar Novamente com IA", key=f"recheck_{criterion['id']}", type="secondary"):
            with st.spinner(f"Re-verificando '{criterion['title']}'..."):
                handle_run_single_check(criterion['id'])
            st.rerun()
        
        st.markdown("---")
        
        # Override Manual
        st.markdown("**Correção Manual**")
        statuses = ["Conforme", "Não Conforme", "Inconclusivo"]
        current_status_index = statuses.index(result['status']) if result['status'] in statuses else 0
        
        new_status = st.selectbox("Alterar status para:", statuses, index=current_status_index, key=f"override_status_{criterion['id']}")
        new_just = st.text_area("Nova justificativa (obrigatório):", value=result['justificativa'], key=f"override_just_{criterion['id']}")
        
        if st.button("💾 Salvar Alteração Manual", key=f"save_override_{criterion['id']}", type="primary", disabled=not new_just):
            handle_manual_override(criterion['id'], new_status, new_just)
            st.toast("Alteração manual salva!")
            st.rerun()

def render_criterion_card(criterion: Dict, result: Optional[Dict]):
    """Renderiza um 'card' completo para um único critério."""
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(criterion['title'])
            st.caption(criterion['description'])

        with col2:
            is_ready = all(project_manager.has_extracted_text(current_project, doc) for doc in criterion['source_documents'])

            if not is_ready:
                st.warning(f"Aguardando extração de: {', '.join(criterion['source_documents'])}")
            elif result:
                render_criterion_status(result)
            else: # Pronto, mas pendente
                st.info("🔵 Pendente de Verificação")
                if st.button("Verificar Critério", key=f"check_{criterion['id']}", use_container_width=True):
                    with st.spinner(f"Verificando '{criterion['title']}'..."):
                        handle_run_single_check(criterion['id'])
                    st.rerun()

        if result and is_ready:
            render_override_options(criterion, result)

# ==============================================================================
# 4. RENDERIZAÇÃO PRINCIPAL DA PÁGINA
# ==============================================================================

# Carrega todos os dados necessários no início
all_criteria = project_manager.get_all_criteria()
project_data = project_manager.load_project(current_project)
results_map = {res['id']: res for res in project_data.criteria_results} if project_data.criteria_results else {}

# Botão principal para verificação em lote
pending_checks_count = len([c for c in all_criteria if c['id'] not in results_map])
if st.button(f"🤖 Verificar todos os {pending_checks_count} critérios pendentes", type="primary", disabled=pending_checks_count == 0):
    with st.spinner("Analisando documentos e aplicando critérios... Isso pode levar alguns minutos."):
        handle_run_all_checks()
    st.success("Verificação em lote concluída!")
    st.rerun()

st.divider()

# Agrupa e exibe os critérios em abas
grouped_criteria = get_grouped_criteria(all_criteria)
if not all_criteria:
    st.warning("Nenhum critério encontrado no banco de dados de critérios.")
else:
    # Ordena as abas para uma melhor visualização
    tab_names = sorted(grouped_criteria.keys())
    tabs = st.tabs(tab_names)

    for i, group_name in enumerate(tab_names):
        with tabs[i]:
            for criterion in grouped_criteria[group_name]:
                result = results_map.get(criterion['id'])
                render_criterion_card(criterion, result)