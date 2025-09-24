import json
from typing import List, Dict, Optional

from app.core.ai_client import GeminiClient
from app.core.prompt_manager import PromptManager
from app.core.logger import Logger
from app.core.models import ProjectState
from app.core.path_manager import PathManager

#======================================================================================================================
# Responsável por carregar critérios de um arquivo JSON e executar a verificação de conformidade em dados de um projeto.
#======================================================================================================================

class CriteriaManager:
    

    def __init__(self, gemini_client: GeminiClient):
        self.logger = Logger(name="CriteriaManager")
        self.ai = gemini_client
        self.prompt = PromptManager()
        self.path = PathManager()

        criteria_database_path = str(self.path.get_criteria_database())
        self.criteria = self.load_criteria(criteria_database_path)

        self.logger.info("Serviço inicializado com sucesso")




    def load_criteria(self, db_path: str) -> List[Dict]:
        
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




    def _gather_context_text(self, criterion: Dict, project_data: ProjectState) -> Optional[str]:
        
        context_parts = []
        source_docs = criterion.get("source_documents", [])

        for doc_name in source_docs:
            doc_data = getattr(project_data.extracted_data, doc_name, None)
            
            # Verifica se os dados daquele documento existem
            if not doc_data:
                self.logger.warning(f"Dados para o documento '{doc_name}' não encontrados no projeto para o critério '{criterion['id']}'.")
                continue

            # Pega o texto consolidado, que é a fonte da verdade após a edição do usuário
            consolidated_text = getattr(doc_data, 'consolidated_text', '').strip()

            if consolidated_text:
                # Adiciona um cabeçalho para dar contexto à IA, especialmente em verificações de consistência
                context_parts.append(f"### Documento Fornecido: {doc_name.upper()} ###\n{consolidated_text}")
            else:
                self.logger.warning(f"Texto consolidado para '{doc_name}' está vazio para o critério '{criterion['id']}'.")

        if not context_parts:
            self.logger.error(f"Nenhum texto de contexto pôde ser reunido para o critério '{criterion['id']}'.")
            return None

        return "\n\n---\n\n".join(context_parts)





    def _perform_single_check(self, criterion: Dict, project_data: ProjectState) -> Dict:
        
        criterion_id = criterion.get("id")
        self.logger.info(f"Executando verificação para o critério {criterion_id} - {criterion.get('title')}")

        # 1. Coletar o texto de contexto
        context_text = self._gather_context_text(criterion, project_data)

        result = {
            "id": criterion["id"],
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
        prompt = self.prompt.get_criteria_check_prompt(
            context_text=context_text,
            instruction=criterion.get("promptinstruction", "")
        )

        # 3. Executar a chamada à IA
        model = self.ai.settings.criteria_model
        ai_response = self.ai.generate_json_from_prompt(prompt, model)

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

    def run_all_checks(self, project_data: ProjectState) -> List[Dict]:

        if not self.criteria:
            self.logger.error("Nenhum critério carregado. Abortando verificação.")
            return []

        self.logger.info(f"Iniciando verificação de {len(self.criteria)} critérios para o projeto {project_data.name}.")
        all_results = []

        for criterion in self.criteria:
            check_result = self._perform_single_check(criterion, project_data)
            all_results.append(check_result)

        self.logger.info("Verificação de todos os critérios concluída.")
        return all_results
