# Resumo da Classe ExtractedDataManager

A classe **ExtractedDataManager** orquestra o processo de extração de dados de diferentes formatos de documentos, preparando o conteúdo para análise por IA (texto ou multimodal) .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **PyMuPDF (fitz)** - Para processamento de arquivos PDF
- **python-docx** - Para processamento de arquivos Word
- **PIL (Pillow)** - Para manipulação de imagens
- **GeminiClient** - Cliente para IA Gemini
- **PromptManager** - Gerenciamento de prompts de IA
- **PathManager** - Gerenciamento de caminhos
- **Logger** - Sistema de logging
- **StructuredExtraction** - Modelo de dados estruturados

## Constantes da Classe

**`WORKFLOWS`** - Dicionário com configurações de workflows para diferentes categorias:
- **estatuto** - Artigos, objetivos, governança
- **ata** - Data da reunião, participantes, decisões
- **licenca** - Número, validade, condições
- **programacao** - Cronograma, atividades, timeline

## Métodos da Classe

### Inicialização
**`__init__(gemini_client)`**
- Inicializa o gerenciador com cliente Gemini, prompt manager e logger
- **Dependências:** GeminiClient, PromptManager, PathManager, Logger

### Verificação e Carregamento
**`has_extracted_text(project_name, category)`**  
- Verifica se existe texto extraído para uma categoria específica
- **Retorna:** bool (True se existe, False caso contrário)
- **Dependências:** path.get_project_extracted_dir, os.path.exists, json.load

**`load_extracted_text(project_name, category)`**
- Carrega texto consolidado de uma categoria específica  
- **Retorna:** Optional[str] (texto extraído ou None)
- **Dependências:** path.get_project_extracted_dir, os.path.exists, json.load

### Extração de Conteúdo
**`_extract_content_from_files(file_paths)` (privado)**
- Extrai conteúdo (texto ou imagens) de diferentes formatos de arquivo
- **Retorna:** Dict (tipo: 'text'/'images'/'empty' e conteúdo)
- **Dependências:** docx.Document, fitz.open, PIL.Image.frombytes

**`run_extraction(file_paths, category)`**
- Método principal que coordena todo o processo de extração
- **Retorna:** Optional[Dict] (dados extraídos pela IA ou None)
- **Dependências:** _extract_content_from_files, prompt_manager, gemini_client

**`_extract_text_from_pdfs(file_paths)` (privado)**
- Extrai texto especificamente de arquivos PDF
- **Retorna:** str (texto consolidado)
- **Dependências:** fitz.open

### Consolidação de Dados
**`consolidate_content_fields(contentfields)`**
- Consolida campos de conteúdo em um texto único
- **Retorna:** str (texto consolidado)
- **Dependências:** Nenhuma dependência externa

**`_consolidate_content_fields(content_fields)` (privado)**
- Versão alternativa para consolidar campos de conteúdo
- **Retorna:** str (texto consolidado)
- **Dependências:** Nenhuma dependência externa

### Gerenciamento de Estruturas
**`create_empty_extraction_data(category)`**
- Cria estrutura vazia de extração para uma categoria
- **Retorna:** StructuredExtraction (estrutura inicializada)
- **Dependências:** StructuredExtraction, datetime.now

**`_create_empty_extraction_data(category)` (privado)**
- Versão alternativa para criar estrutura vazia
- **Retorna:** Dict (estrutura de dados vazia)
- **Dependências:** WORKFLOWS, datetime.now

**`get_workflow_fields(category)`**
- Obtém campos de workflow para uma categoria específica
- **Retorna:** Dict[str, List[str]] (campos do workflow)
- **Dependências:** WORKFLOWS (constante da classe)

### Persistência de Dados
**`save_extracted_text(project_name, category, text)`**
- Salva ou atualiza texto consolidado para uma categoria
- **Retorna:** bool (True se sucesso, False se erro)
- **Dependências:** path.get_project_extracted_dir, _create_empty_extraction_data, json.dump

**`save_dict_to_file(project_name, category, data)`**
- Salva dicionário de dados em arquivo JSON
- **Retorna:** bool (True se sucesso, False se erro)
- **Dependências:** path.get_extracted_file_path, json.dump

A classe centraliza o processamento inteligente de documentos, combinando extração de conteúdo tradicional com análise por IA, suportando fluxos de trabalho específicos para diferentes tipos de documentos .