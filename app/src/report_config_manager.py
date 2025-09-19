import json
from typing import Dict, List, Optional

from src.logger import Logger

class ReportConfigManager:
    """
    Gerencia a configuração para a geração de relatórios, lendo e salvando o arquivo reportconfig.json.
    """
    
    def __init__(self, logger: Logger, config_path: str = "src/config/reportconfig.json"):
        """
        Inicializa o gerenciador de configuração de relatórios.
        
        Args:
            logger (Logger): A instância do logger para registrar eventos.
            config_path (str): O caminho para o arquivo JSON de configuração.
        """
        self.logger = logger
        self.config_path = config_path
        self.config_data: Dict = {}
        self.load_config()
    
    def load_config(self):
        """Carrega o arquivo de configuração JSON na memória."""
        self.logger.info(f"Carregando configuração de relatório de {self.config_path}...")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.logger.info("Configuração de relatório carregada com sucesso.")
        except FileNotFoundError:
            self.logger.error(f"CRÍTICO: Arquivo de configuração de relatório {self.config_path} não encontrado. A aplicação não pode gerar relatórios sem este arquivo.")
            self.config_data = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"CRÍTICO: Arquivo de configuração de relatório {self.config_path} está mal formatado. Erro: {e}")
            self.config_data = {}
    
    def save_config(self, new_config_data: Dict) -> bool:
        """
        Salva um novo dicionário de configuração no arquivo JSON, sobrescrevendo o conteúdo existente.
        
        Args:
            new_config_data (Dict): O objeto de configuração completo a ser salvo.
        
        Returns:
            bool: True se o salvamento for bem-sucedido, False caso contrário.
        """
        self.logger.info(f"Salvando alterações na configuração de relatório em {self.config_path}...")
        
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
    
    def get_full_config(self) -> Dict:
        """Retorna todo o objeto de configuração."""
        return self.config_data
    
    def get_user_input_fields(self) -> List[Dict]:
        """
        Retorna uma lista de todos os campos que requerem entrada do usuário.
        Útil para construir o formulário na UI do Streamlit.
        """
        user_fields = []
        tables = self.config_data.get('tables', [])
        
        for table in tables:
            for field in table.get('fields', []):
                if field.get('source') == 'userinput':
                    user_fields.append(field)
        
        return user_fields