import streamlit as st
from src.project_manager import ProjectManager

# Página de Verificação de Critérios

# Carrega o ProjectManager da sessão
project_manager = st.session_state.get('projectmanager', None)
current_project = st.session_state.get('currentproject', None)

# Verifica se há projeto aberto
if not project_manager or not current_project:
    st.error("Nenhum projeto selecionado. Volte à Home e carregue ou crie um projeto para continuar.")
    st.stop()

st.info(f"Projeto Aberto: {current_project}")
st.caption("Esta é a etapa de Verificação de Critérios. Revise e aplique cada verificação antes de prosseguir.")
st.divider()

# Carrega todas as regras de verificação
all_criteria = project_manager.get_all_criteria()
project_data = project_manager.load_project(current_project)

# Mapeia resultados existentes
results_map = {}
if project_data and project_data.criteriaresults:
    for res in project_data.criteriaresults:
        results_map[res['id']] = res

# Botão para verificação em lote
pending = [c for c in all_criteria if c['id'] not in results_map]
pending_count = len(pending)
if st.button(f"Verificar todos os {pending_count} critérios pendentes", type='primary', disabled=(pending_count==0)):
    with st.spinner("Analisando documentos e aplicando critérios... Isso pode levar alguns minutos."):
        project_manager.execute_criteria_verification(current_project)
    st.success("Verificação em lote concluída!")
    st.experimental_rerun()

st.divider()

# Agrupa critérios por categoria em abas
grouped = {}
for c in all_criteria:
    cat = c['category']
    grouped.setdefault(cat, []).append(c)

tabs = st.tabs(sorted(grouped.keys()))
for tab, category in zip(tabs, sorted(grouped.keys())):
    with tab:
        st.subheader(category.capitalize())
        for criterion in grouped[category]:
            cid = criterion['id']
            title = criterion['title']
            desc = criterion.get('description', '')
            sourcedocs = criterion.get('sourcedocuments', [])
            result = results_map.get(cid, None)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(title)
                st.caption(desc)
            with col2:
                # Checa se textos estão prontos
                ready = all(project_manager.has_extracted_text(current_project, d) for d in sourcedocs)
                if not ready:
                    missing = [d for d in sourcedocs if not project_manager.has_extracted_text(current_project, d)]
                    st.warning(f"Aguardando extração de: {', '.join(missing)}")
                elif result:
                    # Exibe status existente
                    status = result['status']
                    justify = result.get('justificativa', '')
                    if status == 'Conforme':
                        st.success(f"Conforme: {justify}")
                    elif status == 'Não Conforme':
                        st.error(f"Não Conforme: {justify}")
                    else:
                        st.info(f"Indeterminado: {justify}")
                else:
                    st.info("Pendente de Verificação")

            # Botão de verificação individual
            if ready:
                if st.button(f"Verificar Critério", key=f"check_{cid}", use_container_width=True):
                    with st.spinner(f"Verificando {title}..."):
                        project_manager.run_single_check(current_project, cid)
                    st.experimental_rerun()

            # Override de resultado
            if result and ready:
                with st.expander("Sobrepor Decisão"):  
                    new_status = st.selectbox("Status", ["Conforme", "Não Conforme", "Indeterminado"], index=["Conforme", "Não Conforme", "Indeterminado"].index(result['status']), key=f"override_{cid}")
                    new_just = st.text_area("Justificativa", result.get('justificativa', ''), key=f"just_{cid}")
                    if st.button("Aplicar Override", key=f"apply_{cid}"):
                        project_manager.override_criteria_result(current_project, cid, new_status, new_just)
                        st.success("Decisão atualizada")
                        st.experimental_rerun()


def rendercriterionstatusresult(result):
    """Renderiza o status do critério com cores apropriadas"""
    status = result['status']
    if status == 'Conforme':
        st.success(f"Conforme: {result.get('justificativa', '')}")
    elif status == 'Não Conforme':
        st.error(f"Não Conforme: {result.get('justificativa', '')}")
    else:
        st.info(f"Indeterminado: {result.get('justificativa', '')}")

def renderoverrideoptionscriterion(criterion, result):
    """Renderiza opções de override para um critério"""
    if result:
        with st.expander("Sobrepor Decisão"):  
            new_status = st.selectbox(
                "Status", 
                ["Conforme", "Não Conforme", "Indeterminado"], 
                index=["Conforme", "Não Conforme", "Indeterminado"].index(result['status']),
                key=f"override_{criterion['id']}"
            )
            new_just = st.text_area(
                "Justificativa", 
                result.get('justificativa', ''),
                key=f"just_{criterion['id']}"
            )
            if st.button("Aplicar Override", key=f"apply_{criterion['id']}"):
                project_manager.override_criteria_result(current_project, criterion['id'], new_status, new_just)
                st.success("Decisão atualizada")
                st.rerun()


def handlerunallchecks():
    """Handler para verificação em lote"""
    project_manager.execute_criteria_verification(current_project)

def handlerunsinglecheckcriterionid(criterion_id):
    """Handler para verificação individual"""
    project_manager.run_single_check(current_project, criterion_id)

def getgroupedcriteria(all_criteria):
    """Agrupa critérios por categoria"""
    grouped = {}
    for c in all_criteria:
        cat = c['category']
        grouped.setdefault(cat, []).append(c)
    return grouped


def rendercriterioncardcriterion(criterion, result):
    """Renderiza um card completo para um critério"""
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(criterion['title'])
            st.caption(criterion['description'])
        
        with col2:
            # Verifica se textos estão prontos
            is_ready = all(
                project_manager.has_extracted_text(current_project, doc) 
                for doc in criterion['sourcedocuments']
            )
            
            if not is_ready:
                st.warning(f"Aguardando extração de: {', '.join(criterion['sourcedocuments'])}")
            elif result:
                rendercriterionstatusresult(result)
            else:
                st.info("Pendente de Verificação")
        
        # Botão de verificação
        if is_ready and st.button(f"Verificar Critério", key=f"check_{criterion['id']}", use_container_width=True):
            with st.spinner(f"Verificando {criterion['title']}..."):
                handlerunsinglecheckcriterionid(criterion['id'])
            st.rerun()
            
        # Opções de override
        if result and is_ready:
            renderoverrideoptionscriterion(criterion, result)

# Agrupa e exibe os critérios em abas
grouped_criteria = getgroupedcriteria(all_criteria)
if grouped_criteria:
    tab_names = sorted(grouped_criteria.keys())
    tabs = st.tabs(tab_names)
    
    for i, group_name in enumerate(tab_names):
        with tabs[i]:
            for criterion in grouped_criteria[group_name]:
                result = results_map.get(criterion['id'])
                rendercriterioncardcriterion(criterion, result)
