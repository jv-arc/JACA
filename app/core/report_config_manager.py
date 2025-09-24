import json
from typing import Dict, List, Optional

from app.core.logger import Logger
from app.core.path_manager import PathManager

class ReportConfigManager:
    def __init__(self):

        self.logger = Logger(name="ReportConfigManager")
        self.path = PathManager()
        self.config_path = str(self.path.get_app_config())
        self.config_data: Dict = {}
        try:
            self.load_config()
            self.logger.info("Classe inicializada corretamente")
        except:
            self.logger.error("Erro ao inicializar a classe.")
            




    #---------------------------------------------------------------------------------
    # Carrega configuracoes
    #---------------------------------------------------------------------------------
    def load_config(self):
        self.logger.info(f"Carregando configuração de relatório de '{self.config_path}'...")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.logger.info("Configuração de relatório carregada com sucesso.")
        except FileNotFoundError:
            self.logger.error(f"CRÍTICO: Arquivo de configuração de relatório '{self.config_path}' não encontrado.")
            # A aplicação não pode gerar relatórios sem este arquivo.
            self.config_data = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"CRÍTICO: Arquivo de configuração de relatório '{self.config_path}' está mal formatado. Erro: {e}")
            self.config_data = {}




    #---------------------------------------------------------------------------------
    # Salvar configuracoes
    #---------------------------------------------------------------------------------
    def save_config(self, new_config_data: Dict) -> bool:

        self.logger.info(f"Salvando alterações na configuração de relatório em '{self.config_path}'...")
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config_data, f, indent=2, ensure_ascii=False)
            
            # Atualiza a configuração em memória
            self.config_data = new_config_data
            self.logger.info("Configuração de relatório atualizada com sucesso.")
            return True
        except IOError as e:
            self.logger.error(f"Erro de I/O ao salvar a configuração de relatório: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado ao salvar a configuração de relatório: {e}")
            return False



    #---------------------------------------------------------------------------------
    # Obtem o Prompt de extracao de conteudo
    #---------------------------------------------------------------------------------

    def get_full_config(self) -> Dict:
        return self.config_data



    #---------------------------------------------------------------------------------
    # Obtem o Prompt de extracao de conteudo
    #---------------------------------------------------------------------------------
    def get_user_input_fields(self) -> List[Dict]:
        user_fields = []
        tables = self.config_data.get('tables', [])
        for table in tables:
            for field in table.get('fields', []):
                if field.get('source') == 'user_input':
                    user_fields.append(field)
        return user_fields