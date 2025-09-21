import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================

st.set_page_config(page_title="Sobre o Projeto", page_icon="ℹ️", layout="wide")
st.title("ℹ️ Sobre o Assistente de Outorga")

st.markdown("---")

# ==============================================================================
# 2. SEÇÕES DE CONTEÚDO
# ==============================================================================

# --- Descrição do Projeto ---
st.subheader("🤖 O que é este projeto?")
st.markdown(
    """
    O **Assistente de Outorga para Rádios Comunitárias** é uma ferramenta de código aberto 
    projetada para simplificar e agilizar o complexo processo de obtenção de outorga 
    para rádios comunitárias no Brasil.

    Utilizando inteligência artificial (Google Gemini), a ferramenta automatiza tarefas como:
    - **Extração de dados** de documentos como estatutos e atas.
    - **Verificação de conformidade** desses documentos contra um conjunto de regras e critérios.
    - **Geração do formulário de requisição** final, pronto para ser protocolado.

    O objetivo é reduzir a carga burocrática e permitir que os membros da comunidade 
    foquem no que realmente importa: a comunicação e o serviço ao seu público.
    """
)

st.markdown("---")

# --- Licença ---
st.subheader("📜 Licença de Uso")
st.markdown(
    """
    Este projeto é distribuído sob a **Licença MIT**.

    Isso significa que você tem total liberdade para usar, copiar, modificar, distribuir 
    e até mesmo vender o software, desde que o aviso de direitos autorais e esta 
    permissão sejam incluídos em todas as cópias ou partes substanciais do software.
    """
)

st.markdown("---")

# --- Avisos e Disclaimers ---
st.subheader("⚠️ Avisos Importantes e Confiabilidade")
st.warning(
    """
    **A INTELIGÊNCIA ARTIFICIAL É UMA FERRAMENTA DE AUXÍLIO, NÃO UMA CONSULTORIA JURÍDICA.**
    """
)
st.markdown(
    """
    1.  **A IA não é infalível:** Modelos de linguagem podem, ocasionalmente, gerar informações incorretas, 
        interpretar textos de forma equivocada ou "alucinar" detalhes que não estão nos documentos.
    
    2.  **A Responsabilidade é Sua:** A responsabilidade final pela veracidade, precisão e completude
        das informações submetidas às autoridades é **inteiramente do usuário**. Este software é 
        fornecido "como está", sem garantias de qualquer tipo.

    3.  **REVISE TUDO CUIDADOSAMENTE:** Nós o incentivamos e recomendamos fortemente que você **revise 
        e valide cada informação gerada** por esta ferramenta antes de utilizá-la em seu 
        requerimento oficial. Use os dados gerados como um rascunho ou ponto de partida, 
        não como a versão final e definitiva.
    """
)

st.markdown("---")

# --- Contato do Desenvolvedor ---
st.subheader("🧑‍💻 Contato")
st.markdown(
    """
    Para dúvidas, sugestões, relatórios de bugs ou oportunidades de colaboração, 
    sinta-se à vontade para entrar em contato.

    - **E-mail:** `seu.email.profissional@exemplo.com`
    - **GitHub:** [github.com/seu-usuario](https://github.com/seu-usuario)

    *Feedback e contribuições para a melhoria do projeto são sempre bem-vindos!*
    """
)