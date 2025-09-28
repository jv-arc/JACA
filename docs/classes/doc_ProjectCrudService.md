# Resumo da Classe ProjectCRUDService

A classe **ProjectCRUDService** implementa métodos para operações de CRUD (Create, Read, Update, Delete) com os projetos, incluindo carregar, salvar, deletar e listagem de projetos .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **json** - Para manipulação de arquivos JSON
- **shutil** - Para operações de remoção de diretórios  
- **datetime** - Para timestamps de criação/modificação
- **pathlib.Path** - Para manipulação de caminhos
- **ProjectState, ExtractedDataType** - Modelos de dados do projeto
- **PathManager** - Gerenciamento centralizado de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o serviço CRUD e cria diretório de projetos se necessário
- **Dependências:** Logger, PathManager.get_project_dir

### Operações CRUD Principais

#### Create (Criação)
**`create_project(project_name)`**
- Cria novo projeto com estrutura completa de diretórios e metadados
- Cria 5 categorias padrão: estatuto, ata, identificacao, licenca, programacao
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager (validação, caminhos, subdiretórios), ProjectState, ExtractedDataType, datetime.now

#### Read (Leitura)
**`load_project(project_name)`**
- Carrega projeto completo incluindo metadados, dados extraídos e critérios
- **Retorna:** Optional[ProjectState] (projeto ou None)
- **Dependências:** PathManager (caminhos JSON), ProjectState.load_from_file, json.load

**`get_project_metadata(project_name)`**
- Obtém apenas metadados básicos sem carregar dados extraídos
- **Retorna:** Optional[Dict] (metadados ou None)
- **Dependências:** PathManager.get_project_json_path, json.load

#### Update (Atualização)
**`save_project(project)`**
- Salva projeto separando metadados, dados extraídos por categoria e critérios
- Atualiza timestamp automaticamente
- **Retorna:** bool (sucesso/erro)  
- **Dependências:** PathManager (caminhos), ProjectState.save_to_file, json.dump, datetime.now

#### Delete (Exclusão)
**`delete_project(project_name)`**
- Remove projeto e toda estrutura de arquivos do disco
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_project_path, shutil.rmtree

### Operações Utilitárias

**`list_projects()`**
- Lista todos os projetos válidos verificando presença de project.json
- **Retorna:** List[str] (nomes dos projetos)
- **Dependências:** PathManager.get_project_dir, PathManager.extract_project_name_from_path

**`project_exists(project_name)`** 
- Verifica existência e estrutura válida do projeto
- **Retorna:** bool (existe/não existe)
- **Dependências:** PathManager.is_valid_project_structure

**`validate_project_structure(project_name)`**
- Valida e corrige estrutura criando subdiretórios ausentes
- **Retorna:** bool (válido/erro)
- **Dependências:** self.project_exists, PathManager.get_all_project_subdirs

## Características Importantes

### Separação de Dados
- **Metadados:** Salvos em `project.json` principal
- **Dados Extraídos:** Salvos em arquivos JSON separados por categoria (`{categoria}.json`)
- **Critérios:** Salvos em arquivo dedicado para resultados de avaliação

### Estrutura de Categorias
O sistema trabalha com 5 categorias fixas de arquivos:
- estatuto
- ata  
- identificacao
- licenca
- programacao

### Validação e Recuperação
A classe inclui mecanismos para validar e corrigir automaticamente estruturas de projetos, garantindo integridade dos dados e diretórios necessários .