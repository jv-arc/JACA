import json
from typing import List, Dict, Optional

from app.core.path_manager import PathManager
from app.core.models import ProjectState, ExtractedDataType
from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService
from app.core.data_manager import ExtractedDataManager
from app.core.criteria_manager import CriteriaManager
from app.core.export_manager import ExportManager
from app.core.report_config_manager import ReportConfigManager




#================================================================
# CLASS: ProjectWorkflowOrchestrator
#----------------------------------------------------------------
# Implementa workflows de alto nivel: extracao, verificacao,
# extracao secundaria e exportacao
#================================================================




class ProjectWorkflowOrchestrator:

    def __init__(
        self,
        crud_service: ProjectCRUDService,
        extraction_manager: ExtractedDataManager,
        criteria_manager: CriteriaManager,
        export_manager: ExportManager,
        report_config_manager: ReportConfigManager
    ):
        self.logger = Logger("ProjectWorkflowOrchestrator")
        self.crud_service = crud_service
        self.extraction_manager = extraction_manager
        self.criteria_manager = criteria_manager
        self.export_manager = export_manager
        self.report_config_manager = report_config_manager
        self.logger.info("Serviço de workflow inicializado com sucesso")








    #----------------------------------------------------------------
    # Orquestra extração de dados por categoria via AI
    #----------------------------------------------------------------
    def run_extraction_for_category(self, project_name: str, category: str) -> Optional[Dict]:
        self.logger.info(f"Iniciando extração para '{category}' em '{project_name}'.")
        project = self.crud_service.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado.")
            return None

        # Executa extração estruturada
        result = self.extraction_manager.extract_structured(
            project_name, category, project.files.get(category, [])
        )
        if result:
            # Salva no disco
            self.extraction_manager.save_structured_extraction(
                project_name, category,
                result.get("content_fields", {}), result.get("ignored_fields", {})
            )
            self.logger.info(f"Extração para '{category}' concluída.")
        return result











    #----------------------------------------------------------------
    # Orquestra extração secundária (campos específicos do texto bruto)
    #----------------------------------------------------------------
    def run_secondary_extraction(self, project_name: str, fields: List[str]) -> Dict:
        self.logger.info(f"Iniciando extração secundária em '{project_name}' para campos {fields}.")
        raw_text = ""
        for category in fields:
            part = self.extraction_manager.load_consolidated_text(project_name, category) or ""
            raw_text += part + "\n\n"
        return self.extraction_manager.extract_fields(project_name, raw_text, fields)








    #----------------------------------------------------------------
    # Executa todas as verificações de critérios para um projeto
    #----------------------------------------------------------------
    def execute_criteria_verification(self, project_name: str) -> Dict:
        self.logger.info(f"Iniciando verificação de critérios para '{project_name}'.")
        project = self.crud_service.load_project(project_name)
        categories = self.criteria_manager.list_categories()
        all_results: Dict[str, Dict] = {}

        for category in categories:
            files = project.files.get(category, [])
            results = self.criteria_manager.verify_all(
                project_name, category, files
            )
            all_results[category] = results

        # Salva resultados em JSON
        criteria_path = PathManager.get_criteria_results_path(project_name)
        with open(criteria_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        self.logger.info("Verificação de critérios concluída.")
        return all_results









    #----------------------------------------------------------------
    # Executa verificação de um único critério
    #----------------------------------------------------------------
    def execute_single_criterion_verification(
        self, project_name: str, category: str, criterion_id: str
    ) -> Dict:
        self.logger.info(
            f"Verificando critério '{criterion_id}' em '{category}' para '{project_name}'."
        )
        project = self.crud_service.load_project(project_name)
        file_list = project.files.get(category, [])
        result = self.criteria_manager.verify_single(
            project_name, category, criterion_id, file_list
        )
        self.logger.info(f"Verificação de critério '{criterion_id}' concluída.")
        return result










    #----------------------------------------------------------------
    # Atualiza manualmente o status de um critério
    #----------------------------------------------------------------
    def update_manual_override(
        self, project_name: str, category: str, criterion_id: str, status: str, reason: str
    ) -> bool:
        self.logger.info(f"Atualizando override manual para '{criterion_id}'.")
        updated = self.criteria_manager.override(
            project_name, category, criterion_id, status, reason
        )
        if updated:
            self.logger.info("Override manual aplicado com sucesso.")
        return updated










    #----------------------------------------------------------------
    # Exibe resultados de critérios existentes
    #----------------------------------------------------------------
    def get_all_criteria(self, project_name: str) -> Dict:
        criteria_path = PathManager.get_criteria_results_path(project_name)
        try:
            with open(criteria_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao ler resultados de critérios: {e}")
            return {}









    #----------------------------------------------------------------
    # Orquestra exportação completa do projeto
    #----------------------------------------------------------------
    def export_project_package(self, project_name: str) -> Optional[str]:
        self.logger.info(f"Iniciando exportação para '{project_name}'.")
        project = self.crud_service.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado.")
            return None

        # Gera rascunho
        draft_path = self.export_manager.generate_draft(
            project_name, project, self.report_config_manager.load_config()
        )

        # Combina assinatura e anexos
        final_path = self.export_manager.assemble_package(
            project_name, draft_path, project.files.get("signed", [])
        )
        self.logger.info(f"Exportação concluída em '{final_path}'.")
        return final_path








    #----------------------------------------------------------------
    # Valida conexão com a API externa (p.ex. Gemini)
    #----------------------------------------------------------------
    def test_api_connection(self) -> bool:
        self.logger.info("Testando conexão com API externa.")
        return self.extraction_manager.test_connection()






    #----------------------------------------------------------------
    # Valida se o projeto está pronto para exportação
    #----------------------------------------------------------------
    def validate_project_readiness(self, project_name: str) -> Dict[str, bool]:
        self.logger.info(f"Validando prontidão de '{project_name}'.")
        readiness: Dict[str, bool] = {}
        # Exemplo: verifica que ao menos uma extração e um critério foram executados
        readiness["extracted"] = self.crud_service.load_project(project_name).extracted_data is not None
        readiness["criteria"] = bool(self.get_all_criteria(project_name))
        return readiness
