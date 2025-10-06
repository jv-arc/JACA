# Página de Projeto (ui/pages/page1_projeto.py)

## Descrição Básica
Página para expor opções iniciais básicas de projeto, isso inclui exibir uma página para carregar/criar projetos se nenhum estiver selecionado e uma para adicionar/editar/remover arquivos às categorias do projeto.


## Funcionamento Principal
Começa verificando se um projeto está selecionado usando `st.session_state.current_project`
### Caso Exista
Carrega nome do projeto e renderiza:
- Cabeçalho com instruções básicas, nome do projeto e botão para trocar de projeto.
- Carrega `ProjectData` usando `load_project(project_name)` do sistema
- Renderiza caixad para upload de arquivos nas categorias com `render_category_uploader`

### Caso não Exista
Renderiza:
- Container para criar projeto novo com `create_project(new_project_name)`(só muda o nome e recarrega a página, deixa o carregamento para quando `current_project` é identificado)
- Sessão para carregar projetos existentes com `list_projects()` caso não exista mostra um aviso

### Funções de Renderização
#### Abrir arquivo
`open_file_with_default_app(file_path: str)->None`
Abre o arquivo usando bibliotecas específicas, não depende do `app.core`
 
#### Lista de arquivos por Categoria com Botões
`display_files_for_category(category_key:str, files: List[str], project_name: str) -> None`
Faz uma lista reutilizável que lista todos os arquivos em uma categoria com botões para abrir com `open_file_with_default_app()` e para apagar com `remove_file()`do `app.core`


#### Renderizador do Container 
`render_category_uploader(category_config: Dict[str, Any], project_data: Any) ->`
Exibe a lista com botões usando `display_files_for_category` com tratamento caso nenhum arquivo esteja disponível, seguido por um `st.expander` para receber arquivos e um loop usando o `add_file()` de `app.core`


## Usos de `app.core`

### Carregamento dos Dados do Projeto
`load_project(project_name) -> ProjectData`: Usado para carregar o current_project da sessão para um dicionário project_data na página.


### Criar Projeto Novo
`create_project(new_project_name) -> bool`: Usado para criar um novo projeto, retorna apenas um bool, não precisa retornar um projeto ou carregar um projeto porque a página lida com isso ao criar um projeto novo.


### Listagem de Projetos
`list_projects() -> List`: Usado para listar projetos disponívies para serem carregados.

### Remoção de Arquivos dentro da Lista por categoria
`remove_file(project_name, file_path)->bool`: Usado para remover um arquivo de uma determinada categoria no projeto atual. É utilizado dentro de um botão na função de renderização da lista de arquivos por categoria, será que precisava receber a categoria por segurança?

### Adição de um novo arquivo dentro de uma categoria e de um projeto
`add_file(project_name, uploaded_file, category_key)->bool`:Usado para adicionar um arquivo a uma determinada categoria no projeto atual