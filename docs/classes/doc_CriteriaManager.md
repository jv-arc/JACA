# Resumo da Classe CriteriaManager

A classe **CriteriaManager** é responsável por carregar critérios de um arquivo JSON e executar a verificação de conformidade em dados de um projeto usando inteligência artificial .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **json** - Para leitura e parsing do arquivo de critérios
- **GeminiClient** - Cliente de IA para execução das verificações
- **PromptManager** - Gerenciamento de prompts para a IA
- **Logger** - Sistema de logging
- **ProjectState** - Modelo de dados do projeto
- **PathManager** - Gerenciamento de caminhos dos arquivos

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa o gerenciador com todos os serviços necessários
- Carrega automaticamente os critérios do banco de dados JSON
- **Dependências:** Logger, GeminiClient, PromptManager, PathManager, load_criteria

### Carregamento de Dados
**`load_criteria(db_path)`**
- Carrega critérios de verificação de um arquivo JSON
- Trata erros de arquivo não encontrado e JSON malformado
- **Retorna:** List[Dict] (lista de critérios ou vazia em caso de erro)
- **Dependências:** json.load, open, codificação UTF-8

### Processamento de Contexto
**`_gather_context_text(criterion, project_data)`** *(método privado)*
- Coleta e consolida texto de contexto dos documentos fontes
- Busca dados extraídos usando os source_documents do critério
- Utiliza o consolidated_text como fonte da verdade após edições do usuário
- **Retorna:** Optional[str] (texto consolidado ou None)
- **Dependências:** getattr, ProjectState.extracted_data, consolidated_text

### Verificação Individual
**`_perform_single_check(criterion, project_data)`** *(método privado)*
- Executa verificação individual de um critério usando IA
- Processa o contexto, monta o prompt e interpreta a resposta da IA
- Trata erros de contexto, IA e formato de resposta
- **Retorna:** Dict (resultado com id, título, categoria, status, justificativa)
- **Dependências:** _gather_context_text, PromptManager.get_criteria_check_prompt, GeminiClient.generate_json_from_prompt

### Execução Completa
**`run_all_checks(project_data)`**
- Executa verificação de todos os critérios carregados para um projeto
- Método principal da classe que orquestra todo o processo
- **Retorna:** List[Dict] (resultados de todas as verificações)
- **Dependências:** _perform_single_check, self.criteria

## Fluxo de Execução

A classe segue um fluxo bem estruturado:

1. **Inicialização** - Carrega critérios do arquivo JSON automaticamente
2. **run_all_checks()** - Processa todos os critérios para um projeto
3. **_perform_single_check()** - Para cada critério individual
4. **_gather_context_text()** - Coleta dados relevantes dos documentos
5. **PromptManager + GeminiClient** - Executa verificação via IA
6. **Retorno consolidado** - Resultados estruturados com status e justificativas

A classe centraliza toda a lógica de verificação de conformidade, desde o carregamento dos critérios até a execução das verificações usando IA, fornecendo resultados estruturados e tratamento robusto de erros .