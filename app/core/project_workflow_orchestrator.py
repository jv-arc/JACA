import json
from typing import List, Dict, Optional

from app.core.path_manager import PathManager
from app.core.project_crud_service import ProjectCRUDService
from app.core.data_manager import ExtractedDataManager
from app.core.criteria_manager import CriteriaManager
from app.core.export_manager import ExportManager
from app.core.report_config_manager import ReportConfigManager
from app.core.project_data_service import ProjectDataService
from app.core.prompt_manager import PromptManager
from app.core.ai_client import GeminiClient
from app.core.logger import Logger


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

        self.logger = Logger("ProjectWorkflowOrchestrator")
        self.prompt = PromptManager()
        self.crud = ProjectCRUDService()
        self.export = ExportManager()
        self.r_conf = ReportConfigManager()
        self.path = PathManager
        self.ai = gemini_client

        self.logger.info("Serviço de workflow inicializado com sucesso")








    #----------------------------------------------------------------
    # Orquestra extração de dados por categoria via AI
    #----------------------------------------------------------------
    def run_extraction_for_category(self, project_name: str, category: str) -> Optional[Dict]:
        self.logger.info(f"Iniciando extração para '{category}' em '{project_name}'.")
        project = self.crud.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado.")
            return None

        file_paths = self.path.get_files_in_category(project_name, category)
        if not file_paths:
            self.logger.warning(f"Nenhum arquivo para extrair na categoria '{category}'.")

        # Executa extração estruturada
        extracted_data = self.extract.run_extraction(file_paths, category)
        if extracted_data == None:
            self.logger.error(f"O processo de extração para '{category}' não retornou dados.")
            return None

        self.logger.info(f"Extração para '{category}' concluída.")
        if  self.data.save_structured_extraction(project_name, category, extracted_data):
            return extracted_data
            







    #----------------------------------------------------------------
    # Orquestra extração secundária campos do texto salvo pelo usuario
    #----------------------------------------------------------------
    def run_secondary_extraction(self, project_name: str, category: str) -> bool:
        self.logger.info(f"Iniciando extração secundária em '{project_name}' para categoria '{category}'.")
        
        try:
            self.path.validate_project_name(project_name)
        except Exception as e:
            self.logger.error(f"Falha em validar projeto de nome: {project_name} \n\n {e}")
            return False

        consolidated_text = self.data.load_consolidated_text(project_name, category)
        if not consolidated_text:
            self.logger.warning(f"Texto consolidado para '{category}' não disponível. Pulando extração secundária.")
            return True            
        prompt = None

        if category == 'ata':
            prompt = self.prompt.get_ata_director_extraction_prompt()
        elif category == 'identificacao':
            prompt = self.prompt.get_id_document_extraction_prommpt()
        else:
            report_config = self.get_report_configuration()
            fields_to_extract = []
            for table in report_config.get('tables', []):
                for field in table.get('fields', []):
                    data_key = field.get('data_key', '')
                    if field.get('source') == 'extracted' and data_key.startswith(category):
                        fields_to_extract.append(data_key.split('.')[-1])

            if not fields_to_extract:
                self.logger.info(f"Nenhum campo secundário a ser extraído para a categoria '{category}'.")
                return True
            prompt = self.prompt.get_secondary_extraction_prompt(fields_to_extract)

        # Executa a chamada à IA
        full_prompt = prompt + "\n\n--- TEXTO PARA ANÁLISE ---\n" + consolidated_text
        extracted_fields = self.gemini_client.generate_json_from_prompt(
            full_prompt, self.gemini_client.settings.extraction_model
        )

        if not extracted_fields:
            self.logger.error(f"A extração secundária para '{category}' não retornou dados.")
            return False

        # Atualiza os 'content_fields' com os novos dados e salva o projeto

        doc_data_dict = self.data.get_extracted_data(project_name, category)
        if 'content_fields' not in doc_data_dict or doc_data_dict['content_fields'] is None:
            doc_data_dict['content_fields'] = {}

        doc_data_dict['content_fields'].update(extracted_fields)
        setattr(project_data.extracted_data, category, doc_data_dict)

        return self.save_project(project_data)





    #----------------------------------------------------------------
    # Executa todas as verificações de critérios para um projeto
    #----------------------------------------------------------------
    def execute_criteria_verification(self, project_name: str) -> Dict:
        self.logger.info(f"Iniciando verificação de critérios para '{project_name}'.")
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

        self.logger.info("Verificação de critérios concluída.")
        return all_results









    #----------------------------------------------------------------
    # Executa verificação de um único critério
    #----------------------------------------------------------------
    def execute_single_criterion_verification(self, project_name: str, criterion_id: str) -> Dict|None:
        
        self.logger.info(f"Verificando critério '{criterion_id}' para '{project_name}'.")

        file_list = self.get_all_criteria(project_name)
        criterion_to_check = next((c for c in file_list if c['id']== criterion_id), None)

        if not criterion_to_check:
            self.logger.error(f"Critério com ID '{criterion_id}' não encontrado na base de dados.")
            return None
        
        self.projectfil

        new_result = self.criteria._perform_single_check(criterion_to_check, project_data)
        result = self.criteria.verify_single(
            project_name, category, criterion_id, file_list
        )
        self.logger.info(f"Verificação de critério '{criterion_id}' concluída.")
        return result










    #----------------------------------------------------------------
    # Atualiza manualmente o status de um critério
    #----------------------------------------------------------------
    def update_manual_override(self, project_name: str, category: str, criterion_id: str, status: str, reason: str) -> bool:
        self.logger.info(f"Atualizando override manual para '{criterion_id}'.")
        updated = self.criteria.override(
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
        project = self.crud.load_project(project_name)
        if not project:
            self.logger.error("Projeto não encontrado.")
            return None

        # Gera rascunho
        draft_path = self.export.generate_draft(
            project_name, project, self.r_conf.load_config()
        )

        # Combina assinatura e anexos
        final_path = self.export.assemble_package(
            project_name, draft_path, project.files.get("signed", [])
        )
        self.logger.info(f"Exportação concluída em '{final_path}'.")
        return final_path








    #----------------------------------------------------------------
    # Valida conexão com a API externa (p.ex. Gemini)
    #----------------------------------------------------------------
    def test_api_connection(self) -> bool:
        self.logger.info("Testando conexão com API externa.")
        return self.ai.test_connection()






    #----------------------------------------------------------------
    # Valida se o projeto está pronto para exportação
    #----------------------------------------------------------------
    def validate_project_readiness(self, project_name: str) -> Dict[str, bool]:
        self.logger.info(f"Validando prontidão de '{project_name}'.")
        readiness: Dict[str, bool] = {}
        # Exemplo: verifica que ao menos uma extração e um critério foram executados
        readiness["extracted"] = self.crud.load_project(project_name).extracted_data is not None
        readiness["criteria"] = bool(self.get_all_criteria(project_name))
        return readiness
