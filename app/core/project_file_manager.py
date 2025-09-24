import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.core.path_manager import PathManager
from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService

#================================================================
# CLASSE: ProjectFileManager
#----------------------------------------------------------------
# Implementa metodos para acessar e utilizar arquivos dentro dos
# projetos permitindo obter dados dos arquivos e dos projetos
#================================================================


class ProjectFileManager:

    def __init__(self):
        self.logger = Logger(name="ProjectFileManager")
        self.crud_service = ProjectCRUDService()
        self.logger.info("Serviço iniciado com suscesso.")




    #----------------------------------------------------------------
    # adiciona arquivo ao projeto dentro de sua categoria
    #----------------------------------------------------------------
    def add_pdf_file(self, project_name: str, uploaded_file: Any, category: str) -> bool:

        project = self.crud_service.load_project(project_name)

        # verifica projeto
        if project is None:
            self.logger.error(f"Não foi possível adicionar arquivo. Projeto '{project_name}' não encontrado")
            return False

        # verifica categoria
        if category not in project.base_files:
            project.base_files[category] = []

        # tenta adicionar
        try:

            # metodo de obter caminho ja faz isso com um nome seguro
            file_path = PathManager.get_uploaded_file_path(project_name, category, uploaded_file.name)

            # Garante que diretorio existe
            if not file_path.parent.is_dir():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                self.logger.warning(f"Diretorio '{file_path.parent}' criado")

            file_path.write_bytes(uploaded_file.getbuffer())

            # adiciona ao projeto
            file_path_str = str(file_path)
            if file_path_str not in project.base_files[category]:
                project.base_files[category].append(file_path_str)

            # salva o projeto
            success = self.crud_service.save_project(project)
            if success:
                self.logger.info(f"Arquivo '{uploaded_file.name}' adicionado à categoria '{category}' do projeto '{project_name}'")

            return success

        except Exception as e:
            self.logger.error(f"Erro ao adicionar arquivo: {e}", exc_info=True)
            return False






    #----------------------------------------------------------------
    # Remove arquivo do sistema de arquivos do projeto
    #----------------------------------------------------------------
    def remove_pdf_file(self, project_name: str, file_path: str) -> bool:
        project = self.crud_service.load_project(project_name)

        # verifica projeto
        if project is None:
            self.logger.error(f"Não foi possível remover arquivo. Projeto'{project_name}' não encontrado")
            return False

        # tenta remover
        try:
            file_removed = False

            # procura categoria do arquivo
            for category in project.base_files:
                if file_path in project.base_files[category]:
                    project.base_files[category].remove(file_path)
                    file_removed = True
                    break

            # remove arquivo
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                file_path_obj.unlink()

            if file_removed:
                success = self.crud_service.save_project(project)
                if success:
                    self.logger.info(f"Arquivo '{file_path}' removido do projeto '{project_name}'")
                return success
            
            else:
                self.logger.warning(f"Arquivo '{file_path}' não encontrado no projeto '{project_name}'")
                return True

        except Exception as e:
            self.logger.error(f"Erro ao remover arquivo{e}", exc_info=True)
            return False





    #----------------------------------------------------------------
    # Obtem arquivos por categoria
    #----------------------------------------------------------------
    def get_files_by_category(self, project_name: str, category: str) -> List[str]:
        project = self.crud_service.load_project(project_name)
        if project is None:
            self.logger.error(f"Não foi possível obter lista da categoria '{category}'. O projeto '{project_name}' nao foi encontrado")
            return []

        return project.base_files.get(category, [])






    #----------------------------------------------------------------
    # obtem todos os arquivos do projeto em uma lista
    #----------------------------------------------------------------
    def get_all_files(self, project_name: str) -> Dict[str, List[str]]:
        project = self.crud_service.load_project(project_name)
        if project is None:
            self.logger.error(f"Não foi possível obter dicionario de arquivos. O projeto '{project_name}' nao foi encontrado")
            return {}

        return project.base_files.copy()







    #----------------------------------------------------------------
    # valida e limpa caminhos de arquivos
    #----------------------------------------------------------------
    def verify_and_fix_file_paths(self, project_name: str) -> List[str]:
        project = self.crud_service.load_project(project_name)
        if project is None:
            self.logger.error(f"Nao foi possivel validar arquivos. Projeto '{project_name}' nao foi encontrado")
            return []

        removed_files = []
        files_updated = False

        for category in project.base_files:
            existing_files = []

            for file_path in project.base_files[category]:
                if Path(file_path).exists():
                    existing_files.append(file_path)
                else:
                    removed_files.append(file_path)
                    files_updated = True
                    self.logger.warning(f"Arquivo nao existente de caminho '{file_path}' foi removido do projeto")

            project.base_files[category] = existing_files

        # Salva projetos se houver modificacao
        if files_updated:
            success = self.crud_service.save_project(project)
            if success:
                self.logger.info(f"Caminhos limpos e validados para projeto '{project_name}'")
            else:
                self.logger.error(f"Nao foi possivel salvar arquivos para o projeto '{project_name}'")

        return removed_files







    #----------------------------------------------------------------
    # faz upload de arquivos com nome padronizado
    #----------------------------------------------------------------
    def upload_signed_document(self, project_name: str, uploaded_file: Any) -> bool:
        try:
            signed_path = PathManager.get_project_files_dir(project_name) / "requerimento_assinado.pdf"

            signed_path.parent.mkdir(parents=True, exist_ok=True)

            with open(signed_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            self.logger.info(f"Documento assinado salvo para '{project_name}' em: {signed_path}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao salvar documento assinado: {e}", exc_info=True)
            return False






    #----------------------------------------------------------------
    # move arquivo para a categoria
    #----------------------------------------------------------------
    def move_file_to_category(self, project_name: str, old_path: str, new_category: str) -> bool:

        project = self.crud_service.load_project(project_name)
        if project is None:
            return False

        try:
            # Encontra categoria atual do arquivo
            current_category = None
            for category in project.base_files:
                if old_path in project.base_files[category]:
                    current_category = category
                    break

            if current_category is None:
                self.logger.error(f"Arquivo '{old_path}' não encontrado em nenhuma categoria")
                return False

            # garante que categoria existe
            if new_category not in project.base_files:
                project.base_files[new_category] = []

            # Atualiza nos dados do projeto
            project.base_files[current_category].remove(old_path)

            # Gera novo caminho para o arquivo
            old_path_obj = Path(old_path)
            new_filename = f"{new_category}_{old_path_obj.name.split('_', 1)[-1]}"
            new_path = old_path_obj.parent / new_filename

            # Move physical file
            shutil.move(old_path, new_path)

            # Add to new category
            project.base_files[new_category].append(str(new_path))

            # salva projeto
            success = self.crud_service.save_project(project)
            if success:
                self.logger.info(f"arquivo movido de '{current_category}' para '{new_category}'")

            return success

        except Exception as e:
            self.logger.error(f"Erro ao mover arquivo: {e}", exc_info=True)
            return False








    #----------------------------------------------------------------
    # obtem informacoes de arquivo
    #----------------------------------------------------------------
    def get_file_info(self, file_path: str) -> Dict[str, Any]:

        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return {}

        try:
            stat = file_path_obj.stat()
            return {
                'name': file_path_obj.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': PathManager.get_file_extension(file_path_obj.name),
                'exists': True
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter dados de '{file_path}': {e}")
            return {'exists': False, 'error': str(e)}
        








    #----------------------------------------------------------------
    # calcula tamanho do projeto em bytes
    #----------------------------------------------------------------
    def calculate_storage_usage(self, project_name: str) -> int:
        total_size = 0

        try:
            project_path = PathManager.get_project_path(project_name)

            if project_path.exists():
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size

            return total_size

        except Exception as e:
            self.logger.error(f"Erro ao calcular tamanho do projeto '{project_name}': {e}")
            return 0






    #----------------------------------------------------------------
    # obtem lista de arquivos diretamente usando a categoria
    #----------------------------------------------------------------
    def get_files_in_category_from_filesystem(self, project_name: str, category: str) -> List[Path]:
        return PathManager.get_files_in_category(project_name, category)







    #----------------------------------------------------------------
    # Limpa arquivos orfaos
    #----------------------------------------------------------------
    def cleanup_orphaned_files(self, project_name: str) -> List[str]:
        project = self.crud_service.load_project(project_name)
        if project is None:
            return []

        # obtem todos os arquivos referenciados do projeto
        referenced_files = set()
        for file_list in project.base_files.values():
            referenced_files.update(file_list)


        # obtem todos os arquivos no diretorio do projeto
        files_dir = PathManager.get_project_files_dir(project_name)
        orphaned_files = []


        # tenta apagar arquivos
        try:
            if files_dir.exists():
                for file_path in files_dir.iterdir():
                    if file_path.is_file() and str(file_path) not in referenced_files:
                        file_path.unlink()
                        orphaned_files.append(str(file_path))
                        self.logger.info(f"Removido arquivo orfao {file_path}")

            return orphaned_files

        except Exception as e:
            self.logger.error(f"Erro ao limpar arquivo orfao {e}", exc_info=True)
            return []
