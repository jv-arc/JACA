# Métodos usados pela UI
Lista completa de todos os métodos de app.core que a UI utiliza para realizar suas tarefas

## Página de Projeto (page1)
- `load_project`: Usado para carregar o projeto para a sessão
- `create_project`: Usado para criar um novo projeto
- `list_projects`: Usado para listar projetos disponívies
- `remove_file`: Usado para remover um arquivo de uma determinada categoria no projeto atual
- `add_file`:Usado para adicionar um arquivo a uma determinada categoria no projeto atual

## Página de Extração (page2)

- `list_files_in_category`
- `run_extraction`
- `save_edited_text`
- `run_secondary_extraction`
- `get_director_list_from_content`
- `load_extracted_text`
- `list_files_in_category`
- `has_extraction_for_category`


## Página de Verificação (page3)
- `get_all_criteria`
- `load_project`
- `update_manual_override`
- `has_extracted_text`
- `execute_single_criterion_verification`
- `execute_criteria_verification`

## Página de Exportação (page4)
- `load_project`
- `get_all_criteria`
- `get_report_configuration`
- `upload_signed_document`
- `assemble_final_package`
- `delete_export_files`
- `get_draft_document_path`
- `get_signed_document_path`

## Página de Configuração (page5)
- `test_api_connection`
- `get_report_configuration`
- `save_report_configuration`
- `save_report_configuration`
- PÁGINA DE CONFIGURAÇÃO ESCREVENDO DIRETAMENETE EM SETTINGS!!!!
- `settings.api_key`
- `settings.update_key`
- `settings.extraction_model`
- `settings.criteria_model`
- `settings.update_extraction_model`
- `settings.update_crteria_model`
- `settings.debug_mode`


>Necessário:
> Mover chamadas de settings, para ControlFacade