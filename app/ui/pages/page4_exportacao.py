import streamlit as st
import os
from typing import Dict, List, Any

# ==============================================================================
# 1. INICIALIZAÇÃO E VERIFICAÇÃO DE ESTADO
# ==============================================================================

st.set_page_config(page_title="Exportar Requisição", page_icon="🚀", layout="wide")
st.title("🚀 Exportar Pacote de Requisição")

# --- Carregamento dos Serviços e Verificação de Projeto ---
project_manager = st.session_state.get('project_manager')
current_project = st.session_state.get('current_project')

if not all([project_manager, current_project]):
    st.error("⚠️ Nenhum projeto selecionado. Volte para a Home e carregue ou crie um projeto para continuar.")
    st.stop()

st.info(f"**Projeto Aberto:** `{current_project}`")
st.caption("Esta é a etapa final. O processo foi dividido em etapas para garantir que todos os documentos sejam gerados, assinados e compilados corretamente.")
st.divider()

# --- Carrega os dados necessários para a página uma única vez ---
project_data = project_manager.load_project(current_project)
all_criteria = project_manager.get_all_criteria()
results = project_data.criteria_results if project_data else []
results_map = {res['id']: res for res in results}

# ==============================================================================
# 2. FUNÇÕES DE LÓGICA E RENDERIZAÇÃO
# ==============================================================================

#--------------------------------------------------------------------
# Busca um valor pré-extraído dos dados do projeto ou o valor padrão.
#--------------------------------------------------------------------
def get_prefilled_value(project_data_obj: Any, field_config: Dict) -> Any:
    default_value = field_config.get('default', '')
    data_key = field_config.get('data_key')
    if not data_key or not project_data_obj or not project_data_obj.extracted_data:
        return default_value
    try:
        category, field_name_path = data_key.split('.', 1)
        doc_data_dict = getattr(project_data_obj.extracted_data, category, None)
        if doc_data_dict and 'content_fields' in doc_data_dict and doc_data_dict['content_fields']:
            final_key = field_name_path.split('.')[-1]
            extracted_value = doc_data_dict['content_fields'].get(final_key)
            return extracted_value if extracted_value is not None else default_value
    except Exception:
        return default_value
    return default_value

#-------------------------------------------------------------------
# Inicializa cada campo no session_state APENAS SE ele não existir.
#-------------------------------------------------------------------
def initialize_state(project_data_obj: Any):
    if 'export_form_initialized' in st.session_state:
        return

    report_config = project_manager.get_report_configuration()
    
    # Inicializa campos estáticos
    for table in report_config.get('tables', []):
        for field in table.get('fields', []):
            p_key = f"form_{field['id']}"
            if p_key not in st.session_state:
                prefilled = get_prefilled_value(project_data_obj, field) if field.get('source') == 'extracted' else field.get('default', '')
                st.session_state[p_key] = prefilled if prefilled else ''
    
    # Inicializa a lista de dirigentes
    if 'dirigentes_editor' not in st.session_state:
        initial_list = get_prefilled_value(project_data_obj, {'data_key': 'ata.lista_dirigentes_eleitos'}) or []
        st.session_state.dirigentes_editor = [dict(d) for d in initial_list] if isinstance(initial_list, list) else []

    # Inicializa campos extra
    if "form_nome_tecnico_responsavel" not in st.session_state:
        st.session_state.form_nome_tecnico_responsavel = ""
    if "form_crea_tecnico" not in st.session_state:
        st.session_state.form_crea_tecnico = ""
    
    st.session_state['export_form_initialized'] = True


#---------------------------------------------------------------
# Limpa todas as chaves de estado do formulário da sessão.
#---------------------------------------------------------------
def clear_state():
    keys_to_delete = ['dirigentes_editor', 'export_form_initialized']
    for key in list(st.session_state.keys()):
        if key.startswith("form_") or key.startswith("_form_") or key.startswith("dir_"):
            keys_to_delete.append(key)
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]



#------------------------------------------------------------------------------
# Renderiza a seção interativa e modular para gerenciar a lista de dirigentes.
#------------------------------------------------------------------------------
def render_director_editor():
    report_config = project_manager.get_report_configuration()
    st.markdown(f"**{report_config.get('dynamic_tables', [{}])[0].get('header')}**")
    
    for i in range(len(st.session_state.dirigentes_editor)):
        if i >= len(st.session_state.dirigentes_editor): break
        dirigente = st.session_state.dirigentes_editor[i]
        with st.container(border=True):
            cols = st.columns([4, 4, 1])
            dirigente['nome'] = cols[0].text_input("Nome Completo", value=dirigente.get('nome', ''), key=f"dir_nome_{i}")
            dirigente['cargo'] = cols[1].text_input("Cargo", value=dirigente.get('cargo', ''), key=f"dir_cargo_{i}")
            if cols[2].button("🗑️", key=f"remove_dir_{i}", help="Remover Dirigente"):
                st.session_state.dirigentes_editor.pop(i)
                st.rerun()

    if st.button("➕ Adicionar Dirigente", type="secondary"):
        st.session_state.dirigentes_editor.append({'nome': '', 'cargo': ''})
        st.rerun()



#----------------------------------------------------------------------
# Renderiza a Etapa 1: o formulário para gerar o documento de rascunho.
#----------------------------------------------------------------------
def render_draft_generation_screen():
    st.subheader("Etapa 1: Gerar Documento para Assinatura")
    st.markdown("Revise e preencha os campos abaixo. Suas alterações são salvas automaticamente. Quando tudo estiver pronto, clique no botão 'Gerar Documento' no final da página.")
    st.divider()
    
    initialize_state(project_data)
    report_config = project_manager.get_report_configuration()

    for table in report_config.get('tables', []):
        st.markdown(f"**{table['header']}**")
        for field in table.get('fields', []):
            st.text_input(label=field['label'], key=f"form_{field['id']}")
        st.divider()
    
    render_director_editor()
    st.divider()
    
    st.markdown("**Outras Informações para o Documento**")
    st.text_input("Nome do Técnico Responsável", key="form_nome_tecnico_responsavel")
    st.text_input("CREA/CFT do Técnico", key="form_crea_tecnico")
    st.divider()

    if st.button("Gerar Documento para Assinatura", type="primary", use_container_width=True):
        user_overrides = {key.replace("form_", ""): st.session_state[key] for key in st.session_state if key.startswith("form_")}
        user_overrides['lista_dirigentes_final'] = st.session_state.dirigentes_editor

        if not user_overrides.get('endereco_irradiante'):
            st.error("O campo 'Endereço de Instalação do Sistema Irradiante' é obrigatório.")
        else:
            with st.spinner("Gerando documento..."):
                draft_path = project_manager.generate_draft_for_signature(current_project, user_overrides)
            if draft_path:
                st.success("Documento gerado com sucesso!")
                clear_state()
                st.rerun()
            else:
                st.error("Falha ao gerar o documento.")


#-------------------------------------------------------------------------
# Exibe um bloco de erro quando o projeto não está pronto para exportar.
#-------------------------------------------------------------------------
def render_approval_blocker():
    failed_criteria = [res for res in results if res.get('status') != 'Conforme']
    pending_criteria = [c for c in all_criteria if c['id'] not in results_map]
    st.error("🚫 **Projeto Não Aprovado para Exportação**")
    st.warning("Para gerar o pacote de requisição, todos os critérios da fase anterior devem estar com o status '✅ Conforme'. Volte à página de **Verificação de Critérios** para resolver as pendências abaixo.")
    if failed_criteria:
        with st.expander("Critérios com Falhas ('Não Conforme' ou 'Erro')", expanded=True):
            for item in failed_criteria: st.markdown(f"- **{item['title']}** (Status: {item['status']})")
    if pending_criteria:
        with st.expander("Critérios Pendentes de Verificação"):
            for item in pending_criteria: st.markdown(f"- **{item['title']}**")
    st.stop()





#----------------------------------------------------
# Renderiza a Etapa 2: upload do documento assinado.
#----------------------------------------------------
def render_upload_signed_screen(draft_path: str):
    st.subheader("Etapa 2: Obter Assinaturas e Fazer Upload")
    st.success("O documento de requisição foi gerado.")
    st.markdown("**Ação necessária:** Baixe o documento abaixo, obtenha todas as assinaturas e digitalize-o como um PDF.")
    with open(draft_path, "rb") as f:
        st.download_button("📥 Baixar Documento para Assinatura (.pdf)", f, os.path.basename(draft_path), use_container_width=True)
    st.divider()
    uploaded_file = st.file_uploader("**Faça o upload do documento assinado aqui:**", type="pdf")
    if st.button("Enviar Documento Assinado", disabled=not uploaded_file, type="primary", use_container_width=True):
        if project_manager.upload_signed_document(current_project, uploaded_file):
            st.toast("Documento assinado salvo!")
            st.rerun()
        else:
            st.error("Falha ao salvar o documento.")




#----------------------------------------------
# Renderiza a Etapa 3: montar o pacote final.
#----------------------------------------------
def render_final_assembly_screen():
    st.subheader("Etapa 3: Montar Pacote Final")
    st.success("✅ Tudo pronto! O documento assinado foi recebido.")
    st.markdown("Clique no botão abaixo para unir o requerimento assinado com todos os outros documentos do projeto (estatuto, atas, etc.) em um único arquivo PDF.")
    if st.button("Montar Pacote Completo", type="primary", use_container_width=True):
        with st.spinner("Unindo todos os documentos..."):
            final_package_path = project_manager.assemble_final_package(current_project)
        if final_package_path:
            st.session_state['final_package_path'] = final_package_path
            st.rerun()
        else:
            st.error("Ocorreu um erro ao montar o pacote final.")


#------------------------------------------------------
# Renderiza a tela final para baixar o pacote completo.
#------------------------------------------------------
def render_final_download_screen():
    st.balloons()
    st.header("🎉 Pacote de Requisição Finalizado!")
    st.markdown("Seu dossiê completo está pronto para download.")
    final_path = st.session_state['final_package_path']
    with open(final_path, "rb") as f:
        st.download_button("📥 Baixar Pacote Final Completo (.pdf)", f, os.path.basename(final_path), "application/pdf", use_container_width=True, type="primary")
    st.divider()
    if st.button("Resetar e Gerar Novo Pacote"):
        project_manager.delete_export_files(current_project)
        del st.session_state['final_package_path']
        clear_state()
        st.rerun()

# ==============================================================================
# 3. LÓGICA PRINCIPAL DA PÁGINA (A MÁQUINA DE ESTADOS)
# ==============================================================================

if not project_data:
    st.error("Falha ao carregar os dados do projeto. Tente recarregar a página.")
    st.stop()
    
is_approved = not [res for res in results if res.get('status') != 'Conforme'] and not [c for c in all_criteria if c['id'] not in results_map]
draft_path = project_manager.get_draft_document_path(current_project)

if not is_approved and not draft_path:
    render_approval_blocker()
else:
    signed_path = project_manager.get_signed_document_path(current_project)
    final_package_path = st.session_state.get('final_package_path')

    if final_package_path and os.path.exists(final_package_path):
        render_final_download_screen()
    elif not draft_path:
        render_draft_generation_screen()
    elif not signed_path:
        render_upload_signed_screen(draft_path)
    else:
        render_final_assembly_screen()