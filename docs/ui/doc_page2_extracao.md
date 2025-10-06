# Página de Extração (ui/pages/page2_extracao.py)
## Descrição Básica
Página para extrair os dados dos arquivos em cada categoria, A extração ocorre primariamente para extrair dados do texto, o usuário pode corrigir o texto extraído e posteriormente uma extração secundária ocorre para extrair os campos chave que ocorre escondida do usuário.

Apesar de parecer confuso do ponto de vista de implementação, esse workflow foi escolhido para transmitir a sensação de controle para o usuário, mas sem complicar o uso da aplicação.


## Funcionamento
### Caso haja problemas:
Se não houverem projetos ou instancia para acessa-los redireciona o usuário para página `page1_projetos.py`Caso não haja exibe mensagens de erro

### Caso tudo dê certo:
Renderiza um cabeçalho simples informando o projeto aberto e instuições simples

Usa um loop para renderizar páginas de carregamento de arquivos com a função `render_category_section()`

## Funções Auxiliares
> NOTA: Essa página tem funções auxiliares que deveriam ser movidas para `app.core`

### Lidar com a Extração
> PRECISA REFATORAR

`handle_extraction(category_key:str)->Dict`

Usa `list_files_in_category()` de `app.core` para obter lista de arquivos na categoria e `run_extraction` também de `app.core`, a execução da lógica na UI é um erro de arquitetura

### Extração e Salvamento dos Campos
> Talvez refatorar???

`handle_save_and_extract_fields(category_key: str, edited_text: str) -> bool`

Função para renderizar spinner e toast além de rodar o salvamento do texto editado com `save_edited_text` e `run_secondary_extraction` ambos de `app.core`, uma simplificação poderia ser feita para importar apenas um método aqui.

### Renderiza Página Interia quando não tem dados de extração
`render_extraction_interface(category_key: str, category_info: Dict, files: List)->None`

É oque aparece para uma determinada categoria se não tiver extrações feitas, mas tiver arquivos disponíveis. Renderiza:
- lista de arquivos disponíveis
- botão para extração
Usa a função auxiliar `handle_extraction()`

### Renderiza Seção para controlar a lista de dirigentes
`render_director_editor()`

Se não tiver dirigentes na página usa `get_diretor_list_from_content()` para colocar em `st.session_state`

Renderiza em um loop com um container por fim um, botão para adicionar dirigentes.

### Renderiza UI para dados já extraidos
`render_editing_interface(category_key, category_info, files)`

- obtém os dados extraídos com `load_extracted_text()` e trata se não existirem
- exibe "fontes" dos dados extraídos com lista
- exibe campo para edição
SE O CAMPO FOR DA ATA:
- exibe botão para atualizar compos com `handle_save_and_extract_fields`
- Exibe botão para reextração usando `handle_extraction`

### Renderiza uma secção completa para categoria
> Refatoração? Precisamos mesmo listar os arquivos só para verificar se existem

`render_category_section(category_key: str, category_info: Dict)`

1. Imprime cabeçalho
2. Usa `list_files_in_category` para verificar se o projeto tem arquivos
3. Usa `has_extraction_for_category` para verficação de existencia de dados
4. (A) Usa `render_editing_interface` para editar dados extraídos
4. (B) Usa `render_extraction_interface` para renderizar extração dos dados


## Dependência de `app.core`

### Lista Arquivos em uma determinada categoria em um projeto
`list_files_in_category(current_project, category_key)->List(str)`

usado em dois lugares:
- obter lista de arquivos para extração e depois extrair com `run_extraction`
- verifica se o projeto tem arquivos em `render_category_section`

## Rodar Extração
- `run_extraction`
- `save_edited_text`
- `run_secondary_extraction`
- `get_director_list_from_content`
- `load_extracted_text`
- `list_files_in_category`
- `has_extraction_for_category`