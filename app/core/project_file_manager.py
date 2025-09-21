
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
import shutil
from datetime import datetime

from .path_manager import PathManager
from .logger import Logger


class ProjectFileManager:

    def __init__(self, logger: Logger = Logger("ProjectFileManager")):
        self.logger = logger
        self._ensure_base_directories()

    # garante que os diretorios base do projeto existem
    def _ensure_base_directories(self):
        base_dirs = [
            PathManager.get_project_dir(),
            PathManager.get_temp_dir(),
            PathManager.get_logs_dir(),
            PathManager.get_backup_dir()
        ]

        for directory in base_dirs:
            self.ensure_directory_exists(directory)

    # garante que pasta existe
    def ensure_directory_exists(self, directory_path: Path) -> bool:
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao criar diretorio: {directory_path} \n {e}")
            return False

    # verifica que arquivo existe
    def file_exists(self, file_path: Path) -> bool:
        return file_path.exists() and file_path.is_file()

    # verifica se diretorio existe
    def directory_exists(self, dir_path: Path) -> bool:
        return dir_path.exists() and dir_path.is_dir()


    #================================================================
    # Metodos para organizacao dos projetos
    #================================================================

    # Lista projetos disponiveis
    def list_all_projects(self) -> List[str]:
        projects = []
        project_dir = PathManager.get_project_dir()

        if not project_dir.exists():
            self.logger.warning("Diretório de projetos não existe!")
            return projects

        try:
            for item in project_dir.iterdir():
                if item.is_dir():
                    project_name = PathManager.extract_project_name_from_path(item)
                    if self.validate_project_structure(project_name):
                        projects.append(project_name)

            self.logger.info(f"Encontrados {len(projects)} projetos validos")
            return sorted(projects)

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao listar projetos \n {e}")
            return []

    # valida estrutura de projeto
    def validate_project_structure(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            return False
        return PathManager.is_valid_project_structure(project_name)


    # verifica se projeto existe 
    def project_exists(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            return False

        project_path = PathManager.get_project_path(project_name)
        return self.directory_exists(project_path)

    # cria estrutura de projeto
    def create_project_structure(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto invalido: {project_name}")
            return False

        try:
            subdirs = PathManager.get_all_project_subdirs(project_name)

            for dir_name, dir_path in subdirs.items():
                if not self.ensure_directory_exists(dir_path):
                    self.logger.error(f"Falha ao criar diretorio com o nome: {dir_name} e caminho: {dir_path}")
                    return False

            self.logger.info(f"Estrutura criada com sucesso para o projeto: {project_name}")
            return True

        except Exception as e:
            self.logger.error(f"Falha ao criar a estrutura do projeto: {project_name} \n {e}", )
            return False


    # deleta um projeto inteiro e sua estrutura
    def delete_project_completely(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Projeto: {project_name} não existe")
            return False

        try:
            project_path = PathManager.get_project_path(project_name)

            # VERIFICACAO DE SEGURANCA
            if not PathManager.is_under_projects_dir(project_path):
                self.logger.error(f"Violacao de segurança! Tentativa de apagar algo fora do diretorio do projeto: {project_path}")
                return False

            if project_path.exists():
                shutil.rmtree(project_path)
                self.logger.info(f"Projeto deletado corretamente{project_name}")
            else:
                self.logger.info(f"Projeto nao existe {project_name}")

            return True

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao apagar o projeto {project_name} \n {e}")
            return False


    #================================================================
    # JSON DATA OPERATIONS
    #================================================================

    # Salva dados no JSON formatado
    def save_json_file(self, file_path: Path, data: Any) -> bool:
        try:
            self.ensure_directory_exists(file_path.parent)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except (OSError) as e:
            self.logger.error(f"Falha ao salvar no arquivo {file_path} \n {e}")
            return False



    # carrega dados de um json
    def load_json_file(self, file_path: Path) -> Optional[Dict]:
        try:
            if not self.file_exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except (OSError, json.JSONDecodeError) as e:
            self.logger.error(f"Falha ao carregar arquivo: {file_path} \n {e}" )
            return None

    # carrega dados do arquivo JSON com metadados do projeto
    def load_project_json(self, project_name: str) -> Optional[Dict]:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto invalido: {project_name}")
            return None

        project_json_path = PathManager.get_project_json_path(project_name)
        data = self.load_json_file(project_json_path)

        if data:
            self.logger.info(f"Projeto {project_name} carregado com sucesso")
        else:
            self.logger.warning(f"Arquivo de metadados invalido para o projeto {project_name}")

        return data


    # salva dados para um arquivo JSON de metadados de um projeto 
    def save_project_json(self, project_name: str, project_data: Dict) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto {project_name} invalido")
            return False

        project_json_path = PathManager.get_project_json_path(project_name)

        project_data['lastModified'] = datetime.now().isoformat()

        success = self.save_json_file(project_json_path, project_data)

        if success:
            self.logger.info(f"project.json salvado com sucesso para projeto: {project_name}")

        return success


    # carrega dados extraidos para uma categoria especifica
    def load_extracted_data_file(self, project_name: str, category: str) -> Optional[Dict]:
        if not PathManager.validate_project_name(project_name):
            return None

        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)
        return self.load_json_file(extracted_file_path)


    # salva dados extraidos de uma categoria especifica
    def save_extracted_data_file(self, project_name: str, category: str, data: Dict) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Invalid project name: {project_name}")
            return False

        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)

        data['lastModified'] = datetime.now().isoformat()
        if 'extractedAt' not in data:
            data['extractedAt'] = datetime.now().isoformat()

        success = self.save_json_file(extracted_file_path, data)

        if success:
            self.logger.info(f"Dados salvos com sucesso para projeto {project_name}, na categoria: {category}")

        return success


    # verifica se dados extraidos existem
    def extracted_data_exists(self, project_name: str, category: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            return False

        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)

        if not self.file_exists(extracted_file_path):
            return False

        data = self.load_json_file(extracted_file_path)
        if not data:
            return False

        consolidated_text = data.get('consolidatedText', '').strip()
        if consolidated_text:
            return True

        content_fields = data.get('contentFields', {})
        return any(value and str(value).strip() for value in content_fields.values())



    # carrega resultados dos criterios de um projeto
    def load_criteria_results(self, project_name: str) -> Optional[Dict]:
        if not PathManager.validate_project_name(project_name):
            return None

        criteria_path = PathManager.get_criteria_results_path(project_name)
        return self.load_json_file(criteria_path)


    # salva arquivo de criterios para um arquivo
    def save_criteria_results(self, project_name: str, criteria_data: Dict) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto: {project_name} inválido")
            return False

        criteria_path = PathManager.get_criteria_results_path(project_name)


        if isinstance(criteria_data, list):
            timestamped_data = {
                'results': criteria_data,
                'lastUpdated': datetime.now().isoformat()
            }
        else:
            timestamped_data = criteria_data.copy()
            timestamped_data['lastUpdated'] = datetime.now().isoformat()

        success = self.save_json_file(criteria_path, timestamped_data)

        if success:
            self.logger.info(f"Dados de criterios do projeto {project_name} foram salvos com sucesso")

        return success


    #================================================================
    # Lidando com arquivos
    #================================================================


    # salva arquivo no diretorio de um projeto
    def save_uploaded_file(self, project_name: str, category: str, filename: str, file_data: bytes) -> Optional[Path]:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto invalido: {project_name}")
            return None

        try:
            file_path = PathManager.get_uploaded_file_path(project_name, category, filename)

            # Ensure directory exists
            self.ensure_directory_exists(file_path.parent)

            # Write binary data
            with open(file_path, 'wb') as f:
                f.write(file_data)

            self.logger.info(f"Arquivo de nome: {filename} na catregoria: {category} foi dalbo com sucesso para projeto: {project_name}")
            return file_path

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao salvar arquivo {filename} para projeto: {project_name} \n {e}")
            return None

    # apaga arquivo do usuario
    def delete_uploaded_file(self, file_path: Path) -> bool:
        try:
            if self.file_exists(file_path):
                if not PathManager.is_under_projects_dir(file_path):
                    self.logger.error(f"Violacao de seguranca, tentativa de apagar arquivo fora do diretorio do projeto: {file_path}")
                    return False

                file_path.unlink()
                self.logger.info(f"Arquivo: {file_path} deletado com sucesso")
            else:
                self.logger.info(f"Arquivo nao existe: {file_path}")

            return True

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao apagar arquivo: {file_path}: {e}")
            return False

    # obtem todos os arquivos de uma certa categoria em um projeto
    def get_files_by_category(self, project_name: str, category: str) -> List[Path]:
        if not PathManager.validate_project_name(project_name):
            return []

        try:
            return PathManager.get_files_in_category(project_name, category)
        except Exception as e:
            self.logger.error(f"Nao foi possivel obter arquivos da categoria: {category} no projeto: {project_name}: {e}")
            return []


    #================================================================
    # METODOS PARA PACOTE DE EXPORTACAO
    #================================================================

    # verifica se pacote de exportacao existe para um determinado projeto
    def export_package_exists(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            return False

        export_path = PathManager.get_export_package_path(project_name)
        return self.file_exists(export_path)

    # obtem pacote de exportacao de um projeto 
    def get_export_package_path(self, project_name: str) -> Optional[Path]:
        if not PathManager.validate_project_name(project_name):
            return None

        export_path = PathManager.get_export_package_path(project_name)

        if self.file_exists(export_path):
            self.logger.info(f"Pacote de exportacao nao encontrado para projeto: {project_name}")
            return export_path

        return None

    # apaga pacotes de exportacao para um determinado projeto
    def delete_export_package(self, project_name: str) -> bool:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"nome de projeto: {project_name} invalido")
            return False

        export_path = PathManager.get_export_package_path(project_name)
        success = self.delete_uploaded_file(export_path)

        if success:
            self.logger.info(f"Pacote de exportacao do projeto :{project_name} apagado com sucesso")

        return success


    #================================================================
    # METODOS DE BACKUP E MANUTENCAO 
    #================================================================

    # Cria backup de projeto
    def create_project_backup(self, project_name: str) -> Optional[Path]:
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Invalid project name: {project_name}")
            return None

        try:
            project_path = PathManager.get_project_path(project_name)
            if not self.directory_exists(project_path):
                self.logger.error(f"Project directory does not exist: {project_name}")
                return None

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{PathManager.get_safe_name(project_name)}_{timestamp}"
            backup_path = PathManager.get_backup_dir() / backup_filename

            self.ensure_directory_exists(backup_path.parent)

            shutil.copytree(project_path, backup_path)

            self.logger.info(f"Backup do projeto {project_name} criado com sucesso, caminho: {backup_path}")
            return backup_path

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao criar backup do projeto {project_name}: {e}", )
            return None


    # limpa arquivos temporarios mais velhos que um numero de horas
    def cleanup_temp_files(self, max_age_hours: int = 24) -> bool:
        try:
            temp_dir = PathManager.get_temp_dir()
            if not temp_dir.exists():
                return True

            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (max_age_hours * 60 * 60)
            cleaned_count = 0

            for item in temp_dir.iterdir():
                try:
                    if item.stat().st_mtime < cutoff_time:
                        if item.is_file():
                            item.unlink()
                            cleaned_count += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            cleaned_count += 1
                except (OSError, PermissionError) as e:
                    self.logger.warning(f"Nao foi possivel limpar arquivo {item}: {e}")

            self.logger.info(f"{cleaned_count} dados temporarios mais antigos que {max_age_hours} hours limpos com sucesso")
            return True

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao limpar dados temporarios: {e}")
            return False


    # obtem tamanho total do diretorio de um projeto (em bytes)
    def get_project_size(self, project_name: str) -> Optional[int]:
        if not PathManager.validate_project_name(project_name):
            return None

        try:
            project_path = PathManager.get_project_path(project_name)
            if not self.directory_exists(project_path):
                return None

            total_size = 0
            for item in project_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size

            return total_size

        except (OSError, PermissionError) as e:
            self.logger.error(f"Falha ao calcular tamanho do projeto {project_name}, {e}")
            return None


    #================================================================
    # UTILITY METHODS FOR MIGRATION
    #================================================================

    def verify_and_fix_file_paths(self, project_name: str, file_paths: List[str]) -> List[str]:
        """Verify file paths exist and return list of valid paths."""
        if not PathManager.validate_project_name(project_name):
            return []

        valid_paths = []
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            if self.file_exists(file_path):
                valid_paths.append(str(file_path))
            else:
                self.logger.warning(f"File not found, removing from list: {file_path}")

        return valid_paths
