import shutil
from typing import Optional

from app.core.path_manager import PathManager
from app.core.logger import Logger
from app.core.models import ProjectState
from app.core.project_crud_service import ProjectCRUDService
from app.core.export_manager import ExportManager


#================================================================
# CLASSE: DocumentPackageService
#----------------------------------------------------------------
# Implementa métodos para gerar, montar e gerenciar pacotes
# de exportação de documentos dentro dos projetos
#================================================================

class DocumentPackageService:

    def __init__(self):
        self.logger = Logger("DocumentPackageService")
        self.crud_service = ProjectCRUDService()
        self.export_manager = ExportManager()
        self.logger.info("Serviço inicializado com sucesso")



    #----------------------------------------------------------------
    # Gera o rascunho do documento para assinatura
    #----------------------------------------------------------------
    def generate_draft_for_signature(self, project_name: str) -> Optional[str]:
        self.logger.info(f"Gerando rascunho para assinatura: {project_name}")
        project = self.crud_service.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado")
            return None

        draft_path = PathManager.get_export_package_path(project_name)
        success = self.export_manager.generate_pdf_draft(project, draft_path)
        return str(draft_path) if success else None






    #----------------------------------------------------------------
    # Retorna o caminho para o rascunho gerado
    #----------------------------------------------------------------
    def get_draft_document_path(self, project_name: str) -> str:
        return str(PathManager.get_export_package_path(project_name))








    #----------------------------------------------------------------
    # Atualiza conteúdo de um rascunho existente
    #----------------------------------------------------------------
    def update_draft_document(self, project_name: str, new_content: bytes) -> bool:
        draft_path = PathManager.get_export_package_path(project_name)
        try:
            with open(draft_path, "wb") as f:
                f.write(new_content)
            self.logger.info("Rascunho atualizado com sucesso")
            return True
        except IOError as e:
            self.logger.error(f"Falha ao atualizar rascunho: {e}")
            return False






    #----------------------------------------------------------------
    # Monta o pacote final combinando rascunho e anexos
    #----------------------------------------------------------------
    def assemble_final_package(self, project_name: str) -> Optional[str]:
        self.logger.info(f"Montando pacote final: {project_name}")
        exports_dir = PathManager.get_project_exports_dir(project_name)
        signed_path = exports_dir / f"SIGNED_{project_name}.pdf"
        draft_path = exports_dir / f"REQUISICAO_{project_name}.pdf"

        project = self.crud_service.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado")
            return None

        attachments = PathManager.get_files_in_category(project_name, "files")
        success = self.export_manager.combine_signed_and_attachments(
            draft_path, signed_path, attachments, exports_dir
        )
        return str(signed_path) if success else None







    #----------------------------------------------------------------
    # Retorna o caminho para o documento assinado
    #----------------------------------------------------------------
    def get_signed_document_path(self, project_name: str) -> str:
        exports_dir = PathManager.get_project_exports_dir(project_name)
        return str(exports_dir / f"SIGNED_{project_name}.pdf")






    #----------------------------------------------------------------
    # Valida integridade do pacote antes de exportar
    #----------------------------------------------------------------
    def validate_package_completeness(self, project_name: str) -> bool:
        exports_dir = PathManager.get_project_exports_dir(project_name)
        draft = exports_dir / f"REQUISICAO_{project_name}.pdf"
        signed = exports_dir / f"SIGNED_{project_name}.pdf"
        return draft.exists() and signed.exists()





    #----------------------------------------------------------------
    # Exclui pacotes exportados antigos
    #----------------------------------------------------------------
    def delete_exported_package(self, project_name: str) -> bool:
        path = PathManager.get_export_package_path(project_name)
        try:
            path.unlink(missing_ok=True)
            self.logger.info("Pacote exportado excluído")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao excluir pacote: {e}")
            return False





    #----------------------------------------------------------------
    # Limpa todos os arquivos de exportação (rascunho e assinados)
    #----------------------------------------------------------------
    def delete_export_files(self, project_name: str) -> bool:
        exports_dir = PathManager.get_project_exports_dir(project_name)
        try:
            for file in exports_dir.iterdir():
                file.unlink()
            self.logger.info("Arquivos de exportação limpos")
            return True
        except Exception as e:
            self.logger.error(f"Falha ao limpar arquivos de exportação: {e}")
            return False





    #----------------------------------------------------------------
    # Obtém status atual do pacote (rascunho, assinado ou ausente)
    #----------------------------------------------------------------
    def get_package_status(self, project_name: str) -> str:
        exports_dir = PathManager.get_project_exports_dir(project_name)
        draft = exports_dir / f"REQUISICAO_{project_name}.pdf"
        signed = exports_dir / f"SIGNED_{project_name}.pdf"
        if signed.exists():
            return "signed"
        if draft.exists():
            return "draft"
        return "none"




    #----------------------------------------------------------------
    # Arquiva pacote completo movendo para backups
    #----------------------------------------------------------------
    def archive_completed_package(self, project_name: str) -> bool:
        signed = PathManager.get_project_exports_dir(project_name) / f"SIGNED_{project_name}.pdf"
        backup_dir = PathManager.get_backup_dir() / project_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(signed), str(backup_dir / signed.name))
            self.logger.info("Pacote arquivado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao arquivar pacote: {e}")
            return False
