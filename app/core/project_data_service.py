import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.core.path_manager import PathManager
from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService
from app.core.data_manager import ExtractedDataManager
from app.core.ai_client import GeminiClient

from app.core.models import *


#================================================================
# CLASSE: ProjectDataService
#----------------------------------------------------------------
# Implementa metodos para acessar e utilizar arquivos de dados 
# dentro dos projetos 
#================================================================




class ProjectDataService:


    def __init__(self, gemini_client: GeminiClient):
        self.logger = Logger("ProjectDataService")
        self.crud_service = ProjectCRUDService()
        self.extraction_manager = ExtractedDataManager(gemini_client=gemini_client)
        self.logger.info("Serviço inicializado com sucesso")
    
    

    #----------------------------------------------------------------
    # Verifica se o arquivo JSON de extracao existe e tem dados extraidos
    #----------------------------------------------------------------
    def has_extracted_text(self, project_name: str) -> bool:
        categories = ["estatuto", "ata", "identificacao", "licenca", "programacao"]
        
        for category in categories:
            if self.has_extraction_for_category(project_name, category):
                return True
        return False
    



    #----------------------------------------------------------------
    # Verifica se existem dados extraidos para uma categoria especifica
    #----------------------------------------------------------------
    def has_extraction_for_category(self, project_name: str, category: str) -> bool:
        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)
        
        if not extracted_file_path.exists():
            return False
        
        try:
            with open(extracted_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get('consolidated_text', '').strip():
                return True
            
            content_fields = data.get('content_fields', {})
            return any(value and str(value).strip() for value in content_fields.values())

        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao ler arquivo de extração '{extracted_file_path}': {e}")
            return False

    


    


    #----------------------------------------------------------------
    # Carrega dados extraidos
    #----------------------------------------------------------------
    def load_structured_extraction(self, project_name: str, category: str) -> Optional[Dict]:
        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)
        
        if not extracted_file_path.exists():
            return None
        
        try:
            with open(extracted_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao carregar extração estruturada de '{extracted_file_path}': {e}")
            return None
    





    #----------------------------------------------------------------
    # Salva dados extraídos estruturados
    #----------------------------------------------------------------
    def save_structured_extraction(self, project_name: str, category: str, data: Dict) -> bool:
        content_fields = data.get('content_fields', {})
        ignored_fields = data.get('ignored_fields', {})
        consolidated_text = data.get('main_content', {})

        final_data_obj = {
            'content_fields': content_fields,
            'ignored_fields': ignored_fields,
            'consolidated_text': consolidated_text,
            'workflow_used': category,
            'extracted_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'reviewed': False
        }

    
        return self.extraction_manager.save_dict_to_file(project_name, category, final_data_obj)



    #----------------------------------------------------------------
    # Atualiza um campo específico de extracao
    #----------------------------------------------------------------
    def update_extraction_field(self, project_name: str, category: str, field: str, value: any) -> bool:
        data = self.load_structured_extraction(project_name, category)
        if not data:
            return False
        
        try:
            # Atualiza o campo específico
            if 'content_fields' not in data:
                data['content_fields'] = {}
            
            data['content_fields'][field] = value
            data['last_modified'] = datetime.now().isoformat()
            
            # Salva de volta
            extracted_file_path = PathManager.get_extracted_file_path(project_name, category)
            with open(extracted_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar campo '{field}' para categoria '{category}': {e}")
            return False
    





    #----------------------------------------------------------------
    # Salva texto consolidado editado
    #----------------------------------------------------------------
    def load_consolidated_text(self, project_name: str, category: str) -> Optional[str]:
        try:
            data = self.load_structured_extraction(project_name, category)
        
        
        return data.get('consolidated_text', '') if data else None
        







    #----------------------------------------------------------------
    # Verifica se projeto tem dados extraidos
    #----------------------------------------------------------------
    def save_edited_text(self, project_name: str, category: str, text: str) -> bool:
        data = self.load_structured_extraction(project_name, category)
        if data is None:
            self.logger.warning(f"Tentativa de salvar texto editado para '{category}', mas o arquivo base não existe.")
            return False

        data['consolidated_text'] = text
        data['last_modified'] = datetime.now().isoformat()
        data['reviewed'] = True  # Marca como revisado pelo usuário

        extracted_file_path = PathManager.get_extracted_file_path(project_name, category)
        
        try:
            with open(extracted_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Texto editado para '{category}' do projeto '{project_name}' salvo com sucesso.")
            return True
            
        except IOError as e:
            self.logger.error(f"Erro ao salvar texto editado em '{extracted_file_path}': {e}")
            return False  






    #----------------------------------------------------------------
    # Obtém texto consolidado de todas as categorias
    #----------------------------------------------------------------
    def get_list_consolidated_text(self, project_name: str) -> str:
        categories = ["estatuto", "ata", "identificacao", "licenca", "programacao"]
        consolidated_texts = []
        
        for category in categories:
            text = self.load_extracted_text(project_name, category)
            if text:
                consolidated_texts.append(f"=== {category.upper()} ===\n{text}")
        
        return "\n\n".join(consolidated_texts)
    





    #----------------------------------------------------------------
    # Obtem os campos de extracao de dados
    #----------------------------------------------------------------
    def get_workflow_fields(self, category: str) -> Dict[str, List[str]] | List[Any]:
        return self.extraction_manager.workflows.get(category, [])
    


    #----------------------------------------------------------------
    # Obtem os dados extraídos no projeto
    #----------------------------------------------------------------
    def get_extracted_data(self, project_name, category)-> Dict|None:
        project_data = self.crud_service.load_project(project_name)
        return getattr(project_data, category, None)



    #----------------------------------------------------------------
    # Obtém informações pendentes
    #----------------------------------------------------------------
    def get_pending_information(self, project_name: str) -> Dict[str, List[str]]:
        self.logger.info(f"Iniciando verificação de informações pendentes para o projeto '{project_name}'.")
        
        pending_info = {}
        PENDING_TOKEN = "NAO-ENCONTRADO"
        
        project_data = self.crud_service.load_project(project_name)
        if not project_data or not project_data.extracted_data:
            self.logger.warning(f"Não há dados extraídos para verificar no projeto '{project_name}'.")
            return pending_info

        categories_to_check = ["estatuto", "ata", "licenca", "programacao"]
        
        for category in categories_to_check:
            category_data = getattr(project_data.extracted_data, category, None)
            
            if category_data and hasattr(category_data, 'content_fields'):
                content_fields = category_data.content_fields
                
                if not content_fields:
                    continue
                
                for field_name, value in content_fields.items():
                    # Verifica se o valor corresponde ao token de pendência
                    if isinstance(value, str) and value.strip() == PENDING_TOKEN:
                        if category not in pending_info:
                            pending_info[category] = []
                        pending_info[category].append(field_name)

        if pending_info:
            self.logger.info(f"Verificação concluída. Encontrados campos pendentes: {pending_info}")
        else:
            self.logger.info("Verificação concluída. Nenhuma informação pendente foi encontrada.")
        
        return pending_info
    





    #----------------------------------------------------------------
    # Marca campo como completo
    #----------------------------------------------------------------
    def mark_field_as_complete(self, project_name: str, category:str,  field: str) -> bool:
        return self.update_extraction_field(project_name, category, field, "")
    







    #----------------------------------------------------------------
    # Atualiza lista de diretores
    #----------------------------------------------------------------
    def update_director_list(self, project_name: str, directors: List[Dict]) -> bool:
        self.logger.info(f"Atualizando a lista de dirigentes para o projeto '{project_name}'.")
        
        project_data = self.crud_service.load_project(project_name)
        if not project_data or not project_data.extracted_data.ata:
            self.logger.error("Não foi possível carregar os dados da ata para atualizar a lista de dirigentes.")
            return False

        # Atualiza a chave específica com a lista fornecida
        project_data.extracted_data.ata.content_fields['lista_dirigentes_eleitos'] = directors
        
        return self.crud_service.save_project(project_data)
    





    #----------------------------------------------------------------
    # Obtem lista de diretores
    #----------------------------------------------------------------
    def get_director_list(self, project_name: str) -> List[Dict]:
        project_data = self.crud_service.load_project(project_name)
        if not project_data or not project_data.extracted_data.ata:
            return []

        content_fields = getattr(project_data.extracted_data.ata, 'content_fields', {})
        return content_fields.get('lista_dirigentes_eleitos', [])