# Resumo da Classe ExportManager

A classe **ExportManager** é responsável por gerenciar a exportação e geração de pacotes completos de requisições em PDF, unindo formulários gerados com documentos originais do projeto .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **os** - Operações do sistema operacional e manipulação de caminhos
- **fitz (PyMuPDF)** - Biblioteca para manipulação e concatenação de PDFs
- **typing** - Tipagem (Dict, List)
- **Logger** - Sistema de logging
- **ProjectState** - Model representando estado do projeto
- **PdfGenerator** - Gerador de PDFs de formulários
- **ReportConfigManager** - Gerenciador de configurações de relatórios

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o gerenciador com Logger, PdfGenerator e ReportConfigManager
- Registra inicialização bem-sucedida no log
- **Dependências:** Logger, PdfGenerator, ReportConfigManager

### Métodos Internos (Privados)
**`_get_project_source_pdfs(project_data)`**
- Coleta lista de todos os caminhos de arquivos PDF originais do projeto
- Filtra apenas arquivos com extensão `.pdf` de todas as categorias
- **Retorna:** List[str] (caminhos dos PDFs)
- **Dependências:** project_data.base_files
- **Visibilidade:** Método privado (prefixo `_`)

### Método Principal de Exportação
**`generate_full_package(project_data, user_overrides, export_dir)`**
- Gera pacote completo de exportação unindo formulário e documentos do projeto
- **Retorna:** str (caminho do arquivo PDF final)
- **Dependências:** Múltiplas (ver fluxo detalhado abaixo)

## Fluxo Detalhado do Método Principal

O método `generate_full_package` executa as seguintes etapas:

### Geração do Formulário
1. **Criação do PDF do formulário** - Usa PdfGenerator com configurações do ReportConfigManager
2. **Validação** - Verifica sucesso da geração, aborta com IOError se falhar

### Coleta e Concatenação
3. **Coleta de PDFs** - Obtém todos os PDFs originais via `_get_project_source_pdfs`
4. **Criação do documento final** - Inicializa documento PyMuPDF vazio
5. **Inserção sequencial** - Adiciona primeiro o formulário, depois os documentos do usuário
6. **Verificação de existência** - Pula arquivos não encontrados com warning

### Finalização e Limpeza
7. **Salvamento** - Gera arquivo final nomeado como `REQUISICAO_{project_name}.pdf`
8. **Limpeza** - Remove arquivo temporário do formulário usando bloco `finally`

## Tratamento de Erros

A classe implementa tratamento robusto de erros:
- **Falha na geração do formulário** → Lança IOError e aborta processo
- **Falha na concatenação** → Lança IOError com detalhes do erro
- **Arquivos PDF não encontrados** → Registra warning e continua processamento
- **Limpeza garantida** → Usa bloco `finally` para remover arquivos temporários

O ExportManager centraliza toda a lógica de exportação, garantindo que todos os documentos relevantes sejam consolidados em um único PDF de requisição pronto para submissão .