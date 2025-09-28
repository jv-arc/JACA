# Resumo da Classe ProjectDataService

A classe **ProjectDataService** implementa métodos para acessar e utilizar arquivos de dados dentro dos projetos, especializando-se no gerenciamento de dados extraídos e estruturados .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **json** - Para manipulação de arquivos JSON
- **datetime** - Para timestamps e controle temporal
- **PathManager** - Gerenciamento de caminhos de arquivos de dados
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD dos projetos
- **ExtractedDataManager** - Gerenciamento de dados extraídos
- **GeminiClient** - Cliente para integração com IA Gemini

## Categorias de Dados

A classe trabalha com **5 categorias principais** de dados:
- estatuto, ata, identificacao, licenca, programacao

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa o serviço com cliente Gemini, logger, CRUD service e extraction manager
- **Dependências:** Logger, ProjectCRUDService, ExtractedDataManager

### Verificação de Dados Extraídos
**`has_extracted_text(project_name)`**
- Verifica se existe texto extraído em qualquer categoria do projeto
- **Retorna:** bool (True se há dados extraídos)
- **Dependências:** has_extraction_for_category

**`has_extraction_for_category(project_name, category)`**
- Verifica se categoria específica possui dados extraídos
- **Retorna:** bool (True se categoria tem dados)
- **Dependências:** PathManager.get_extracted_file_path, json.load

### Carregamento de Dados
**`load_structured_extraction(project_name, category)`**
- Carrega dados extraídos estruturados de uma categoria
- **Retorna:** Optional[Dict] (dados ou None)
- **Dependências:** PathManager.get_extracted_file_path, json.load

**`load_extracted_text(project_name, category)`**
- Carrega texto consolidado extraído de categoria específica
- **Retorna:** Optional[str] (texto ou None)
- **Dependências:** load_structured_extraction

**`get_consolidated_text(project_name)`**
- Obtém texto consolidado de todas as categorias
- **Retorna:** str (texto consolidado formatado)
- **Dependências:** load_extracted_text

### Salvamento de Dados
**`save_structured_extraction(project_name, category, data)`**
- Salva dados extraídos estruturados (**método incompleto**)
- **Retorna:** bool (sucesso/erro)
- **Dependências:** extraction_manager.consolidate_content_fields, extraction_manager.save_dict_to_file

**`save_edited_text(project_name, category, text)`**
- Salva texto consolidado editado pelo usuário
- **Retorna:** bool (sucesso/erro)
- **Dependências:** load_structured_extraction, PathManager.get_extracted_file_path, json.dump

### Atualização de Campos
**`update_extraction_field(project_name, category, field, value)`**
- Atualiza campo específico de extração
- **Retorna:** bool (sucesso/erro)
- **Dependências:** load_structured_extraction, PathManager.get_extracted_file_path, json.dump

**`mark_field_as_complete(project_name, category, field)`**
- Marca campo como completo definindo valor vazio
- **Retorna:** bool (sucesso/erro)
- **Dependências:** update_extraction_field

### Gerenciamento de Workflows
**`get_workflow_fields(category)`**
- Obtém campos de extração para uma categoria
- **Retorna:** List[str] (lista de campos)
- **Dependências:** extraction_manager.WORKFLOWS

### Análise de Pendências
**`get_pending_information(project_name)`**
- Identifica campos pendentes (com valor "NAO-ENCONTRADO")
- **Retorna:** Dict[str, List[str]] (categorias e campos pendentes)
- **Dependências:** crud_service.load_project
- **Token usado:** "NAO-ENCONTRADO"

### Gerenciamento de Diretores
**`update_director_list(project_name, directors)`**
- Atualiza lista de diretores na categoria 'ata'
- **Retorna:** bool (sucesso/erro)
- **Dependências:** crud_service.load_project, crud_service.save_project
- **Campo alvo:** lista_dirigentes_eleitos

**`get_director_list(project_name)`**
- Obtém lista atual de diretores
- **Retorna:** List[Dict] (lista de diretores)
- **Dependências:** crud_service.load_project
- **Campo fonte:** lista_dirigentes_eleitos

## Observações Importantes

- O método `save_structured_extraction` está **incompleto** no código fornecido
- A classe usa o token **"NAO-ENCONTRADO"** para identificar campos pendentes
- Trabalha exclusivamente com as 5 categorias predefinidas
- Mantém controle temporal com timestamps de criação e modificação