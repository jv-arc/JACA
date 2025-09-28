# Resumo da Classe Settings

A classe **Settings** é responsável por gerenciar as configurações da aplicação através de um arquivo JSON, permitindo carregar, salvar e atualizar parâmetros de configuração .

## Dependências Principais

A classe depende dos seguintes módulos:
- **json** - Para serialização e deserialização de dados JSON
- **PathManager** - Para obtenção do caminho do arquivo de configuração via `get_app_config()`

## Constantes

**CONFIG_PATH** - Caminho para o arquivo de configuração obtido através de `PathManager.get_app_config()`

## Variáveis de Instância

A classe gerencia quatro configurações principais:
- **api_key** - Chave da API
- **extraction_model** - Modelo usado para extração de dados  
- **criteria_model** - Modelo usado para critérios
- **debug_mode** - Status do modo de debug (boolean)

## Métodos da Classe

### Inicialização e Carregamento
**`__init__()`**
- Inicializa todas as variáveis como None e carrega configurações
- **Dependências:** load_or_create_config()

**`load_or_create_config()`**
- Carrega configurações existentes ou cria arquivo com valores padrão
- **Comportamento:** Se arquivo existe, carrega dados; caso contrário, define valores padrão e salva
- **Valores padrão:** api_key='', extraction_model='gemini-2.5-Flash', criteria_model='gemini-2.0-flash', debug_mode=False
- **Dependências:** CONFIG_PATH.exists(), CONFIG_PATH.read_text(), json.loads(), save_config()

### Persistência
**`save_config()`**
- Salva as configurações atuais no arquivo JSON
- **Comportamento:** Serializa dados em JSON com indentação de 2 espaços e escreve no arquivo
- **Dependências:** json.dumps(), CONFIG_PATH.write_text()

### Métodos de Atualização
**`update_api_key(new_key)`**
- Atualiza a chave da API e salva automaticamente
- **Dependências:** save_config()

**`update_extraction_model(new_model)`**
- Atualiza o modelo de extração e salva automaticamente
- **Dependências:** save_config()

**`update_criteria_model(new_model)`**
- Atualiza o modelo de critérios e salva automaticamente
- **Dependências:** save_config()

**`update_debug_mode(new_status: bool)`**
- Atualiza o status do modo debug e salva automaticamente
- **Parâmetros:** new_status deve ser boolean
- **Dependências:** save_config()

## Características da Implementação

A classe implementa um padrão de **persistência automática**, onde cada método de atualização automaticamente salva as alterações no arquivo. Isso garante que as configurações sejam sempre mantidas sincronizadas entre memória e disco.

O tratamento de erros é robusto, capturando `json.JSONDecodeError` e `FileNotFoundError` para garantir que a aplicação sempre tenha configurações válidas, mesmo em caso de arquivo corrompido ou inexistente .