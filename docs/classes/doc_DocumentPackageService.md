# Resumo da Classe DocumentPackageService

A classe **DocumentPackageService** implementa métodos para gerar, montar e gerenciar pacotes de exportação de documentos dentro dos projetos .

## Dependências Principais

A classe depende dos seguintes módulos e serviços:
- **shutil** - Para operações de movimentação e cópia de arquivos
- **typing.Optional** - Para tipos opcionais
- **PathManager** - Gerenciamento de caminhos e diretórios
- **Logger** - Sistema de logging e registro de eventos
- **ProjectState** - Modelo de estado do projeto
- **ProjectCRUDService** - Operações CRUD dos projetos
- **ExportManager** - Gerenciador especializado em exportação

## Métodos da Classe

### Inicialização
**`__init__()`**
- Inicializa o serviço com Logger, ProjectCRUDService e ExportManager
- **Dependências:** Logger, ProjectCRUDService, ExportManager

### Geração de Documentos
**`generate_draft_for_signature(project_name)`**
- Gera o rascunho do documento para assinatura
- **Retorna:** Optional[str] (caminho do rascunho ou None)
- **Dependências:** crud_service.load_project, PathManager.get_export_package_path, export_manager.generate_pdf_draft

**`update_draft_document(project_name, new_content)`**
- Atualiza conteúdo de um rascunho existente com novos bytes
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_export_package_path

**`assemble_final_package(project_name)`**
- Monta o pacote final combinando rascunho e anexos
- **Retorna:** Optional[str] (caminho do pacote final ou None)
- **Dependências:** PathManager.get_project_exports_dir, crud_service.load_project, PathManager.get_files_in_category, export_manager.combine_signed_and_attachments

### Consulta de Caminhos
**`get_draft_document_path(project_name)`**
- Retorna o caminho para o rascunho gerado
- **Retorna:** str (caminho do documento rascunho)
- **Dependências:** PathManager.get_export_package_path

**`get_signed_document_path(project_name)`**
- Retorna o caminho para o documento assinado
- **Retorna:** str (caminho do documento assinado)
- **Dependências:** PathManager.get_project_exports_dir

### Validação e Status
**`validate_package_completeness(project_name)`**
- Valida integridade do pacote verificando se rascunho e documento assinado existem
- **Retorna:** bool (True se pacote completo)
- **Dependências:** PathManager.get_project_exports_dir, Path.exists

**`get_package_status(project_name)`**
- Obtém status atual do pacote (rascunho, assinado ou ausente)
- **Retorna:** str ('signed', 'draft' ou 'none')
- **Dependências:** PathManager.get_project_exports_dir, Path.exists

### Limpeza e Remoção
**`delete_exported_package(project_name)`**
- Exclui pacotes exportados antigos
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_export_package_path, Path.unlink

**`delete_export_files(project_name)`**
- Limpa todos os arquivos de exportação (rascunho e assinados)
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_project_exports_dir, Path.iterdir, Path.unlink

### Arquivamento
**`archive_completed_package(project_name)`**
- Arquiva pacote completo movendo para diretório de backups
- **Retorna:** bool (sucesso/erro)
- **Dependências:** PathManager.get_project_exports_dir, PathManager.get_backup_dir, shutil.move

A classe centraliza todo o fluxo de geração, montagem e gerenciamento de pacotes de documentos, desde a criação do rascunho até o arquivamento final, mantendo controle sobre o status e integridade dos pacotes exportados .