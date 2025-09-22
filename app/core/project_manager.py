from typing import Dict, List, Optional

from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService
from app.core.project_file_manager import ProjectFileManager
from app.core.project_data_service import ProjectDataService
from app.core.project_workflow_orchestrator import ProjectWorkflowOrchestrator
from app.core.document_package_service import DocumentPackageService
from app.core.project_configuration_service import ProjectConfigurationService
from app.core.models import ProjectState


class ProjectManager:
    def __init__(
        self,
        crud_service: ProjectCRUDService,
        file_manager: ProjectFileManager,
        data_service: ProjectDataService,
        workflow: ProjectWorkflowOrchestrator,
        package_service: DocumentPackageService,
        config_service: ProjectConfigurationService,
    ):
        self.logger = Logger("ProjectManager")
        self.crud = crud_service
        self.files = file_manager
        self.data = data_service
        self.workflow = workflow
        self.packages = package_service
        self.config = config_service
        self.logger.info("ProjectManager initialized successfully")

    # -----------------------
    # Project CRUD Methods
    # -----------------------
    def list_projects(self) -> List[str]:
        return self.crud.list_projects()

    def create_project(self, name: str, description: str = "") -> ProjectState:
        return self.crud.create_project(name, description)

    def load_project(self, project_name: str) -> Optional[ProjectState]:
        return self.crud.load_project(project_name)

    def save_project(self, project: ProjectState) -> bool:
        return self.crud.save_project(project)

    def delete_project(self, project_name: str) -> bool:
        return self.crud.delete_project(project_name)

    # -----------------------
    # File Management
    # -----------------------
    def add_file(self, project_name: str, file_path: str, category: str) -> bool:
        return self.files.add_pdf_file(project_name, file_path, category)

    def remove_file(self, project_name: str, file_path: str) -> bool:
        return self.files.remove_pdf_file(project_name, file_path)

    def list_files(self, project_name: str) -> Dict[str, List[str]]:
        return self.files.get_all_files(project_name)

    # -----------------------
    # Data & Extraction
    # -----------------------
    def has_extracted_text(self, project_name: str) -> bool:
        return self.data.has_extracted_text(project_name)

    def run_extraction(self, project_name: str, category: str) -> Dict:
        return self.workflow.run_extraction_for_category(project_name, category)

    def load_structured_extraction(self, project_name: str, category: str) -> Optional[Dict]:
        return self.data.load_structured_extraction(project_name, category)

    def save_structured_extraction(self, project_name: str, category: str, data: Dict) -> bool:
        return self.data.save_structured_extraction(project_name, category, data)

    def load_extracted_text(self, project_name: str, category: str) -> Optional[str]:
        return self.data.load_extracted_text(project_name, category)

    def save_edited_text(self, project_name: str, category: str, text: str) -> bool:
        return self.data.save_edited_text(project_name, category, text)

    def get_consolidated_text(self, project_name: str) -> str:
        return self.data.get_consolidated_text(project_name)

    def get_pending_information(self, project_name: str) -> Dict[str, List[str]]:
        return self.data.get_pending_information(project_name)

    def update_extraction_field(self, project_name: str, category: str, field: str, value: any) -> bool:
        return self.data.update_extraction_field(project_name, category, field, value)

    def mark_field_complete(self, project_name: str, category: str, field: str) -> bool:
        return self.data.mark_field_as_complete(project_name, category, field)

    def get_director_list(self, project_name: str) -> List[Dict]:
        return self.data.get_director_list(project_name)

    def update_director_list(self, project_name: str, directors: List[Dict]) -> bool:
        return self.data.update_director_list(project_name, directors)

    # -----------------------
    # Criteria & Verification
    # -----------------------
    def execute_criteria_verification(self, project_name: str) -> Dict:
        return self.workflow.execute_criteria_verification(project_name)

    def execute_single_criterion(self, project_name: str, criterion_id: str) -> Dict:
        return self.workflow.execute_single_criterion_verification(project_name, criterion_id)

    def update_manual_override(self, project_name: str, criterion_id: str, status: str, reason: str) -> bool:
        return self.workflow.update_manual_override(project_name, criterion_id, status, reason)

    # -----------------------
    # Package & Export
    # -----------------------
    def prepare_export(self, project_name: str) -> bool:
        return self.workflow.prepare_project_for_export(project_name)

    def export_package(self, project_name: str) -> str:
        return self.workflow.export_project_package(project_name)

    def get_export_path(self, project_name: str) -> str:
        return self.packages.get_exported_package_path(project_name)

    def generate_draft(self, project_name: str) -> str:
        return self.packages.generate_draft_for_signature(project_name)

    def assemble_package(self, project_name: str) -> str:
        return self.packages.assemble_final_package(project_name)

    def delete_exports(self, project_name: str) -> bool:
        return self.packages.delete_exported_package(project_name)

    # -----------------------
    # Configuration
    # -----------------------
    def get_report_config(self, project_name: str) -> Dict:
        return self.config.get_report_configuration(project_name)

    def save_report_config(self, project_name: str, config: Dict) -> bool:
        return self.config.save_report_configuration(project_name, config)
