# Classe ProjectConfigurationService

A classe **ProjectConfigurationService** implementa métodos para gerenciar configurações de projetos e relatórios dentro da aplicação, centralizando o controle de configurações tanto globais quanto específicas de projeto .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **json** - Para manipulação de arquivos de configuração JSON
- **datetime** - Para timestamps de modificação
- **PathManager** - Gerenciamento de caminhos de configuração
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD dos projetos
- **ReportConfigManager** - Gerenciamento específico de configurações de relatórios

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o serviço com Logger, ProjectCRUDService e ReportConfigManager
- **Dependências:** Logger, ProjectCRUDService, ReportConfigManager

### Configuração de Relatórios
**`get_report_configuration(project_name=None)`**
- Obtém configuração de relatório para a interface do usuário
- **Retorna:** Dict (configuração ou dict vazio)
- **Dependências:** report_config_manager.get_full_config

**`save_report_configuration(config_data, project_name=None)`**
- Salva nova configuração de relatório recebida da UI
- **Retorna:** bool (sucesso/erro)
- **Dependências:** report_config_manager.save_config

**`reset_report_configuration(project_name=None)`**
- Reseta configuração para os padrões do arquivo template
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_report_config, json.load, save_report_configuration

**`validate_report_configuration(config_data)`**
- Valida estrutura e campos obrigatórios da configuração
- **Retorna:** tuple[bool, List[str]] (é_válido, lista_de_erros)
- **Dependências:** Validações internas (isinstance, verificações de campos)

### Configurações de Projeto
**`get_project_settings(project_name)`**
- Obtém configurações específicas de um projeto
- **Retorna:** Dict (configurações ou dict vazio)
- **Dependências:** crud_service.load_project

**`update_project_settings(project_name, settings)`**
- Atualiza configurações específicas do projeto e timestamp de modificação
- **Retorna:** bool (sucesso/erro)
- **Dependências:** crud_service.load_project, datetime.now, crud_service.save_project

### Import/Export de Configurações
**`export_project_configuration(project_name)`**
- Exporta configuração completa do projeto (settings + report config)
- **Retorna:** Optional[Dict] (dados de exportação ou None)
- **Dependências:** get_project_settings, get_report_configuration, datetime.now

**`import_project_configuration(project_name, config_data)`**
- Importa configuração para um projeto a partir de dados externos
- **Retorna:** bool (sucesso/erro)
- **Dependências:** update_project_settings, save_report_configuration

## Funcionalidades Principais

### Gerenciamento de Relatórios
A classe oferece controle completo sobre configurações de relatórios, incluindo obtenção, salvamento, reset para padrões e validação de estrutura com verificação de campos obrigatórios como 'tables' e 'metadata'.

### Configurações por Projeto  
Permite armazenar e gerenciar configurações específicas de cada projeto, mantendo isolamento entre diferentes projetos e atualizando automaticamente timestamps de modificação.

### Portabilidade de Configurações
Implementa sistema completo de import/export que permite transferir configurações entre projetos ou fazer backup das configurações, incluindo tanto settings do projeto quanto configurações de relatórios.

A classe centraliza todo o gerenciamento de configurações da aplicação, proporcionando uma interface unificada para operações de configuração tanto globais quanto específicas de projeto .