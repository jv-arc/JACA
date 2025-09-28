# Resumo da Classe ProjectManager

A classe **ProjectManager** funciona como uma **interface unificada** que expõe os métodos e orquestrações de múltiplas classes para a UI da aplicação, centralizando todas as operações relacionadas ao gerenciamento de projetos.

## Dependências Principais

A classe integra os seguintes serviços através de injeção de dependência:
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD de projetos
- **ProjectFileManager** - Gerenciamento de arquivos
- **ProjectDataService** - Operações com dados
- **ProjectWorkflowOrchestrator** - Orquestração de workflows
- **DocumentPackageService** - Serviços de pacotes de documentos
- **ProjectConfigurationService** - Configurações de projeto
- **ExportManager** - Gerenciamento de exportações
- **PathManager** - Gerenciamento de caminhos

## Métodos Organizados por Categoria

### **Inicialização**
**`__init__()`**
- Inicializa o ProjectManager com todas as dependências de serviços
- **Dependências:** Todos os serviços injetados via construtor

### **CRUD de Projetos** (5 métodos)
**`list_projects()`**
- Lista todos os projetos disponíveis
- **Retorna:** List[str] - nomes dos projetos
- **Dependências:** self.crud.list_projects

**`create_project(name)`**
- Cria novo projeto e retorna seu estado
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.create_project, self.crud.load_project

**`load_project(project_name)`**
- Carrega projeto existente pelo nome
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.load_project

**`save_project(project)`**
- Salva estado de um projeto
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.save_project

**`delete_project(project_name)`**
- Remove projeto completamente
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.delete_project

### **Gerenciamento de Arquivos** (4 métodos)
**`add_file(project_name, file_path, category)`**
- Adiciona arquivo ao projeto em categoria específica
- **Dependências:** self.file.add_pdf_file

**`remove_file(project_name, file_path)`**
- Remove arquivo do projeto
- **Dependências:** self.file.remove_pdf_file

**`list_files(project_name)`**
- Lista todos os arquivos organizados por categoria
- **Retorna:** Dict[str, List[str]]
- **Dependências:** self.file.get_all_files

**`list_files_in_category(project_name, category)`**
- Lista arquivos de categoria específica
- **Retorna:** List[str]
- **Dependências:** self.file.get_files_by_category

### **Dados e Extração** (13 métodos)
**Verificação de dados:**
- `has_extraction_for_category()` - Verifica se existe extração para categoria
- `has_extracted_text()` - Verifica se projeto possui texto extraído

**Operações de extração:**
- `run_extraction()` - Executa extração para categoria
- `load_structured_extraction()` - Carrega dados estruturados
- `save_structured_extraction()` - Salva dados estruturados
- `load_extracted_text()` - Carrega texto extraído
- `save_edited_text()` - Salva texto editado

**Consolidação e análise:**
- `get_consolidated_text()` - Obtém texto consolidado do projeto
- `get_pending_information()` - Obtém informações pendentes
- `update_extraction_field()` - Atualiza campo específico
- `mark_field_complete()` - Marca campo como completo

**Gerenciamento de diretores:**
- `get_director_list()` - Obtém lista de diretores
- `update_director_list()` - Atualiza lista de diretores

### **Critérios e Verificação** (3 métodos)
**`execute_criteria_verification(project_name)`**
- Executa verificação de todos os critérios
- **Retorna:** Dict - resultado da verificação
- **Dependências:** self.workflow.execute_criteria_verification

**`execute_single_criterion(project_name, criterion_id)`**
- Executa verificação de critério específico
- **Dependências:** self.workflow.execute_single_criterion_verification

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza sobrescrita manual de critério
- **Dependências:** self.workflow.update_manual_override
# Resumo da Classe ProjectManager

A classe **ProjectManager** funciona como uma **interface unificada** que expõe os métodos e orquestrações de múltiplas classes para a UI da aplicação, centralizando todas as operações relacionadas ao gerenciamento de projetos.

## Dependências Principais

A classe integra os seguintes serviços através de injeção de dependência:
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD de projetos
- **ProjectFileManager** - Gerenciamento de arquivos
- **ProjectDataService** - Operações com dados
- **ProjectWorkflowOrchestrator** - Orquestração de workflows
- **DocumentPackageService** - Serviços de pacotes de documentos
- **ProjectConfigurationService** - Configurações de projeto
- **ExportManager** - Gerenciamento de exportações
- **PathManager** - Gerenciamento de caminhos

## Métodos Organizados por Categoria

### **Inicialização**
**`__init__()`**
- Inicializa o ProjectManager com todas as dependências de serviços
- **Dependências:** Todos os serviços injetados via construtor

### **CRUD de Projetos** (5 métodos)
**`list_projects()`**
- Lista todos os projetos disponíveis
- **Retorna:** List[str] - nomes dos projetos
- **Dependências:** self.crud.list_projects

**`create_project(name)`**
- Cria novo projeto e retorna seu estado
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.create_project, self.crud.load_project

**`load_project(project_name)`**
- Carrega projeto existente pelo nome
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.load_project

**`save_project(project)`**
- Salva estado de um projeto
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.save_project

**`delete_project(project_name)`**
- Remove projeto completamente
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.delete_project

### **Gerenciamento de Arquivos** (4 métodos)
**`add_file(project_name, file_path, category)`**
- Adiciona arquivo ao projeto em categoria específica
- **Dependências:** self.file.add_pdf_file

**`remove_file(project_name, file_path)`**
- Remove arquivo do projeto
- **Dependências:** self.file.remove_pdf_file

**`list_files(project_name)`**
- Lista todos os arquivos organizados por categoria
- **Retorna:** Dict[str, List[str]]
- **Dependências:** self.file.get_all_files

**`list_files_in_category(project_name, category)`**
- Lista arquivos de categoria específica
- **Retorna:** List[str]
- **Dependências:** self.file.get_files_by_category

### **Dados e Extração** (13 métodos)
**Verificação de dados:**
- `has_extraction_for_category()` - Verifica se existe extração para categoria
- `has_extracted_text()` - Verifica se projeto possui texto extraído

**Operações de extração:**
- `run_extraction()` - Executa extração para categoria
- `load_structured_extraction()` - Carrega dados estruturados
- `save_structured_extraction()` - Salva dados estruturados
- `load_extracted_text()` - Carrega texto extraído
- `save_edited_text()` - Salva texto editado

**Consolidação e análise:**
- `get_consolidated_text()` - Obtém texto consolidado do projeto
- `get_pending_information()` - Obtém informações pendentes
- `update_extraction_field()` - Atualiza campo específico
- `mark_field_complete()` - Marca campo como completo

**Gerenciamento de diretores:**
- `get_director_list()` - Obtém lista de diretores
- `update_director_list()` - Atualiza lista de diretores

### **Critérios e Verificação** (3 métodos)
**`execute_criteria_verification(project_name)`**
- Executa verificação de todos os critérios
- **Retorna:** Dict - resultado da verificação
- **Dependências:** self.workflow.execute_criteria_verification

**`execute_single_criterion(project_name, criterion_id)`**
- Executa verificação de critério específico
- **Dependências:** self.workflow.execute_single_criterion_verification

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza sobrescrita manual de critério
- **Dependências:** self.workflow.update_manual_override

### **Pacotes e Exportação** (5 métodos)
**`export_package(project_name)`**
- Exporta pacote completo do projeto
- **Retorna:** Optional[str] - caminho do pacote
- **Dependências:** self.workflow.export_project_package

**`get_export_path(project_name)`**
- Obtém caminho do pacote se existir
- **Retorna:** str|None
- **Dependências:** self.path.get_export_package_path

**`generate_draft(project_name)`**
- Gera rascunho para assinatura
- **Dependências:** self.packages.generate_draft_for_signature

**`assemble_package(project_name)`**
- Monta pacote final
- **Dependências:** self.packages.assemble_final_package

**`delete_exports(project_name)`**
- Remove pacotes exportados
- **Dependências:** self.packages.delete_exported_package

### **Configuração** (2 métodos)
**`get_report_config(project_name)`**
- Obtém configuração de relatório
- **Retorna:** Dict
- **Dependências:** self.config.get_report_configuration

**`save_report_config(project_name, config_data)`**
- Salva configuração de relatório  
- **Dependências:** self.config.save_report_configuration

## Características da Arquitetura

A classe **ProjectManager** implementa o padrão **Facade**, fornecendo uma interface simplificada para um subsistema complexo de gerenciamento de projetos. Ela **delega** todas as operações para os serviços especializados, mantendo a **separação de responsabilidades** e facilitando a **manutenibilidade** do código.# Resumo da Classe ProjectManager

A classe **ProjectManager** funciona como uma **interface unificada** que expõe os métodos e orquestrações de múltiplas classes para a UI da aplicação, centralizando todas as operações relacionadas ao gerenciamento de projetos.

## Dependências Principais

A classe integra os seguintes serviços através de injeção de dependência:
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD de projetos
- **ProjectFileManager** - Gerenciamento de arquivos
- **ProjectDataService** - Operações com dados
- **ProjectWorkflowOrchestrator** - Orquestração de workflows
- **DocumentPackageService** - Serviços de pacotes de documentos
- **ProjectConfigurationService** - Configurações de projeto
- **ExportManager** - Gerenciamento de exportações
- **PathManager** - Gerenciamento de caminhos

## Métodos Organizados por Categoria

### **Inicialização**
**`__init__()`**
- Inicializa o ProjectManager com todas as dependências de serviços
- **Dependências:** Todos os serviços injetados via construtor

### **CRUD de Projetos** (5 métodos)
**`list_projects()`**
- Lista todos os projetos disponíveis
- **Retorna:** List[str] - nomes dos projetos
- **Dependências:** self.crud.list_projects

**`create_project(name)`**
- Cria novo projeto e retorna seu estado
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.create_project, self.crud.load_project

**`load_project(project_name)`**
- Carrega projeto existente pelo nome
- **Retorna:** Optional[ProjectState]
- **Dependências:** self.crud.load_project

**`save_project(project)`**
- Salva estado de um projeto
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.save_project

**`delete_project(project_name)`**
- Remove projeto completamente
- **Retorna:** bool (sucesso)
- **Dependências:** self.crud.delete_project

### **Gerenciamento de Arquivos** (4 métodos)
**`add_file(project_name, file_path, category)`**
- Adiciona arquivo ao projeto em categoria específica
- **Dependências:** self.file.add_pdf_file

**`remove_file(project_name, file_path)`**
- Remove arquivo do projeto
- **Dependências:** self.file.remove_pdf_file

**`list_files(project_name)`**
- Lista todos os arquivos organizados por categoria
- **Retorna:** Dict[str, List[str]]
- **Dependências:** self.file.get_all_files

**`list_files_in_category(project_name, category)`**
- Lista arquivos de categoria específica
- **Retorna:** List[str]
- **Dependências:** self.file.get_files_by_category

### **Dados e Extração** (13 métodos)
**Verificação de dados:**
- `has_extraction_for_category()` - Verifica se existe extração para categoria
- `has_extracted_text()` - Verifica se projeto possui texto extraído

**Operações de extração:**
- `run_extraction()` - Executa extração para categoria
- `load_structured_extraction()` - Carrega dados estruturados
- `save_structured_extraction()` - Salva dados estruturados
- `load_extracted_text()` - Carrega texto extraído
- `save_edited_text()` - Salva texto editado

**Consolidação e análise:**
- `get_consolidated_text()` - Obtém texto consolidado do projeto
- `get_pending_information()` - Obtém informações pendentes
- `update_extraction_field()` - Atualiza campo específico
- `mark_field_complete()` - Marca campo como completo

**Gerenciamento de diretores:**
- `get_director_list()` - Obtém lista de diretores
- `update_director_list()` - Atualiza lista de diretores

### **Critérios e Verificação** (3 métodos)
**`execute_criteria_verification(project_name)`**
- Executa verificação de todos os critérios
- **Retorna:** Dict - resultado da verificação
- **Dependências:** self.workflow.execute_criteria_verification

**`execute_single_criterion(project_name, criterion_id)`**
- Executa verificação de critério específico
- **Dependências:** self.workflow.execute_single_criterion_verification

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza sobrescrita manual de critério
- **Dependências:** self.workflow.update_manual_override

### **Pacotes e Exportação** (5 métodos)
**`export_package(project_name)`**
- Exporta pacote completo do projeto
- **Retorna:** Optional[str] - caminho do pacote
- **Dependências:** self.workflow.export_project_package

**`get_export_path(project_name)`**
- Obtém caminho do pacote se existir
- **Retorna:** str|None
- **Dependências:** self.path.get_export_package_path

**`generate_draft(project_name)`**
- Gera rascunho para assinatura
- **Dependências:** self.packages.generate_draft_for_signature

**`assemble_package(project_name)`**
- Monta pacote final
- **Dependências:** self.packages.assemble_final_package

**`delete_exports(project_name)`**
- Remove pacotes exportados
- **Dependências:** self.packages.delete_exported_package

### **Configuração** (2 métodos)
**`get_report_config(project_name)`**
- Obtém configuração de relatório
- **Retorna:** Dict
- **Dependências:** self.config.get_report_configuration

**`save_report_config(project_name, config_data)`**
- Salva configuração de relatório  
- **Dependências:** self.config.save_report_configuration

## Características da Arquitetura

A classe **ProjectManager** implementa o padrão **Facade**, fornecendo uma interface simplificada para um subsistema complexo de gerenciamento de projetos. Ela **delega** todas as operações para os serviços especializados, mantendo a **separação de responsabilidades** e facilitando a **manutenibilidade** do código.
### **Pacotes e Exportação** (5 métodos)
**`export_package(project_name)`**
- Exporta pacote completo do projeto
- **Retorna:** Optional[str] - caminho do pacote
- **Dependências:** self.workflow.export_project_package

**`get_export_path(project_name)`**
- Obtém caminho do pacote se existir
- **Retorna:** str|None
- **Dependências:** self.path.get_export_package_path

**`generate_draft(project_name)`**
- Gera rascunho para assinatura
- **Dependências:** self.packages.generate_draft_for_signature

**`assemble_package(project_name)`**
- Monta pacote final
- **Dependências:** self.packages.assemble_final_package

**`delete_exports(project_name)`**
- Remove pacotes exportados
- **Dependências:** self.packages.delete_exported_package

### **Configuração** (2 métodos)
**`get_report_config(project_name)`**
- Obtém configuração de relatório
- **Retorna:** Dict
- **Dependências:** self.config.get_report_configuration

**`save_report_config(project_name, config_data)`**
- Salva configuração de relatório  
- **Dependências:** self.config.save_report_configuration

## Características da Arquitetura

A classe **ProjectManager** implementa o padrão **Facade**, fornecendo uma interface simplificada para um subsistema complexo de gerenciamento de projetos. Ela **delega** todas as operações para os serviços especializados, mantendo a **separação de responsabilidades** e facilitando a **manutenibilidade** do código.