# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .# Resumo da Classe ProjectWorkflowOrchestrator

A classe **ProjectWorkflowOrchestrator** implementa workflows de alto nível para extração, verificação, extração secundária e exportação de projetos .

## Dependências Principais

A classe possui múltiplas dependências de serviços especializados:
- **GeminiClient** - Cliente para API de IA
- **ExtractedDataManager** - Gerenciamento de dados extraídos  
- **CriteriaManager** - Gerenciamento de critérios de validação
- **ProjectDataService** - Serviço de dados do projeto
- **ExportManager** - Gerenciamento de exportação
- **ReportConfigManager** - Configuração de relatórios
- **ProjectCRUDService** - Operações CRUD de projetos
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa todos os serviços dependentes e o cliente Gemini
- **Dependências:** Todos os managers e serviços listados acima

### Workflows de Extração
**`run_extraction_for_category(project_name, category)`**
- Orquestra extração de dados por categoria via IA
- **Retorna:** Optional[Dict] (dados extraídos ou None)
- **Dependências:** crud.load_project, path.get_files_in_category, extract.run_extraction, data.save_structured_extraction

**`run_secondary_extraction(project_name, category)`**
- Executa extração secundária de campos específicos do texto bruto
- **Retorna:** Dict (campos extraídos)
- **Dependências:** extract.load_consolidated_text, extract.extract_fields

### Verificação de Critérios
**`execute_criteria_verification(project_name)`**
- Executa todas as verificações de critérios para um projeto
- **Retorna:** Dict (resultados de todos os critérios)
- **Dependências:** crud.load_project, criteria.list_categories, criteria.verify_all, PathManager.get_criteria_results_path, json.dump

**`execute_single_criterion_verification(project_name, criterion_id)`**
- Verifica um critério específico individualmente
- **Retorna:** Dict|None (resultado do critério)
- **Dependências:** get_all_criteria, criteria._perform_single_check, criteria.verify_single

**`update_manual_override(project_name, category, criterion_id, status, reason)`**
- Atualiza manualmente status de critério com override
- **Retorna:** bool (sucesso da atualização)
- **Dependências:** criteria.override

### Consulta de Dados
**`get_all_criteria(project_name)`**
- Carrega resultados de critérios existentes do arquivo JSON
- **Retorna:** Dict (resultados de critérios)
- **Dependências:** PathManager.get_criteria_results_path, json.load

### Exportação
**`export_project_package(project_name)`**
- Orquestra exportação completa do projeto com rascunho e montagem
- **Retorna:** Optional[str] (caminho do pacote exportado)
- **Dependências:** crud.load_project, export.generate_draft, r_conf.load_config, export.assemble_package

### Validação e Testes
**`test_api_connection()`**
- Valida conexão com API externa (Gemini)
- **Retorna:** bool (status da conexão)
- **Dependências:** ai.test_connection

**`validate_project_readiness(project_name)`**
- Valida se projeto está pronto para exportação
- **Retorna:** Dict[str, bool] (status de prontidão)
- **Dependências:** crud.load_project, get_all_criteria

## Problemas Identificados no Código

**Erros que necessitam correção:**
1. **Linha 78:** Variável `fields` não definida, deveria ser `category`
2. **Linha 115:** Variável `file_list` usada antes de ser definida
3. **Linha 120:** Código incompleto `self.projectfil`
4. **Linha 123:** Variável `project_data` não definida
5. **Método `run_secondary_extraction`:** Lógica inconsistente entre parâmetros e implementação

A classe serve como orquestrador central coordenando múltiplos serviços especializados para executar workflows completos de processamento de projetos, desde extração de dados até exportação final .