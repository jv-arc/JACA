import streamlit as st
import os
from typing import Dict, List, Any

# 1. INICIALIZAÇÃO E VERIFICAÇÃO DE ESTADO
st.set_page_config(page_title="Exportar Requisição", page_icon="📤", layout="wide")
st.title("📤 Exportar Pacote de Requisição")

# --- Carregamento e Verificação Inicial ---
projectmanager = st.session_state.get("projectmanager")
currentproject = st.session_state.get("currentproject")

if not all([projectmanager, currentproject]):
    st.error("❌ Nenhum projeto selecionado. Volte para a Home e carregue ou crie um projeto para continuar.")
    st.stop()

st.info(f"📁 Projeto Aberto: {currentproject}")
st.caption("Esta é a etapa final. O processo foi dividido em etapas para garantir que todos os documentos sejam gerados, assinados e compilados corretamente.")
st.divider()

# --- Carrega todos os dados necessários uma única vez ---
allcriteria = projectmanager.getallcriteria()
projectdata = projectmanager.loadproject(currentproject)
results = projectdata.criteriaresults if projectdata else []
resultsmap = {res["id"]: res for res in results}

# 2. FUNÇÕES AUXILIARES E DE RENDERIZAÇÃO

def renderapprovalblock():
    """Exibe um bloco de erro quando o projeto não está pronto para exportar."""
    failed_criteria = [res for res in results if res.get("status") != "Conforme"]
    pending_criteria = [c for c in allcriteria if c["id"] not in resultsmap]
    
    st.error("❌ Projeto Não Aprovado para Exportação")
    st.warning("Para gerar o pacote de requisição, todos os critérios da fase anterior devem estar com o status 'Conforme'. Por favor, volte à página de Verificação de Critérios para resolver as pendências abaixo.")
    
    if failed_criteria:
        with st.expander("❌ Critérios com Falhas (Não Conforme ou Erro)", expanded=True):
            for item in failed_criteria:
                st.markdown(f"- {item['title']} | Status: {item['status']}")
    
    if pending_criteria:
        with st.expander("⏳ Critérios Pendentes de Verificação"):
            for item in pending_criteria:
                st.markdown(f"- {item['title']}")
    
    st.stop()

def getprefilledvalue(projectdataobj: Any, fieldconfig: Dict) -> Any:
    """Busca um valor pré-extrado dos dados do projeto."""
    defaultvalue = fieldconfig.get("default", "")
    datakey = fieldconfig.get("datakey")
    
    if not datakey or not projectdataobj or not projectdataobj.extracteddata:
        return defaultvalue
    
    try:
        category, fieldnamepath = datakey.split(".", 1)
        docdatadict = getattr(projectdata.extracteddata, category, None)
        
        if docdatadict and "contentfields" in docdatadict:
            finalkey = fieldnamepath.split(".")[-1]
            return docdatadict["contentfields"].get(finalkey, defaultvalue)
    except Exception:
        return defaultvalue
    
    return defaultvalue

def initializepersistentstate(projectdataobj: Any):
    """Inicializa as chaves de ESTADO PERSISTENTE, se não existirem."""
    if "forminitialized" in st.session_state:
        return
    
    reportconfig = projectmanager.getreportconfiguration()
    
    # Inicializa campos do formulário
    for table in reportconfig.get("tables", []):
        for field in table.get("fields", []):
            fieldkey = f"form{field['id']}"
            if fieldkey not in st.session_state:
                prefilled = getprefilledvalue(projectdataobj, field) if field.get("source") == "extracted" else field.get("default", "")
                st.session_state[fieldkey] = prefilled if prefilled else ""
    
    # Inicializa lista de dirigentes
    if "dirigenteseditor" not in st.session_state:
        initiallist = getprefilledvalue(projectdataobj, {"datakey": "ata.listadirigenteseleitos"}) or []
        st.session_state["dirigenteseditor"] = [dict(d) for d in initiallist] if isinstance(initiallist, list) else []
    
    # Inicializa campos extras
    if "formnometecnicoresponsavel" not in st.session_state:
        st.session_state["formnometecnicoresponsavel"] = ""
    if "formcreatecnico" not in st.session_state:
        st.session_state["formcreatecnico"] = ""
    
    st.session_state["forminitialized"] = True

def cleareditorstate():
    """Limpa todos os dados do formulário e do editor de dirigentes do sessionstate."""
    if "dirigenteseditor" in st.session_state:
        del st.session_state["dirigenteseditor"]
    
    for key in list(st.session_state.keys()):
        if key.startswith("form"):
            del st.session_state[key]

def renderdirectoreditor():
    """Renderiza a seção interativa para gerenciar a lista de dirigentes."""
    reportconfig = projectmanager.getreportconfiguration()
    st.markdown(f"**{reportconfig.get('dynamictables', [{}])[0].get('header')}**")
    
    for i, dirigente in enumerate(st.session_state["dirigenteseditor"]):
        with st.container(border=True):
            cols = st.columns([4, 4, 1])
            dirigente["nome"] = cols[0].text_input("Nome Completo", value=dirigente.get("nome", ""), key=f"dirnome{i}")
            dirigente["cargo"] = cols[1].text_input("Cargo", value=dirigente.get("cargo", ""), key=f"dircargo{i}")
            
            if cols[2].button("🗑️", key=f"removedir{i}", help="Remover Dirigente"):
                st.session_state["dirigenteseditor"].pop(i)
                st.rerun()
    
    if st.button("➕ Adicionar Dirigente", type="secondary"):
        st.session_state["dirigenteseditor"].append({"nome": "", "cargo": ""})
        st.rerun()

def renderdraftgenerationscreen(projectdataobj: Any):
    """Renderiza a tela para gerar o documento de rascunho (Etapa 1)."""
    st.subheader("📝 Etapa 1: Gerar Documento para Assinatura")
    
    initializepersistentstate(projectdataobj)
    
    reportconfig = projectmanager.getreportconfiguration()
    
    # Renderiza campos do formulário
    for table in reportconfig.get("tables", []):
        st.markdown(f"**{table['header']}**")
        for field in table.get("fields", []):
            st.text_input(label=f"{field['label']}", key=f"form{field['id']}")
    
    st.divider()
    
    # Editor de dirigentes
    renderdirectoreditor()
    
    st.divider()
    
    # Campos extras
    st.markdown("**Outras Informações para o Documento**")
    st.text_input("Nome do Técnico Responsável", key="formnometecnicoresponsavel")
    st.text_input("CREA/CFT do Técnico", key="formcreatecnico")
    
    st.divider()
    
    if st.button("🚀 Gerar Documento para Assinatura", type="primary", use_container_width=True):
        # Coleta dados do formulário
        useroverrides = {key.replace("form", ""): st.session_state[key] for key in st.session_state if key.startswith("form") and key != "forminitialized"}
        useroverrides["listadirigentesfinal"] = st.session_state["dirigenteseditor"]
        
        # Validação obrigatória
        if not useroverrides.get("enderecoirradiante"):
            st.error("❌ O campo 'Endereço de Instalação do Sistema Irradiante' é obrigatório.")
        else:
            with st.spinner("Gerando documento..."):
                draftpath = projectmanager.generatedraftforsignature(currentproject, useroverrides)
                
                if draftpath:
                    st.success("✅ Documento gerado com sucesso!")
                    cleareditorstate()
                    st.rerun()
                else:
                    st.error("❌ Falha ao gerar o documento.")

def renderuploadsignedscreen(draftpath: str):
    """Renderiza a tela para upload do documento assinado (Etapa 2)."""
    st.subheader("✍️ Etapa 2: Obter Assinaturas e Fazer Upload")
    
    st.success("✅ O documento de requisição foi gerado.")
    st.markdown("**Ação necessária:** Baixe o documento abaixo, obtenha todas as assinaturas necessárias e digitalize-o novamente como um único arquivo PDF.")
    
    with open(draftpath, "rb") as f:
        st.download_button("📥 Baixar Documento para Assinatura (.pdf)", f, os.path.basename(draftpath), use_container_width=True)
    
    st.divider()
    
    uploadedfile = st.file_uploader("📤 Faça o upload do documento assinado aqui", type="pdf")
    
    if st.button("📨 Enviar Documento Assinado", disabled=not uploadedfile, type="primary", use_container_width=True):
        if projectmanager.uploadsigneddocument(currentproject, uploadedfile):
            st.toast("✅ Documento assinado salvo!")
            st.rerun()
        else:
            st.error("❌ Falha ao salvar o documento.")

def renderfinalassemblyscreen():
    """Renderiza a tela para montar o pacote final (Etapa 3)."""
    st.subheader("📦 Etapa 3: Montar Pacote Final")
    
    st.success("✅ Tudo pronto! O documento assinado foi recebido.")
    st.markdown("Clique no botão abaixo para unir o requerimento assinado com todos os outros documentos do projeto (estatuto, atas, etc.) em um único arquivo PDF, pronto para ser protocolado.")
    
    if st.button("🔗 Montar Pacote Completo", type="primary", use_container_width=True):
        with st.spinner("Unindo todos os documentos... Isso pode levar um momento."):
            finalpackagepath = projectmanager.assemblefinalpackage(currentproject)
            
            if finalpackagepath:
                st.session_state["finalpackagepath"] = finalpackagepath
                st.rerun()
            else:
                st.error("❌ Ocorreu um erro ao montar o pacote final.")

def renderfinaldownloadscreen():
    """Renderiza a tela final para baixar o pacote completo."""
    st.balloons()
    st.header("🎉 Pacote de Requisição Finalizado!")
    
    st.markdown("Seu dossiê completo está pronto para download.")
    
    finalpath = st.session_state["finalpackagepath"]
    with open(finalpath, "rb") as f:
        st.download_button("📥 Baixar Pacote Final Completo (.pdf)", f, os.path.basename(finalpath), "application/pdf", use_container_width=True, type="primary")
    
    st.divider()
    
    if st.button("🔄 Resetar e Gerar Novo Pacote"):
        projectmanager.deleteexportfiles(currentproject)
        del st.session_state["finalpackagepath"]
        cleareditorstate()
        st.rerun()

# 3. LÓGICA PRINCIPAL - MÁQUINA DE ESTADOS

if not projectdata:
    st.error("❌ Falha ao carregar os dados do projeto.")
    st.stop()

# Verifica se o projeto está aprovado para exportação
isapproved = not [res for res in results if res.get("status") != "Conforme"] and not [c for c in allcriteria if c["id"] not in resultsmap]

if not isapproved and not projectmanager.getdraftdocumentpath(currentproject):
    renderapprovalblock()

# Determina o estado atual do fluxo de exportação
draftpath = projectmanager.getdraftdocumentpath(currentproject)
signedpath = projectmanager.getsigneddocumentpath(currentproject)
finalpackagepath = st.session_state.get("finalpackagepath")

# Renderiza a tela correta com base no estado
if finalpackagepath and os.path.exists(finalpackagepath):
    renderfinaldownloadscreen()
elif not draftpath:
    renderdraftgenerationscreen(projectdata)
elif not signedpath:
    renderuploadsignedscreen(draftpath)
else:
    renderfinalassemblyscreen()