import json
import shutil
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from app.core.models import ProjectState, ExtractedDataType
from app.core.path_manager import PathManager
from app.core.logger import Logger

#================================================================
# CLASSE: ProjectCRUDService
#----------------------------------------------------------------
# Implementa metodos para operacoes de CRUD com os projetos 
# e metodos relacionados. 
# 
# Como:
#   - carregar projetos
#   - salvar projetos
#   - deletar projetos
#   - listagem de projeto
#
#================================================================

class ProjectCRUDService:
    
    def __init__(self):
        self.logger = Logger(name="ProjectCRUDService")
        
        self.projects_dir = PathManager.get_project_dir()
        if not self.projects_dir.is_dir():
            self.projects_dir.mkdir(parents=True, exist_ok=True)
            self.logger.warning(f"Diretorio de projetos não existe. Diretório '{self.projects_dir}' criado")

        self.logger.info("Servico inicializado com sucesso.")
    



    #----------------------------------------------------------------
    # Cria projeto com estrutura de arquivos
    #----------------------------------------------------------------
    def create_project(self, project_name: str) -> bool:
        
        # valida nome do projeto
        if not PathManager.validate_project_name(project_name):
            self.logger.error(f"Nome de projeto invalido: {project_name}")
            return False
        
        # verifica se diretorio do projeto ja existe
        project_path = PathManager.get_project_path(project_name)
        if project_path.exists():
            self.logger.warning(f"Tentativa de criar projeto ja existente: {project_name}")
            return False
        
        try:
            # Cria subrietorios do projeto
            project_subdirs = PathManager.get_all_project_subdirs(project_name)
            for subdir_path in project_subdirs.values():
                subdir_path.mkdir(parents=True, exist_ok=True)
            
            # Cria estado original do projeto vazio
            project = ProjectState(
                name=project_name,
                path=str(project_path),
                base_files={
                    "estatuto": [],
                    "ata": [],
                    "identificacao": [],
                    "licenca": [],
                    "programacao": []
                },
                extracted_data=ExtractedDataType(),
                criteria_results={},
                current_step=1,
                created_at=datetime.now().isoformat(),
                last_modified=datetime.now().isoformat()
            )
    
            # Salva metadados do projeto
            project_json_path = PathManager.get_project_json_path(project_name)
            project.save_to_file(str(project_json_path))
            
            self.logger.info(f"Projeto '{project_name}' criado com sucesso.")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao criar projeto '{project_name}': {e}", exc_info=True)
            
            # Cleanup se tiver falha
            if project_path.exists():
                shutil.rmtree(project_path)
            return False
    
    



    #----------------------------------------------------------------
    # Carrega projeto com estrutura de arquivos
    #----------------------------------------------------------------
    def load_project(self, project_name: str) -> Optional[ProjectState]:
        
        project_json_path = PathManager.get_project_json_path(project_name)
        
        if not project_json_path.exists():
            self.logger.error(f"Project.json not found for project: {project_name}")
            return None
        
        try:
            # Load base project metadata
            project = ProjectState.load_from_file(str(project_json_path))
            
            # Load extracted data for each category
            extracted_dir = PathManager.get_project_extracted_dir(project_name)
            for category in ["estatuto", "ata", "identificacao", "licenca", "programacao"]:
                extracted_file = extracted_dir / f"{category}.json"
                
                if extracted_file.exists():
                    with open(extracted_file, 'r', encoding='utf-8') as f:
                        extracted_data = json.load(f)
                        setattr(project.extracted_data, category, extracted_data)
            
            # Load criteria results if they exist
            criteria_file = PathManager.get_criteria_results_path(project_name)
            if criteria_file.exists():
                with open(criteria_file, 'r', encoding='utf-8') as f:
                    project.criteria_results = json.load(f)
            
            return project
            
        except Exception as e:
            self.logger.error(f"Error loading project '{project_name}': {e}", exc_info=True)
            return None
    
    


    #----------------------------------------------------------------
    # Salva Projeto e dados separadamente
    #----------------------------------------------------------------
    def save_project(self, project: ProjectState) -> bool:
        

        try:
            # atualiza timestamp
            project.last_modified = datetime.now().isoformat()
            
            # cria metadados do projeto
            metadata_project = ProjectState(
                name=project.name,
                path=project.path,
                base_files=project.base_files,
                extracted_data=ExtractedDataType(),
                criteria_results={},
                current_step=project.current_step,
                created_at=project.created_at,
                last_modified=project.last_modified
            )
            
            # Salva metadados do projeto
            project_json_path = PathManager.get_project_json_path(project.name)
            metadata_project.save_to_file(str(project_json_path))
            
            # Save extracted data separately by category
            extracted_dir = PathManager.get_project_extracted_dir(project.name)
            for category in ["estatuto", "ata", "identificacao", "licenca", "programacao"]:
                extracted_data = getattr(project.extracted_data, category, None)
                
                if extracted_data:
                    extracted_file = extracted_dir / f"{category}.json"
                    with open(extracted_file, 'w', encoding='utf-8') as f:
                        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            # Save criteria results if they exist
            if project.criteria_results:
                criteria_file = PathManager.get_criteria_results_path(project.name)
                criteria_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(criteria_file, 'w', encoding='utf-8') as f:
                    json.dump(project.criteria_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Projeto '{project.name}' salvo com sucesso.")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar projeto '{project.name}': {e}", exc_info=True)
            return False
    
    





    #----------------------------------------------------------------
    # Deleta projeto e todos os arquivos
    #----------------------------------------------------------------
    def delete_project(self, project_name: str) -> bool:
        
        project_path = PathManager.get_project_path(project_name)
        
        try:
            if project_path.exists():
                shutil.rmtree(project_path)
                self.logger.info(f"Projeto '{project_name}' deletado com sucesso.")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao deletar projeto '{project_name}': {e}", exc_info=True)
            return False
    







    #----------------------------------------------------------------
    # Lista projetos
    #----------------------------------------------------------------
    def list_projects(self) -> List[str]:
        
        projects = []
        self.projects_dir = PathManager.get_project_dir()
        
        if not self.projects_dir.exists():
            return projects
        
        try:
            for item in self.projects_dir.iterdir():
                if item.is_dir():
                    # Check if it has a valid project structure
                    project_json = item / "project.json"
                    if project_json.exists():
                        # Extract project name from directory name
                        project_name = PathManager.extract_project_name_from_path(item)
                        projects.append(project_name)
            
            return projects
            
        except Exception as e:
            self.logger.error(f"Error listing projects: {e}", exc_info=True)
            return []
    
    







    #----------------------------------------------------------------
    # Verifica se projeto existe
    #----------------------------------------------------------------
    def project_exists(self, project_name: str) -> bool:
        return PathManager.is_valid_project_structure(project_name)
    








    #----------------------------------------------------------------
    # valida estrutura do projeto
    #----------------------------------------------------------------
    def validate_project_structure(self, project_name: str) -> bool:
        if not self.project_exists(project_name):
            return False
        
        try:
            # Check all required subdirectories exist
            project_subdirs = PathManager.get_all_project_subdirs(project_name)
            
            for subdir_name, subdir_path in project_subdirs.items():
                if subdir_name != 'base' and not subdir_path.exists():
                    self.logger.warning(f"Criando subdiretorio '{subdir_name}' no projeto '{project_name}'")
                    # Create missing directory
                    subdir_path.mkdir(parents=True, exist_ok=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar estrutura do projeto '{project_name}': {e}")
            return False
    
    




    #----------------------------------------------------------------
    # Obtem metadados de um projeto
    #----------------------------------------------------------------
    def get_project_metadata(self, project_name: str) -> Optional[Dict]:
        
        project_json_path = PathManager.get_project_json_path(project_name)
        
        if not project_json_path.exists():
            return None
        
        try:
            with open(project_json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar metados do projeto '{project_name}': {e}")
            return None