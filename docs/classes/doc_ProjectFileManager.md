# Resumo da Classe ProjectFileManager

A classe **ProjectFileManager** é responsável por implementar métodos para acessar e utilizar arquivos dentro dos projetos, permitindo obter dados dos arquivos e dos projetos .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **shutil** - Para operações de movimentação de arquivos
- **datetime** - Para manipulação de datas e timestamps
- **pathlib.Path** - Para manipulação de caminhos de arquivos
- **PathManager** - Gerenciamento de caminhos do projeto
- **Logger** - Sistema de logging
- **ProjectCRUDService** - Operações CRUD dos projetos

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o gerenciador com Logger e ProjectCRUDService
- **Dependências:** Logger, ProjectCRUDService

### Gerenciamento de Arquivos
**`add_pdf_file(project_name, uploaded_file, category)`**
- Adiciona arquivo PDF ao projeto dentro de uma categoria específica
- **Retorna:** bool (sucesso/erro)
- **Dependências:** crud_service.load_project, PathManager.get_uploaded_file_path, crud_service.save_project

**`remove_pdf_file(project_name, file_path)`**
- Remove arquivo do sistema de arquivos do projeto
- **Retorna:** bool (sucesso/erro)  
- **Dependências:** crud_service.load_project, Path.unlink, crud_service.save_project

**`move_file_to_category(project_name, old_path, new_category)`**
- Move arquivo entre categorias, atualizando nome e localização
- **Retorna:** bool (sucesso/erro)
- **Dependências:** crud_service.load_project, shutil.move, crud_service.save_project

### Consulta de Arquivos
**`get_files_by_category(project_name, category)`**
- Obtém lista de arquivos por categoria específica
- **Retorna:** List[str] (caminhos dos arquivos)
- **Dependências:** crud_service.load_project

**`get_all_files(project_name)`**
- Obtém todos os arquivos organizados por categoria
- **Retorna:** Dict[str, List[str]] (categorias e arquivos)
- **Dependências:** crud_service.load_project

**`get_files_in_category_from_filesystem(project_name, category)`**
- Obtém arquivos diretamente do sistema de arquivos
- **Retorna:** List[Path] (objetos Path)
- **Dependências:** PathManager.get_files_in_category

### Informações e Análise
**`get_file_info(file_path)`**
- Obtém informações detalhadas sobre arquivo específico
- **Retorna:** Dict[str, Any] (nome, tamanho, data modificação, etc.)
- **Dependências:** Path.stat, PathManager.get_file_extension, datetime.fromtimestamp

**`calculate_storage_usage(project_name)`**
- Calcula tamanho total do projeto em bytes
- **Retorna:** int (tamanho em bytes)
- **Dependências:** PathManager.get_project_path, Path.rglob, Path.stat

### Manutenção e Limpeza
**`verify_and_fix_file_paths(project_name)`**
- Valida e limpa caminhos, removendo referências a arquivos inexistentes
- **Retorna:** List[str] (arquivos removidos)
- **Dependências:** crud_service.load_project, Path.exists, crud_service.save_project

**`cleanup_orphaned_files(project_name)`**
- Remove arquivos órfãos não referenciados no projeto
- **Retorna:** List[str] (arquivos órfãos removidos)
- **Dependências:** crud_service.load_project, PathManager.get_project_files_dir, Path.unlink

### Funcionalidades Específicas
**`upload_signed_document(project_name, uploaded_file)`**
- Upload de documento assinado com nome padronizado "requerimento_assinado.pdf"
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_project_files_dir

A classe centraliza todas as operações relacionadas ao gerenciamento de arquivos dos projetos, desde adição e remoção até validação e limpeza, mantendo consistência entre os dados do projeto e o sistema de arquivos .