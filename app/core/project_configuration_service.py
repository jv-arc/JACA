import json
from typing import Dict, List, Optional
from datetime import datetime

from app.core.path_manager import PathManager
from app.core.models import ProjectState
from app.core.logger import Logger
from app.core.project_crud_service import ProjectCRUDService
from app.core.report_config_manager import ReportConfigManager


#================================================================
# CLASSE: ProjectConfigurationService
#----------------------------------------------------------------
# Implementa métodos para gerenciar configurações de projetos
# e relatórios dentro da aplicação
#================================================================




class ProjectConfigurationService:

    def __init__(self):
        self.logger = Logger("ProjectConfigurationService")
        self.crud_service = ProjectCRUDService()
        self.report_config_manager = ReportConfigManager()
        self.logger.info("Serviço inicializado com sucesso")




    
    #----------------------------------------------------------------
    # Obtém configuração de relatório
    #----------------------------------------------------------------
    def get_report_configuration(self, project_name: Optional[str] = None) -> Dict:

        self.logger.info("Buscando configuração de relatório para a UI.")
        
        try:
            config = self.report_config_manager.get_full_config()
            return config.copy() if config else {}
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar configuração de relatório: {e}")
            return {}

    






    #----------------------------------------------------------------
    # Salva configuração de relatório
    #----------------------------------------------------------------
    def save_report_configuration(self, config_data: Dict, project_name: Optional[str] = None) -> bool:
    
        self.logger.info("Recebida solicitação da UI para salvar a nova configuração de relatório.")
        
        try:
            success = self.report_config_manager.save_config(config_data)
            
            if success:
                self.logger.info("Configuração de relatório salva com sucesso.")
            else:
                self.logger.error("Falha ao salvar configuração de relatório.")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração de relatório: {e}")
            return False

    




    #----------------------------------------------------------------
    # Reseta configuração de relatório para padrões
    #----------------------------------------------------------------
    def reset_report_configuration(self, project_name: Optional[str] = None) -> bool:
    
        self.logger.info("Resetando configuração de relatório para padrões.")
        
        try:
            # Carrega configuração padrão do arquivo de template
            default_config_path = PathManager.get_report_config()
            
            if default_config_path.exists():
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    default_config = json.load(f)
                
                return self.save_report_configuration(default_config, project_name)
            else:
                self.logger.error("Arquivo de configuração padrão não encontrado.")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao resetar configuração: {e}")
            return False

    




    #----------------------------------------------------------------
    # Obtém configurações específicas do projeto
    #----------------------------------------------------------------
    def get_project_settings(self, project_name: str) -> Dict:
        
        self.logger.info(f"Buscando configurações específicas do projeto '{project_name}'.")
        
        try:
            project_data = self.crud_service.load_project(project_name)
            if not project_data:
                self.logger.warning(f"Projeto '{project_name}' não encontrado.")
                return {}
            
            # Extrai configurações do projeto (se existirem)
            settings = getattr(project_data, 'settings', {})
            return settings if settings else {}
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar configurações do projeto '{project_name}': {e}")
            return {}

    




    #----------------------------------------------------------------
    # Atualiza configurações específicas do projeto
    #----------------------------------------------------------------
    def update_project_settings(self, project_name: str, settings: Dict) -> bool:
        
        self.logger.info(f"Atualizando configurações do projeto '{project_name}'.")
        
        try:
            project_data = self.crud_service.load_project(project_name)
            if not project_data:
                self.logger.error(f"Projeto '{project_name}' não encontrado para atualização de configurações.")
                return False
            
            # Atualiza as configurações
            if not hasattr(project_data, 'settings'):
                project_data.settings = {}
            
            project_data.settings.update(settings)
            project_data.last_modified = datetime.now().isoformat()
            
            return self.crud_service.save_project(project_data)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar configurações do projeto '{project_name}': {e}")
            return False

    




    #----------------------------------------------------------------
    # Exporta configuração do projeto
    #----------------------------------------------------------------
    def export_project_configuration(self, project_name: str) -> Optional[Dict]:
        
        self.logger.info(f"Exportando configuração do projeto '{project_name}'.")
        
        try:
            project_settings = self.get_project_settings(project_name)
            report_config = self.get_report_configuration(project_name)
            
            export_data = {
                'project_name': project_name,
                'exported_at': datetime.now().isoformat(),
                'project_settings': project_settings,
                'report_configuration': report_config,
                'version': '1.0'
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar configuração do projeto '{project_name}': {e}")
            return None

    




    #----------------------------------------------------------------
    # Importa configuração para um projeto
    #----------------------------------------------------------------
    def import_project_configuration(self, project_name: str, config_data: Dict) -> bool:
        
        self.logger.info(f"Importando configuração para o projeto '{project_name}'.")
        
        try:
            # Valida estrutura dos dados
            if not isinstance(config_data, dict):
                self.logger.error("Dados de configuração inválidos.")
                return False
            
            success = True
            
            # Importa configurações do projeto
            if 'project_settings' in config_data:
                success &= self.update_project_settings(project_name, config_data['project_settings'])
            
            # Importa configuração de relatório (se específica do projeto)
            if 'report_configuration' in config_data:
                success &= self.save_report_configuration(
                    config_data['report_configuration'], 
                    project_name
                )
            
            if success:
                self.logger.info(f"Configuração importada com sucesso para '{project_name}'.")
            else:
                self.logger.error(f"Falha parcial ao importar configuração para '{project_name}'.")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao importar configuração para o projeto '{project_name}': {e}")
            return False

    





    #----------------------------------------------------------------
    # Valida configuração de relatório
    #----------------------------------------------------------------
    def validate_report_configuration(self, config_data: Dict) -> tuple[bool, List[str]]:
        
        errors = []
        
        try:
            # Validações básicas
            if not isinstance(config_data, dict):
                errors.append("Configuração deve ser um dicionário")
                return False, errors
            
            # Valida campos obrigatórios
            required_fields = ['tables', 'metadata']
            for field in required_fields:
                if field not in config_data:
                    errors.append(f"Campo obrigatório ausente: {field}")
            
            # Valida estrutura das tabelas
            if 'tables' in config_data:
                tables = config_data['tables']
                if not isinstance(tables, list):
                    errors.append("Campo 'tables' deve ser uma lista")
                else:
                    for i, table in enumerate(tables):
                        if not isinstance(table, dict):
                            errors.append(f"Tabela {i} deve ser um dicionário")
                            continue
                        
                        if 'fields' not in table:
                            errors.append(f"Tabela {i} deve ter campo 'fields'")
            
            is_valid = len(errors) == 0
            return is_valid, errors
            
        except Exception as e:
            errors.append(f"Erro durante validação: {str(e)}")
            return False, errors
