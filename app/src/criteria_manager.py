import json
from typing import List, Dict, Optional

from src.ai_client import GeminiClient
from src.prompt_manager import PromptManager
from src.logger import Logger
from src.models import ProjectState

class CriteriaManager:
    """
    Responsável por carregar critérios de um arquivo JSON e executar a verificação de conformidade em dados de um projeto.
    """

    def __init__(self,
                 gemini_client: GeminiClient,
                 prompt_manager: PromptManager,
                 logger: Logger,
                 criteria_db_path: str = "src/criteria/criteriadatabase.json"):
        """
        Inicializa o CriteriaManager.

        Args:
            gemini_client (GeminiClient): Cliente para a API Gemini.
            prompt_manager (PromptManager): Gerenciador de prompts.
            logger (Logger): Instância do logger.
            criteria_db_path (str): Caminho para o banco de dados de critérios em JSON.
        """
        self.gemini_client = gemini_client
        self.prompt_manager = prompt_manager
        self.logger = logger
        self.criteria = self.load_criteria(criteria_db_path)

    def load_criteria(self, db_path: str) -> List[Dict]:
        """
        Carrega as regras do arquivo JSON.

        Args:
            db_path (str): Caminho para o arquivo de critérios.

        Returns:
            List[Dict]: Lista de critérios carregados.
        """
        self.logger.info(f"Carregando critérios de {db_path}...")
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                criteria = json.load(f)
            self.logger.info(f"{len(criteria)} critérios carregados com sucesso.")
            return criteria
        except FileNotFoundError:
            self.logger.error(f"Arquivo de critérios não encontrado em {db_path}.")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar o JSON de critérios em {db_path}: {e}")
            return []

    def gather_context_text(self,
                            criterion: Dict,
                            project_data: ProjectState) -> Optional[str]:
        """
        Coleta e formata o texto relevante dos documentos do projeto.

        Args:
            criterion (Dict): Critério a ser verificado.
            project_data (ProjectState): Estado do projeto com dados extraídos.

        Returns:
            Optional[str]: Texto concatenado dos campos relevantes, ou None se não houver dados.
        """
        context_parts = []
        sourcedocs = criterion.get("sourcedocuments", [])
        relevant_fields = criterion.get("relevantfields", {})

        for doc_name in sourcedocs:
            doc_data = project_data.extracteddata.get(doc_name)
            if not doc_data:
                self.logger.warning(f"Dados para o documento {doc_name} não encontrados no projeto para o critério {criterion.get('id')}.")
                continue

            fields = relevant_fields.get(doc_name, [])
            for field_name in fields:
                field_text = None

                if hasattr(doc_data, "contentfields"):
                    field_text = doc_data.contentfields.get(field_name, "").strip()
                elif isinstance(doc_data, dict):
                    field_text = doc_data.get(field_name, "").strip()

                if field_text:
                    context_parts.append(f"Trecho de {doc_name.upper()} - Campo {field_name}: {field_text}")

        if not context_parts:
            self.logger.error(f"Nenhum texto de contexto pode ser reunido para o critério {criterion.get('id')}.")
            return None

        return "\n".join(context_parts)

    def perform_single_check(self,
                             criterion: Dict,
                             project_data: ProjectState) -> Dict:
        """
        Executa a verificação para um único critério.

        Args:
            criterion (Dict): Critério a ser verificado.
            project_data (ProjectState): Estado do projeto.

        Returns:
            Dict: Resultado da verificação.
        """
        criterion_id = criterion.get("id")
        self.logger.info(f"Executando verificação para o critério {criterion_id} - {criterion.get('title')}")

        # 1. Coletar o texto de contexto
        context_text = self.gather_context_text(criterion, project_data)

        result = {
            "id": criterion_id,
            "title": criterion.get("title"),
            "category": criterion.get("category"),
            "status": "Pendente",
            "justificativa": "A verificação não foi executada."
        }

        if not context_text:
            result["status"] = "Erro"
            result["justificativa"] = "Não foi possível coletar os dados necessários dos documentos para realizar esta verificação."
            return result

        # 2. Montar o prompt
        prompt = self.prompt_manager.get_criteriacheck_prompt(
            contexttext=context_text,
            instruction=criterion.get("promptinstruction", "")
        )

        # 3. Executar a chamada à IA
        model = self.gemini_client.settings.criteriamodel
        ai_response = self.gemini_client.generate_json_from_prompt(prompt, model)

        # 4. Processar a resposta da IA
        if ai_response and isinstance(ai_response, dict):
            result["status"] = ai_response.get("status", "Erro de Formato")
            result["justificativa"] = ai_response.get("justificativa", "A IA não forneceu uma justificativa no formato esperado.")
            self.logger.info(f"Critério {criterion_id} finalizado com status {result['status']}")
        else:
            result["status"] = "Erro de IA"
            result["justificativa"] = "A IA não retornou uma resposta JSON válida ou a chamada falhou."
            self.logger.error(f"Falha na execução da IA para o critério {criterion_id}.")

        return result

    def run_all_checks(self,
                       project_data: ProjectState) -> List[Dict]:
        """
        Executa todos os critérios de verificação para um determinado projeto.

        Args:
            project_data (ProjectState): O objeto de estado do projeto com os dados extraídos.

        Returns:
            List[Dict]: Lista de resultados de todas as verificações.
        """
        if not self.criteria:
            self.logger.error("Nenhum critério carregado. Abortando verificação.")
            return []

        self.logger.info(f"Iniciando verificação de {len(self.criteria)} critérios para o projeto {project_data.name}.")
        all_results = []

        for criterion in self.criteria:
            check_result = self.perform_single_check(criterion, project_data)
            all_results.append(check_result)

        self.logger.info("Verificação de todos os critérios concluída.")
        return all_results
