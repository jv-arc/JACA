import streamlit as st
import os


pm = st.session_state.get("project_manager")
project = st.session_state.get("project")


    def render_editing_interface(category_key: str, category_info: dict, files: list):
        """Renderiza a UI para quando os dados já foram extraídos."""
        
        # ... (código existente para carregar o texto e mostrar o st.expander com os arquivos) ...
        
        st.write("**Texto Consolidado (Revisável):**")
        
        edited_text = st.text_area(
            label="Revise o texto extraído pela IA...",
            value=project_manager.load_extracted_text(current_project, category_key),
            height=300, # Altura reduzida para dar espaço ao novo editor
            key=f"text_{category_key}"
        )
        
        # ... (código existente para os botões de Salvar e Re-extrair) ...
    
        # ===========================================================
        # NOVA SEÇÃO: EDITOR DE DIRIGENTES (SÓ APARECE PARA A 'ATA')
        # ===========================================================


if category_key == 'ata':
            st.divider()
            st.subheader("👥 Dirigentes Extraídos")
            st.caption("Verifique a lista extraída pela IA. Adicione, remova ou corrija nomes e cargos diretamente na tabela abaixo. As alterações aqui serão usadas no documento de exportação final.")
    
            project_data = project_manager.load_project(current_project)
            
            # Pega a lista de dirigentes dos content_fields da ata
            dirigentes_list = []
            if project_data.extracted_data.ata and project_data.extracted_data.ata.content_fields:
                dirigentes_list = project_data.extracted_data.ata.content_fields.get('lista_dirigentes_eleitos', [])
    
            # Garante que o dado seja uma lista de dicionários
            if not isinstance(dirigentes_list, list) or not all(isinstance(d, dict) for d in dirigentes_list):
                st.warning("O formato da lista de dirigentes extraída não é válido. A edição está desabilitada.")
                dirigentes_list = []
                
            edited_dirigentes = st.data_editor(
                dirigentes_list,
                num_rows="dynamic", # Permite ao usuário adicionar e apagar linhas
                column_config={
                    "nome": st.column_config.TextColumn("Nome Completo do Dirigente", required=True),
                    "cargo": st.column_config.TextColumn("Cargo", required=True),
                },
                key="dirigentes_editor",
                use_container_width=True
            )
    
            if st.button("Salvar Lista de Dirigentes", key="save_dirigentes_list"):
                if project_manager.update_director_list(current_project, edited_dirigentes):
                    st.toast("✅ Lista de dirigentes atualizada com sucesso!", icon="👥")
                else:
                    st.error("Ocorreu um erro ao salvar a lista de dirigentes.")
