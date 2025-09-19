import os
import json
import shutil
from datetime import datetime
from typing import List, Optional, Dict


from app.core.report_config_manager import ReportConfigManager
from app.core.models import ProjectState, ExtractedDataType
from app.core.data_manager import ExtractedDataManager
from app.core.criteria_manager import CriteriaManager
from app.core.export_manager import ExportManager
from app.core.logger import Logger


class ProjectManager:
    """
    Orquestrador principal - gerencia projetos, extração IA, verificação de critérios e exportação.
    """

    def __init__(
        self,
        extraction_manager: ExtractedDataManager,
        reportconfig_manager: ReportConfigManager,
        criteria_manager: CriteriaManager,
        export_manager: ExportManager,
        logger: Logger,
        projects_dir: str
    ):
        self.extraction_manager = extraction_manager
        self.criteria_manager = criteria_manager
        self.export_manager = export_manager
        self.reportconfig_manager = reportconfig_manager
        self.logger = logger
        self.projects_dir = projects_dir
        os.makedirs(self.projects_dir, exist_ok=True)
        self.logger.info("ProjectManager inicializado com todas as dependências.")

    # -------------------
    # Métodos de Projeto
    # -------------------

    def project_path(self, project_name: str) -> str:
        return os.path.join(self.projects_dir, project_name)

    def project_export_dir(self, project_name: str) -> str:
        path = os.path.join(self.project_path(project_name), "exports")
        os.makedirs(path, exist_ok=True)
        return path

    def project_criteria_dir(self, project_name: str) -> str:
        path = os.path.join(self.project_path(project_name), "criteria")
        os.makedirs(path, exist_ok=True)
        return path

    def project_extracted_dir(self, project_name: str) -> str:
        path = os.path.join(self.project_path(project_name), "extracted")
        os.makedirs(path, exist_ok=True)
        return path

    def list_projects(self) -> List[str]:
        try:
            return [d for d in os.listdir(self.projects_dir)
                    if os.path.isdir(os.path.join(self.projects_dir, d))]
        except Exception:
            return []

    def load_project(self, project_name: str) -> Optional[ProjectState]:
        path = os.path.join(self.project_path(project_name), f"{project_name}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ProjectState(**data)
        except Exception as e:
            self.logger.error(f"Falha ao carregar projeto {project_name}: {e}")
            return None

    def save_project(self, project: ProjectState) -> bool:
        path = os.path.join(self.project_path(project.name), f"{project.name}.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(project.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Falha ao salvar projeto {project.name}: {e}", exc_info=True)
            return False

    # -------------------------------
    # Extração de Dados por Categoria
    # -------------------------------

    def run_extraction_for_category(self, project_name: str, category: str) -> bool:
        self.logger.info(f"Orquestrando extração para {project_name}, categoria {category}.")
        filepaths = self.get_files_by_category(project_name, category)
        if not filepaths:
            self.logger.warning(f"Nenhum arquivo para extrair na categoria {category}.")
            return False
        extracted = self.extraction_manager.extract_data_from_files(filepaths, category)
        if not extracted:
            self.logger.error(f"O processo de extração para {category} não retornou dados.")
            return False
        return self._save_structured_data(project_name, category, extracted)

    def _save_structured_data(
        self,
        project_name: str,
        category: str,
        extracted_data: ExtractedDataType
    ) -> bool:
        try:
            consolidated = self.extraction_manager.consolidate_content_fields(
                extracted_data.content_fields,
                workflow_used=category
            )
            output = {
                **extracted_data.content_fields,
                "consolidated_text": consolidated,
                "last_modified": datetime.now().isoformat()
            }
            path = os.path.join(
                self.project_extracted_dir(project_name),
                f"{category}.json"
            )
            with open(path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Dados estruturados para {category} salvos com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Falha ao salvar dados estruturados para {category}: {e}", exc_info=True)
            return False

    # --------------------------
    # Verificação de Critérios
    # --------------------------

    def execute_criteria_verification(self, project_name: str) -> bool:
        self.logger.info(f"Iniciando orquestração da verificação de critérios para {project_name}.")
        project_data = self.load_project(project_name)
        if not project_data:
            self.logger.error("Não foi possível carregar o projeto para verificação.")
            return False

        results = self.criteria_manager.run_all_checks(project_data)
        # Mesmo que vazio, salvamos
        return self._update_criteria_results(project_name, results)

    def execute_single_criterion_verification(self, project_name: str, criterion_id: str) -> bool:
        self.logger.info(f"Iniciando verificação do critério {criterion_id} para {project_name}.")
        project_data = self.load_project(project_name)
        if not project_data:
            self.logger.error(f"Não foi possível carregar o projeto {project_name}.")
            return False

        criterion = next(
            (c for c in self.get_all_criteria() if c["id"] == criterion_id),
            None
        )
        if not criterion:
            self.logger.error(f"Critério {criterion_id} não encontrado.")
            return False

        new_result = self.criteria_manager.perform_single_check(criterion, project_data)
        current = project_data.criteria_results or []
        updated = [r for r in current if r.get("id") != criterion_id] + [new_result]
        return self._update_criteria_results(project_name, updated)

    def get_all_criteria(self) -> List[Dict]:
        return self.criteria_manager.criteria

    def _update_criteria_results(self, project_name: str, results: List[Dict]) -> bool:
        self.logger.info(f"Salvando {len(results)} resultados de critérios para {project_name}.")
        path = os.path.join(self.project_criteria_dir(project_name), "results.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Erro de IO ao salvar results.json: {e}")
            return False

        project = self.load_project(project_name)
        if not project:
            return False
        project.criteria_results = results
        project.current_step = max(project.current_step, 4)
        return self.save_project(project)

    def updatemanualoverride(
        self,
        project_name: str,
        criterion_id: str,
        new_status: str,
        new_justification: str
    ) -> bool:
        self.logger.info(f"Aplicando override manual para {criterion_id} em {project_name}.")
        project = self.load_project(project_name)
        if not project or not project.criteria_results:
            self.logger.error("Não há resultados para fazer override.")
            return False

        found = False
        for r in project.criteria_results:
            if r.get("id") == criterion_id:
                r["status"] = new_status
                r["justification"] = new_justification
                r["overridden_at"] = datetime.now().isoformat()
                found = True
                break
        if not found:
            self.logger.error(f"Resultado {criterion_id} não encontrado.")
            return False

        return self.save_project(project)

    # --------------------------
    # Exportação de Pacotes
    # --------------------------

    def get_exported_package_path(self, project_name: str) -> Optional[str]:
        export_dir = self.project_export_dir(project_name)
        filename = f"REQUISICAO_{project_name}.pdf"
        full = os.path.join(export_dir, filename)
        if os.path.exists(full):
            self.logger.info(f"Pacote existente em {full}.")
            return full
        return None

    def delete_exported_package(self, project_name: str) -> bool:
        path = self.get_exported_package_path(project_name)
        if not path:
            return False
        try:
            os.remove(path)
            return True
        except Exception as e:
            self.logger.error(f"Falha ao apagar {path}: {e}", exc_info=True)
            return False

    def savereportconfiguration(self, new_config: Dict) -> bool:
        self.logger.info("Salvando nova configuração de relatório.")
        return self.reportconfig_manager.save_config(new_config)

    def export_project_package(self, project_name: str, user_overrides: Dict) -> Optional[str]:
        self.logger.info(f"Iniciando exportação para {project_name}.")
        project = self.load_project(project_name)
        if not project:
            self.logger.error("Não foi possível carregar o projeto para exportação.")
            return None

        try:
            path = self.export_manager.generate_full_package(
                project_data=project,
                user_overrides=user_overrides,
                export_dir=self.project_export_dir(project_name)
            )
            return path
        except Exception as e:
            self.logger.error(f"Exportação falhou: {e}", exc_info=True)
            return None

    def get_files_by_category(self, project_name: str, category: str) -> List[str]:
        folder = os.path.join(self.project_path(project_name), category)
        if not os.path.isdir(folder):
            return []
        return [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
