# Resumo da Classe ReportConfigManager

A classe **ReportConfigManager** é responsável por gerenciar configurações para geração de relatórios, carregando e salvando dados de configuração em arquivo JSON .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **json** - Para serialização e deserialização de dados JSON
- **typing** - Para tipagem (Dict, List, Optional)
- **Logger** - Sistema de logging da aplicação
- **PathManager** - Gerenciamento de caminhos de arquivos da aplicação

## Variáveis de Instância

- **self.logger** - Logger para registrar eventos e erros
- **self.path** - Instância do PathManager
- **self.config_path** - Caminho do arquivo de configuração (string)
- **self.config_data** - Dados de configuração carregados (Dict)

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o gerenciador de configurações de relatório
- Configura logger, path manager e tenta carregar configurações automaticamente
- **Dependências:** Logger, PathManager.get_app_config, load_config

### Gerenciamento de Configurações
**`load_config()`**
- Carrega configurações do arquivo JSON para a memória
- **Retorna:** None (modifica self.config_data)
- **Dependências:** json.load, open (built-in)
- **Tratamento de erros:** FileNotFoundError, JSONDecodeError

**`save_config(new_config_data)`**
- Salva novas configurações no arquivo JSON e atualiza dados em memória
- **Parâmetros:** new_config_data: Dict
- **Retorna:** bool (True para sucesso, False para erro)
- **Dependências:** json.dump, open (built-in)
- **Tratamento de erros:** IOError, Exception genérica

### Consulta de Configurações
**`get_full_config()`**
- Retorna todas as configurações carregadas
- **Retorna:** Dict (dados completos de configuração)
- **Dependências:** self.config_data
- Método simples que fornece acesso completo aos dados de configuração

**`get_user_input_fields()`**
- Extrai e retorna campos que requerem entrada do usuário das configurações
- **Retorna:** List[Dict] (campos que necessitam input do usuário)
- **Dependências:** self.config_data
- Filtra campos com source='user_input' das tabelas nas configurações

## Características Importantes

### Tratamento de Erros Robusto
A classe implementa tratamento específico para:
- **FileNotFoundError** - Quando arquivo de configuração não existe
- **JSONDecodeError** - Quando arquivo JSON está mal formatado
- **IOError** - Para erros de entrada/saída durante salvamento
- **Exception genérica** - Para erros inesperados durante salvamento

### Persistência de Dados
- Utiliza encoding UTF-8 para suporte a caracteres especiais
- Formata JSON com indentação para melhor legibilidade
- Mantém sincronização entre arquivo e dados em memória

A classe centraliza o gerenciamento de configurações de relatório, fornecendo uma interface segura e confiável para carregar, salvar e consultar configurações necessárias para geração de relatórios .