from app.core.config import settings
from app.core.ai_client import gemini_client
from app.core.logger import Logger

class AppConfigService():

    def __init__(self) -> None:
        self.logger = Logger("AppConfigService")
        self.ai = gemini_client
        self.settings = settings


    def update_api_key(self, new_key:str)-> bool:
        old_key = settings.api_key
        settings.update_api_key(new_key)
        gemini_client.reload()

        self.logger.info("Testando nova chave de API")
        works = gemini_client.test_api_connection(settings.criteria_model)
        
        if works:
            self.logger.info("Nova chave de API funciona corretamente")
            return True
        else:
            self.logger.error("Nova chave de API não funciona, usando o modelo antigo")
            settings.update_api_key(old_key)
            return False




    def update_extraction_model(self, new_model:str ) -> bool:
        old_model = settings.extraction_model
        settings.update_extraction_model(new_model)
        gemini_client.reload()

        self.logger.info("Testando novo modelo de extração")
        works = gemini_client.test_api_connection(settings.extraction_model)
        
        if works:
            self.logger.info("Novo modelo de extração funciona corretamente")
            return True
        else:
            self.logger.error("Novo modelo de extração não funciona, usando o modelo antigo")
            settings.update_extraction_model(old_model)
            return False




    def update_criteria_model(self, new_model:str ) -> bool:
        old_model = settings.criteria_model
        settings.update_criteria_model(new_model)
        gemini_client.reload()

        self.logger.info("Testando novo modelo de critérios")
        works = gemini_client.test_api_connection(settings.criteria_model)
        
        if works:
            self.logger.info("Novo modelo de critérios funciona corretamente")
            return True
        else:
            self.logger.error("Novo modelo de criterios não funciona, usando o modelo antigo")
            settings.update_criteria_model(old_model)
            return False
