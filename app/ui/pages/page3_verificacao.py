import streamlit as st
from typing import Dict, List, Any

# ==============================================================================
# 1. INICIALIZAÇÃO E VERIFICAÇÃO DE ESTADO
# ==============================================================================

st.set_page_config(page_title="Verificação de Critérios", page_icon="✔️", layout="wide")
st.title("✔️ Verificação de Conformidade dos Documentos")

# --- Carregamento dos Serviços e Verificação de Projeto ---
project_manager = st.session_state.get('project_manager')
current_project = st.session_state.get('current_project')
ui_logger = st.session_state.get('ui_logger')

if not all([project_manager, current_project, ui_logger]):
    st.error("⚠️ Nenhum projeto selecionado ou a sessão expirou.")
    st.info("Por favor, volte para a página `Home` e selecione ou crie um projeto para continuar.")
    st.stop()

st.info(f"**Projeto Aberto:** `{current_project}`")
st.caption("Nesta seção, a IA analisa os textos extraídos e os compara com os critérios legais e de boas práticas. Revise cada item e, se necessário, faça correções manuais.")
st.divider()

# --- Carrega todos os dados necessários para a página ---
all_criteria = project_manager.get_all_criteria()
project_data = project_manager.load_project(current_project)
results_map = {res['id']: res for res in project_data.criteria_results} if project_data and project_data.criteria_results else {}

# ==============================================================================
# 2. FUNÇÕES DE LÓGICA E RENDERIZAÇÃO DE COMPONENTES
# ==============================================================================

def get_grouped_criteria(criteria_list: List[Dict]) -> Dict[str, List[Dict]]:
    """Agrupa critérios por documento fonte para exibição em abas."""
    grouped = {}
    for c in criteria_list:
        docs = c.get('source_documents', [])
        # Define a chave do grupo
        group_key = "Consistência e Regras Gerais"
        if len(docs) == 1:
            group_key = f"Critérios do Documento: {docs[0].capitalize()}"
        
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(c)
    return grouped

def render_dashboard():
    """Exibe um painel de resumo no topo da página."""
    total_criteria = len(all_criteria)
    verified_count = len(results_map)
    conforme_count = len([res for res in results_map.values() if res.get('status') == 'Conforme'])
    
    st.subheader("Painel de Conformidade")
    cols = st.columns(3)
    cols[0].metric("Critérios Verificados", f"{verified_count}/{total_criteria}")
    cols[1].metric("Critérios 'Conforme'", f"{conforme_count}/{verified_count}")
    cols[2].metric("Progresso Geral", f"{int((verified_count/total_criteria)*100 if total_criteria > 0 else 0)}%")
    st.progress(verified_count / total_criteria if total_criteria > 0 else 0)

def render_criterion_status(result: Dict):
    """Exibe o status formatado de um critério verificado."""
    status = result.get("status", "Pendente")
    status_map = {
        "Conforme": ("success", "✅ Conforme"),
        "Não Conforme": ("error", "❌ Não Conforme"),
        "Inconclusivo": ("warning", "⚠️ Inconclusivo"),
    }
    style, text = status_map.get(status, ("error", f"🚨 Erro ({status})"))
    
    getattr(st, style)(text)
    st.caption("Justificativa da Análise:")
    st.markdown(f"> {result.get('justificativa', 'N/A')}")
    if result.get('overridden_at'):
        st.info("Este resultado foi alterado manualmente.")
    
    # Expansor para ver a análise completa da IA (Chain of Thought)
    if result.get('analise_completa'):
        with st.expander("Ver Raciocínio Completo da IA"):
            st.text(result['analise_completa'])

def render_override_options(criterion_id: str, current_result: Dict):
    """Renderiza as opções de correção manual para um critério."""
    st.markdown("**Correção Manual**")
    statuses = ["Conforme", "Não Conforme", "Inconclusivo"]
    try:
        current_status_index = statuses.index(current_result['status'])
    except ValueError:
        current_status_index = 0 # Padrão para 'Conforme'
    
    new_status = st.selectbox("Alterar status para:", statuses, index=current_status_index, key=f"override_status_{criterion_id}")
    new_just = st.text_area("Nova justificativa (obrigatório):", value=current_result['justificativa'], key=f"override_just_{criterion_id}")
    
    if st.button("Salvar Correção Manual", key=f"save_override_{criterion_id}", type="primary"):
        if not new_just.strip():
            st.error("A justificativa é obrigatória para uma correção manual.")
        else:
            if project_manager.update_manual_override(current_project, criterion_id, new_status, new_just):
                st.toast("Correção manual salva!")
                st.rerun()
            else:
                st.error("Falha ao salvar a correção.")

def render_criterion_card(criterion: Dict):
    """Renderiza um 'card' completo para um único critério."""
    criterion_id = criterion['id']
    result = results_map.get(criterion_id)

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(criterion['title'])
            st.caption(criterion['description'])

        with col2:
            is_ready = all(project_manager.has_extracted_text(current_project, doc) for doc in criterion['source_documents'])
            
            if not is_ready:
                st.warning(f"Aguardando extração de: **{', '.join(criterion['source_documents'])}**.")
            elif result:
                render_criterion_status(result)
            else:
                st.info("🔵 Pendente de Verificação")
                if st.button("Verificar Critério", key=f"check_{criterion_id}"):
                    with st.spinner(f"Verificando '{criterion['title']}'..."):
                        project_manager.execute_single_criterion_verification(current_project, criterion_id)
                    st.rerun()

        if result and is_ready:
            with st.expander("Opções Avançadas (Re-verificar ou Corrigir)"):
                if st.button("Verificar Novamente com IA", key=f"recheck_{criterion_id}", type="secondary"):
                     with st.spinner(f"Re-verificando '{criterion['title']}'..."):
                        project_manager.execute_single_criterion_verification(current_project, criterion_id)
                     st.rerun()
                st.divider()
                render_override_options(criterion_id, result)

# ==============================================================================
# 3. RENDERIZAÇÃO PRINCIPAL DA PÁGINA
# ==============================================================================

if not project_data:
    st.error("Falha ao carregar os dados do projeto. Tente selecionar o projeto novamente na Home.")
    st.stop()

render_dashboard()
st.divider()

pending_checks_count = len([c for c in all_criteria if c['id'] not in results_map])
if st.button(f"▶️ Verificar todos os {pending_checks_count} critérios pendentes", type="primary", disabled=pending_checks_count == 0):
    with st.spinner("Analisando documentos e aplicando todos os critérios... Isso pode levar alguns minutos."):
        project_manager.execute_criteria_verification(current_project)
    st.success("Verificação em lote concluída!")
    st.rerun()

st.divider()

grouped_criteria = get_grouped_criteria(all_criteria)
tab_names = sorted(grouped_criteria.keys())
tabs = st.tabs(tab_names)

for i, group_name in enumerate(tab_names):
    with tabs[i]:
        st.header(f"Critérios para: {group_name}")
        for criterion in grouped_criteria[group_name]:
            render_criterion_card(criterion)