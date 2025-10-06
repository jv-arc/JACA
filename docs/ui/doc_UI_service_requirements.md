# Métodos usados pela UI
Lista completa de todos os métodos de app.core que a UI utiliza para realizar suas tarefas

## Página de Projeto (page1)
**Carregamento dos Dados do Projeto**
`load_project(project_name) -> ProjectData`: Usado para carregar o current_project da sessão para um dicionário project_data na página.


**Criar Projeto Novo**
`create_project(new_project_name) -> bool`: Usado para criar um novo projeto, retorna apenas um bool, não precisa retornar um projeto ou carregar um projeto porque a página lida com isso ao criar um projeto novo.


**Listagem de Projetos**
`list_projects() -> List`: Usado para listar projetos disponívies para serem carregados.

**Remoção de Arquivos dentro da Lista por categoria**
`remove_file(project_name, file_path)->bool`: Usado para remover um arquivo de uma determinada categoria no projeto atual. É utilizado dentro de um botão na função de renderização da lista de arquivos por categoria, será que precisava receber a categoria por segurança?

**Adição de um novo arquivo dentro de uma categoria e de um projeto**
`add_file(project_name, uploaded_file, category_key)->bool`:Usado para adicionar um arquivo a uma determinada categoria no projeto atual


## Página de Extração (page2)

**Lista Arquivos em uma determinada categoria em um projeto**
`list_files_in_category(current_project, category_key)->List(str)` usado em dois lugares:
- obter lista de arquivos para extração e depois extrair com `run_extraction`

- 


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