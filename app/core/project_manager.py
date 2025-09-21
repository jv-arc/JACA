import os
import json
import shutil
from datetime import datetime
from typing import List, Optional, Dict

from app.core.models import ProjectState, ExtractedDataType
from app.core.criteria_manager import CriteriaManager
from app.core.data_manager import ExtractedDataManager
from app.core.logger import Logger
from app.core.export_manager import ExportManager

class ProjectManager:
    def __init__(
        self, 
        export_manager: ExportManager, 
        extraction_manager: ExtractedDataManager, 
        logger: Logger, 
        criteria_manager: CriteriaManager, 
        projects_dir='data/projects'
    ):
        
        self.projects_dir = projects_dir
        self.extraction_manager = extraction_manager
        self.criteria_manager = criteria_manager
        self.export_manager = export_manager
        self.logger = logger
        os.makedirs(self.projects_dir, exist_ok=True)
        self.logger.info("self inicializada.")

    #===================================
    # Métodos de Estrutura de Arquivos
    #===================================

    def list_projects(self) -> List[str]:
        projects = []
        if not os.path.exists(self.projects_dir):
            return projects
        for item in os.listdir(self.projects_dir):
            item_path = os.path.join(self.projects_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'project.json')):
                projects.append(item)
        return projects

    def project_path(self, project_name: str) -> str:
        return os.path.join(self.projects_dir, project_name)
    
    def project_json_path(self, project_name: str) -> str:
        return os.path.join(self.project_path(project_name), 'project.json')

    def project_files_dir(self, project_name: str) -> str:
        project_dir = os.path.join(self.project_path(project_name), 'files')
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    def project_extracted_dir(self, project_name: str) -> str:
        extracted_dir = os.path.join(self.project_path(project_name), "extracted")
        os.makedirs(extracted_dir, exist_ok=True)
        return extracted_dir
    
    def project_criteria_dir(self, project_name: str) -> str:
        criteria_dir = os.path.join(self.project_path(project_name), "criteria")
        os.makedirs(criteria_dir, exist_ok=True)
        return criteria_dir
    
    def _get_safe_filename(self, filename: str) -> str:
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        safe_filename = "".join(c if c in safe_chars else "_" for c in filename)
        if safe_filename.startswith('.'):
            safe_filename = 'file_' + safe_filename
        return safe_filename

    # ===========================================================
    # Métodos CRUD
    # ===========================================================
    
    def create_project(self, project_name: str) -> bool:
        project_dir = self.project_path(project_name)
        if os.path.exists(project_dir):
            self.logger.warning(f"Tentativa de criar um projeto que já existe: {project_name}")
            return False
        try: 
            os.makedirs(project_dir, exist_ok=True)

            self.project_files_dir(project_name)
            self.project_extracted_dir(project_name)
            self.project_criteria_dir(project_name)
            project = ProjectState(
                name=project_name,
                path=project_dir,
                base_files={
                    'estatuto': [],
                    'ata': [],
                    'identificacao': [],
                    'licenca': [],
                    'programacao': []
                },
                extracted_data=ExtractedDataType(),
                criteria_results={},
                current_step=1,
                created_at=datetime.now().isoformat(),
                last_modified=datetime.now().isoformat()
            )

            project_json_path = self.project_json_path(project_name)
            project.save_to_file(self.project_json_path(project_name))
            self.logger.info(f"Projeto '{project_name}' criado com sucesso.")
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao criar projeto '{project_name}': {e}", exc_info=True)
            if os.path.exists(project_dir): 
                shutil.rmtree(project_dir)
            return False

    def load_project(self, project_name: str) -> Optional[ProjectState]:
        project_json_path = self.project_json_path(project_name)

        if not os.path.exists(project_json_path):
            self.logger.error(f"Arquivo project.json não encontrado para o projeto '{project_name}'.")
            return None
        
        try:
            project = ProjectState.load_from_file(project_json_path)
            extracted_dir = self.project_extracted_dir(project_name)
            for category in ['estatuto', 'ata', 'identificacao', 'licenca', 'programacao']:
                extracted_file = os.path.join(extracted_dir, f'{category}.json')
                if os.path.exists(extracted_file):
                    with open(extracted_file, 'r', encoding='utf-8') as f:
                        extracted_data = json.load(f)
                        setattr(project.extracted_data, category, extracted_data)
            criteria_file = os.path.join(self.project_criteria_dir(project_name), 'results.json')
            if os.path.exists(criteria_file):
                with open(criteria_file, 'r', encoding='utf-8') as f:
                    project.criteria_results = json.load(f)
            return project
        
        except Exception as e:
            self.logger.error(f"Erro ao carregar o projeto '{project_name}': {e}", exc_info=True)
            return None

    def save_project(self, project: ProjectState) -> bool:
        
        try:
            project.last_modified = datetime.now().isoformat()
            project_json_path = self.project_json_path(project.name)

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

            metadata_project.save_to_file(project_json_path)
            extracted_dir = self.project_extracted_dir(project.name)
            for category in ['estatuto', 'ata', 'identificacao', 'licenca', 'programacao']:
                extracted_data = getattr(project.extracted_data, category, None)
                if extracted_data:
                    extracted_file = os.path.join(extracted_dir, f'{category}.json')
                    with open(extracted_file, 'w', encoding='utf-8') as f:
                        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            if project.criteria_results:
                criteria_file = os.path.join(self.project_criteria_dir(project.name), 'results.json')
                with open(criteria_file, 'w', encoding='utf-8') as f:
                    json.dump(project.criteria_results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Projeto '{project.name}' salvo com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar o projeto '{project.name}': {e}", exc_info=True)
            return False

    def delete_project(self, project_name: str) -> bool:
        project_dir = self.project_path(project_name)
        try:
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
                self.logger.info(f"Projeto '{project_name}' deletado com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao deletar o projeto '{project_name}': {e}", exc_info=True)
            return False

    # ===========================================================
    # Métodos de Arquivos
    # ===========================================================

    def add_pdf_file(self, project_name: str, uploaded_file, category: str) -> bool:
        project = self.load_project(project_name)
        if project is None:
            return false

        if category not in project.base_files:
            project.base_files[category] = []
        try:
            safe_filename = self._get_safe_filename(uploaded_file.name)
            project_files_dir = self.project_files_dir(project_name)
            file_path = os.path.join(project_files_dir, f"{category}_{safe_filename}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            if file_path not in project.base_files[category]:
                project.base_files[category].append(file_path)

            self.logger.info(f"Arquivo '{uploaded_file.name}' adicionado à categoria '{category}' do projeto '{project_name}'.")
            return self.save_project(project)
        except Exception as e:
            self.logger.error(f"Erro ao adicionar arquivo PDF: {e}", exc_info=True)
            return False
    
    def remove_pdf_file(self, project_name: str, file_path: str, category: str) -> bool:
        project = self.load_project(project_name)
        if project is None:
            return False
        try:
            # Remove dos dados do projeto
            if category in project.base_files and file_path in project.base_files[category]:
                project.base_files[category].remove(file_path)
                # Remove arquivo da pasta
                if os.path.exists(file_path):
                    os.remove(file_path)
                return self.save_project(project)
            return False
        except Exception as e:
            print(f'Error removing PDF file: {e}')
            return False


    def verify_and_fix_file_paths(self, project_name: str) -> bool:
        project = self.load_project(project_name)
        if project is None:
            return False
        files_updated = False
        for category in project.base_files:
            # Filtra arquivos que não existem
            existing_files = []
            for file_path in project.base_files[category]:
                if os.path.exists(file_path):
                    existing_files.append(file_path)
                else:
                    print(f"Arquivo removido da lista (não encontrado): {file_path}")
                    files_updated = True
            project.base_files[category] = existing_files
        if files_updated:
            return self.save_project(project)
        return True

    def get_files_by_category(self, project_name: str, category: str) -> List[str]:
        project = self.load_project(project_name)
        if project is None: return []
        return project.base_files.get(category, [])
    
    def get_all_files(self, project_name: str) -> Dict[str, List[str]]:
        project = self.load_project(project_name)
        if project is None:
            return {}
        return project.base_files

    def project_exports_dir(self, project_name: str) -> str:
        exports_dir = os.path.join(self.project_path(project_name), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        return exports_dir
    

    # ===========================================================
    # Métodos de I/O para Dados Extraídos
    # ===========================================================
    
    def has_extracted_text(self, project_name: str, category: str) -> bool:
        """Verifica se o arquivo JSON de extração existe e tem conteúdo."""
        extracted_file_path = os.path.join(self.project_extracted_dir(project_name), f'{category}.json')
        if not os.path.exists(extracted_file_path):
            return False
        try:
            with open(extracted_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Verifica se há texto consolidado ou algum campo de conteúdo preenchido
            if data.get('consolidated_text', '').strip():
                return True
            content_fields = data.get('content_fields', {})
            return any(value and str(value).strip() for value in content_fields.values())
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao ler arquivo de extração '{extracted_file_path}': {e}")
            return False

    def load_structured_extraction(self, project_name: str, category: str) -> Optional[Dict]:
        """Carrega a estrutura completa de dados extraídos de um arquivo JSON."""
        extracted_file_path = os.path.join(self.project_extracted_dir(project_name), f'{category}.json')
        if not os.path.exists(extracted_file_path):
            return None
        try:
            with open(extracted_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Erro ao carregar extração estruturada de '{extracted_file_path}': {e}")
            return None

    def save_structured_extraction(self, 
                                    project_name: str, category: str,
                                    content_fields: Dict[str, str],
                                    ignored_fields: Dict[str, str]) -> bool:

        return self.extraction_manager.save_structured_extraction(project_name, category, content_fields, ignored_fields)

    def load_extracted_text(self, project_name: str, category: str) -> Optional[str]:
        """Carrega apenas o campo 'consolidated_text' do arquivo JSON."""
        data = self.load_structured_extraction(project_name, category)
        return data.get('consolidated_text', '') if data else None

    def save_edited_text(self, project_name: str, category: str, text: str) -> bool:
        """Salva o texto consolidado editado pelo usuário."""
        data = self.load_structured_extraction(project_name, category)
        if data is None:
            self.logger.warning(f"Tentativa de salvar texto editado para '{category}', mas o arquivo base não existe. Ação ignorada.")
            return False
        
        data['consolidated_text'] = text
        data['last_modified'] = datetime.now().isoformat()
        data['reviewed'] = True  # Marca como revisado pelo usuário

        extracted_file_path = os.path.join(self.project_extracted_dir(project_name), f'{category}.json')
        try:
            with open(extracted_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Texto editado para '{category}' do projeto '{project_name}' salvo com sucesso.")
            return True
        except IOError as e:
            self.logger.error(f"Erro ao salvar texto editado em '{extracted_file_path}': {e}")
            return False

    def get_workflow_fields(self, category: str) -> Dict[str, List[str]]:
        """Delega a busca pelos campos do workflow para o ExtractedDataManager."""
        return self.extraction_manager.WORKFLOWS.get(category, {})

    def update_criteria_results(self, project_name: str, criteria_results: List[Dict]) -> bool:
            """
            Salva os resultados da verificação de critérios no arquivo results.json
            e atualiza o estado geral do projeto.
            """
            self.logger.info(f"Salvando {len(criteria_results)} resultados de critérios para o projeto '{project_name}'.")
            
            # Salva o arquivo JSON com os resultados detalhados
            criteria_file_path = os.path.join(self.project_criteria_dir(project_name), 'results.json')
            try:
                with open(criteria_file_path, 'w', encoding='utf-8') as f:
                    json.dump(criteria_results, f, indent=2, ensure_ascii=False)
            except IOError as e:
                self.logger.error(f"Erro de I/O ao salvar o arquivo de resultados de critérios: {e}")
                return False
    
            # Atualiza o objeto do projeto principal
            project = self.load_project(project_name)
            if project is None:
                return False
            
            project.criteria_results = criteria_results
            # Avança o passo do projeto para indicar que a verificação foi concluída
            project.current_step = max(project.current_step, 4) 
            
            return self.save_project(project)

    # ===========================================================
    # Orquestração de IA
    # ===========================================================

    def export_project_package(self, project_name: str, user_overrides: Dict) -> Optional[str]:
        self.logger.info(f"Iniciando orquestração da exportação para o projeto '{project_name}'.")
        # a. Carrega todos os dados do projeto
        project_data = self.load_project(project_name)
        if not project_data:
            self.logger.error(f"Não foi possível carregar o projeto '{project_name}' para exportação.")
            return None
        
        # b. Define o diretório de saída
        export_dir = self.project_exports_dir(project_name)
        # c. Delega a geração e concatenação para o ExportManager
        try:
            final_pdf_path = self.export_manager.generate_full_package(
                project_data=project_data,
                user_overrides=user_overrides,
                export_dir=export_dir
            )
            return final_pdf_path
        except Exception as e:
            self.logger.error(f"A orquestração da exportação falhou: {e}", exc_info=True)
            return None

    def execute_criteria_verification(self, project_name: str) -> bool:
            self.logger.info(f"Iniciando orquestração da verificação de critérios para o projeto '{project_name}'.")
    
            # a. Carrega todos os dados do projeto, incluindo as extrações
            project_data = self.load_project(project_name)
            if not project_data:
                self.logger.error("Não foi possível carregar o projeto para iniciar a verificação de critérios.")
                return False
            
            # b. Delega a execução para o CriteriaManager
            results = self.criteria_manager.run_all_checks(project_data)
            
            if not results:
                self.logger.warning("A verificação de critérios não produziu resultados.")
                # Pode ser um erro ou simplesmente não haver critérios, então continuamos para salvar o resultado vazio.
            
            # c. Salva os resultados obtidos
            return self.update_criteria_results(project_name, results)


    # Delega a extracao e salva os resultados
    def run_extraction_for_category(self, project_name: str, category: str) -> bool:
        self.logger.info(f"Orquestrando extração para '{project_name}', categoria '{category}'.")
        
        file_paths = self.get_files_by_category(project_name, category)
        if not file_paths:
            self.logger.warning(f"Nenhum arquivo para extrair na categoria '{category}'.")
            return False

        extracted_data = self.extraction_manager.extract_data_from_files(file_paths, category)
        
        if not extracted_data:
            self.logger.error(f"O processo de extração para '{category}' não retornou dados.")
            return False

        return self._save_structured_data(project_name, category, extracted_data)

    def _save_structured_data(self, project_name: str, category: str, extracted_data: Dict) -> bool:
        try:
            content = extracted_data.get('content_fields', {})
            ignored = extracted_data.get('ignored_fields', {})

            final_data_obj = {
                'content_fields': content,
                'ignored_fields': ignored,
                'consolidated_text': self.extraction_manager.consolidate_content_fields(content),
                'workflow_used': category,
                'extracted_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'reviewed': False
            }
            
            extracted_file_path = os.path.join(self.project_extracted_dir(project_name), f'{category}.json')
            
            with open(extracted_file_path, 'w', encoding='utf-8') as f:
                json.dump(final_data_obj, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Dados estruturados para '{category}' salvos em '{extracted_file_path}'.")
            return True
        except Exception as e:
            self.logger.error(f"Falha ao salvar dados estruturados para '{category}': {e}", exc_info=True)
            return False



    def get_all_criteria(self) -> List[Dict]:
        """Expõe a lista de critérios carregada pelo CriteriaManager."""
        return self.criteria_manager.criteria
    
    def execute_single_criterion_verification(self, project_name: str, criterion_id: str) -> bool:
        """
        Orquestra a verificação de um único critério e atualiza os resultados.
        """
        self.logger.info(f"Iniciando verificação do critério '{criterion_id}' para o projeto '{project_name}'.")
    
        # a. Carrega os dados do projeto
        project_data = self.load_project(project_name)
        if not project_data:
            self.logger.error(f"Não foi possível carregar o projeto '{project_name}'.")
            return False
    
        # b. Encontra o critério específico
        criterion_to_check = next((c for c in self.get_all_criteria() if c['id'] == criterion_id), None)
        if not criterion_to_check:
            self.logger.error(f"Critério com ID '{criterion_id}' não encontrado na base de dados.")
            return False
    
        # c. Delega a execução para um método do CriteriaManager (vamos assumir que ele existe)
        new_result = self.criteria_manager._perform_single_check(criterion_to_check, project_data)
    
        # d. Atualiza a lista de resultados existente
        current_results = project_data.criteria_results or []
            
        # Remove o resultado antigo, se existir
        updated_results = [res for res in current_results if res.get('id') != criterion_id]
        updated_results.append(new_result)
    
        # e. Salva a lista de resultados atualizada
        return self.update_criteria_results(project_name, updated_results)
    
    def update_manual_override(self, project_name: str, criterion_id: str, new_status: str, new_justification: str) -> bool:
        self.logger.info(f"Aplicando override manual para o critério '{criterion_id}' no projeto '{project_name}'.")
        project_data = self.load_project(project_name)
        if not project_data or not project_data.criteria_results:
            self.logger.error("Não há resultados para fazer override.")
            return False
    
        # Encontra e atualiza o resultado
        result_found = False
        for result in project_data.criteria_results:
            if result.get('id') == criterion_id:
                result['status'] = new_status
                result['justificativa'] = new_justification
                result['overridden_at'] = datetime.now().isoformat() # Adiciona um marcador
                result_found = True
                break
        
        if not result_found:
            self.logger.error(f"Não foi encontrado um resultado existente para o critério '{criterion_id}'.")
            return False

        # Salva o projeto com a lista de resultados modificada
        return self.save_project(project_data)

    def get_report_configuration(self) -> Dict:
        self.logger.info("Buscando configuração de relatório para a UI.")
        # Retornamos uma cópia para evitar modificações acidentais no objeto em memória
        return self.report_config_manager.get_full_config().copy()

    def save_report_configuration(self, new_config_data: Dict) -> bool:
        self.logger.info("Recebida solicitação da UI para salvar a nova configuração de relatório padrão.")
        # Delega a responsabilidade de salvar para o manager correto
        return self.report_config_manager.save_config(new_config_data)

    def get_exported_package_path(self, project_name: str) -> Optional[str]:
        export_dir = self.project_exports_dir(project_name)
        expected_filename = f"REQUISICAO_{project_name}.pdf"
        full_path = os.path.join(export_dir, expected_filename)

        if os.path.exists(full_path):
            self.logger.info(f"Pacote de exportação já existente encontrado em: {full_path}")
            return full_path
        
        return None

    def delete_exported_package(self, project_name: str) -> bool:
        package_path = self.get_exported_package_path(project_name)
        if not package_path:
            self.logger.warning(f"Tentativa de apagar pacote para '{project_name}', mas ele não existe.")
            return True # O estado desejado (sem arquivo) já foi alcançado.

        self.logger.info(f"Apagando pacote de exportação existente: {package_path}")
        try:
            os.remove(package_path)
            self.logger.info("Pacote apagado com sucesso.")
            return True
        except OSError as e:
            self.logger.error(f"Erro de sistema operacional ao apagar o pacote: {e}", exc_info=True)
            return False

    def test_api_connection(self) -> (bool, str):
       """
       Testa a conexão com a API Gemini para verificar se a chave é válida.
       Delega a chamada para o GeminiClient.
       """
       self.logger.info("Executando teste de conexão da API a pedido da UI.")
       try:
           # Uma chamada simples e de baixo custo para a API
           response = self.criteria_manager.gemini_client.generate_text_from_prompt(
               prompt="Responda apenas com a palavra 'OK'.",
               model_name='gemini-1.5-flash' # Usando um modelo conhecido e rápido
           )
           if response and 'OK' in response:
               return (True, "Conexão bem-sucedida!")
           else:
               return (False, f"A API respondeu, mas o resultado foi inesperado: {response}")
       except Exception as e:
           self.logger.error(f"Falha no teste de conexão da API: {e}")
           return (False, f"Falha na conexão: {e}")