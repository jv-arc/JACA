import json
from typing import List, Dict, Optional

from app.core.path_manager import PathManager
from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService
from app.core.data_manager import ExtractedDataManager
from app.core.criteria_manager import CriteriaManager
from app.core.export_manager import ExportManager
from app.core.report_config_manager import ReportConfigManager
from app.core.project_data_service import ProjectDataService
from app.core.ai_client import GeminiClient



#================================================================
# CLASS: ProjectWorkflowOrchestrator
#----------------------------------------------------------------
# Implementa workflows de alto nivel: extracao, verificacao,
# extracao secundaria e exportacao
#================================================================


class ProjectWorkflowOrchestrator:

    def __init__(self, gemini_client: GeminiClient):
        self.extract = ExtractedDataManager(gemini_client=gemini_client)
        self.criteria = CriteriaManager(gemini_client=gemini_client)
        self.data = ProjectDataService(gemini_client=gemini_client)

        self.lgr = Logger("ProjectWorkflowOrchestrator")

        self.crud = ProjectCRUDService()
        self.export = ExportManager()
        self.r_conf = ReportConfigManager()
        self.path = PathManager
        self.ai = gemini_client

        self.lgr.info("Serviço de workflow inicializado com sucesso")








    #----------------------------------------------------------------
    # Orquestra extração de dados por categoria via AI
    #----------------------------------------------------------------
    def run_extraction_for_category(self, project_name: str, category: str) -> bool:
        self.lgr.info(f"Iniciando extração para '{category}' em '{project_name}'.")
        project = self.crud.load_project(project_name)
        if not project:
            self.lgr.error("Projeto não encontrado.")
            return False

        file_paths = self.path.get_files_in_category(project_name, category)
        if not file_paths:
            self.lgr.warning(f"Nenhum arquivo para extrair na categoria '{category}'.")

        # Executa extração estruturada
        extracted_data = self.extract.run_extraction(file_paths, category)
        if extracted_data == None:
            self.lgr.error(f"O processo de extração para '{category}' não retornou dados.")
            return False

        self.lgr.info(f"Extração para '{category}' concluída.")
        return self.data.save_structured_extraction(project_name, category, extracted_data)
            











    #----------------------------------------------------------------
    # Orquestra extração secundária (campos específicos do texto bruto)
    #----------------------------------------------------------------
    def run_secondary_extraction(self, project_name: str, category: List[str]) -> Dict:
        self.lgr.info(f"Iniciando extração secundária em '{project_name}' para categoria '{category}'.")
        raw_text = ""
        for category in fields:
            part = self.extract.load_consolidated_text(project_name, category) or ""
            raw_text += part + "\n\n"
        return self.extract.extract_fields(project_name, raw_text, fields)








    #----------------------------------------------------------------
    # Executa todas as verificações de critérios para um projeto
    #----------------------------------------------------------------
    def execute_criteria_verification(self, project_name: str) -> Dict:
        self.lgr.info(f"Iniciando verificação de critérios para '{project_name}'.")
        project = self.crud.load_project(project_name)
        categories = self.criteria.list_categories()
        all_results: Dict[str, Dict] = {}

        for category in categories:
            files = project.files.get(category, [])
            results = self.criteria.verify_all(
                project_name, category, files
            )
            all_results[category] = results

        # Salva resultados em JSON
        criteria_path = PathManager.get_criteria_results_path(project_name)
        with open(criteria_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        self.lgr.info("Verificação de critérios concluída.")
        return all_results









    #----------------------------------------------------------------
    # Executa verificação de um único critério
    #----------------------------------------------------------------
    def execute_single_criterion_verification(self, project_name: str, criterion_id: str) -> Dict|None:
        
        self.lgr.info(f"Verificando critério '{criterion_id}' para '{project_name}'.")

        file_list = self.get_all_criteria(project_name)
        criterion_to_check = next((c for c in file_list if c['id']== criterion_id), None)

        if not criterion_to_check:
            self.lgr.error(f"Critério com ID '{criterion_id}' não encontrado na base de dados.")
            return None
        
        self.projectfil

        new_result = self.criteria._perform_single_check(criterion_to_check, project_data)
        result = self.criteria.verify_single(
            project_name, category, criterion_id, file_list
        )
        self.lgr.info(f"Verificação de critério '{criterion_id}' concluída.")
        return result










    #----------------------------------------------------------------
    # Atualiza manualmente o status de um critério
    #----------------------------------------------------------------
    def update_manual_override(self, project_name: str, category: str, criterion_id: str, status: str, reason: str) -> bool:
        self.lgr.info(f"Atualizando override manual para '{criterion_id}'.")
        updated = self.criteria.override(
            project_name, category, criterion_id, status, reason
        )
        if updated:
            self.lgr.info("Override manual aplicado com sucesso.")
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
            self.lgr.error(f"Erro ao ler resultados de critérios: {e}")
            return {}









    #----------------------------------------------------------------
    # Orquestra exportação completa do projeto
    #----------------------------------------------------------------
    def export_project_package(self, project_name: str) -> Optional[str]:
        self.lgr.info(f"Iniciando exportação para '{project_name}'.")
        project = self.crud.load_project(project_name)
        if not project:
            self.lgr.error("Projeto não encontrado.")
            return None

        # Gera rascunho
        draft_path = self.export.generate_draft(
            project_name, project, self.r_conf.load_config()
        )

        # Combina assinatura e anexos
        final_path = self.export.assemble_package(
            project_name, draft_path, project.files.get("signed", [])
        )
        self.lgr.info(f"Exportação concluída em '{final_path}'.")
        return final_path








    #----------------------------------------------------------------
    # Valida conexão com a API externa (p.ex. Gemini)
    #----------------------------------------------------------------
    def test_api_connection(self) -> bool:
        self.lgr.info("Testando conexão com API externa.")
        return self.ai.test_connection()






    #----------------------------------------------------------------
    # Valida se o projeto está pronto para exportação
    #----------------------------------------------------------------
    def validate_project_readiness(self, project_name: str) -> Dict[str, bool]:
        self.lgr.info(f"Validando prontidão de '{project_name}'.")
        readiness: Dict[str, bool] = {}
        # Exemplo: verifica que ao menos uma extração e um critério foram executados
        readiness["extracted"] = self.crud.load_project(project_name).extracted_data is not None
        readiness["criteria"] = bool(self.get_all_criteria(project_name))
        return readiness
