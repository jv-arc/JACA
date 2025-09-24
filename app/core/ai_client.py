import google.generativeai as genai
import json
from typing import Dict, Optional, List
from PIL import Image

from app.core.config import Settings
from app.core.logger import Logger
#===========================================================================
# CLASSE: GeminiClient
#---------------------------------------------------------------------------
# Uma classe que trata a conexao do programa e a API do Gemini do Google
# utiliza a chave de API obtida pela classe Settings
#===========================================================================
class GeminiClient:



    #---------------------------------------------------------------------------------
    # Inicializa classe
    #---------------------------------------------------------------------------------
    # Inicializa a classe criando e testando uma conexão 
    #---------------------------------------------------------------------------------
    def __init__(self):
        self.settings = Settings()
        self.logger = Logger("GeminiClient")
        self._is_configured = False
        
        if not self.settings.api_key:
            self.logger.critical("API key do Gemini não foi fornecida nas configurações.")
            raise ValueError("A API key não pode ser vazia.")

        try:
            genai.configure(api_key=self.settings.api_key)
            self._is_configured = True 
            self.logger.info("Cliente Gemini configurado com sucesso.")

        except Exception as e:
            self.logger.critical(f"Falha ao configurar a API do Gemini: {e}")



    #---------------------------------------------------------------------------------
    # Gera Texto com Gemini 
    #---------------------------------------------------------------------------------
    # Recebe: um prompt, um nome de modelo
    # Retorna: o texto gerado pelo model ou none
    #---------------------------------------------------------------------------------
    def generate_text_from_prompt(self, prompt: str, model_name: str) -> Optional[str]:
        if not self._is_configured:
            self.logger.error("Cliente Gemini não configurado. Impossível gerar texto.")
            return None

        try:
            self.logger.info(f"Gerando texto com o modelo: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Acessa o texto de forma segura
            if response.parts:
                return response.text
            else:
                # Se não houver 'parts', pode ser que a resposta foi bloqueada.
                self.logger.warning("A resposta do modelo não contém 'parts'. Pode ter sido bloqueada ou estar vazia.")
                return None

        except Exception as e:
            self.logger.error(f"Erro durante a chamada para a API Gemini: {e}", exc_info=True)
            return None

    #---------------------------------------------------------------------------------
    # Gera um Dicionário com Gemini
    #---------------------------------------------------------------------------------
    # Recebe: um prompt, um nome de modelo
    # Retorno: Retorna um dicíonario Python com os dados extraídos ou none 
    #---------------------------------------------------------------------------------
    def generate_json_from_prompt(self, prompt: str, model_name: str) -> Optional[Dict]:
        if not self._is_configured:
            self.logger.error("Cliente Gemini não configurado. Impossível gerar JSON.")
            return None

        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        try:
            self.logger.info(f"Gerando JSON com o modelo: {model_name}...")
            model = genai.GenerativeModel(model_name, generation_config=generation_config)
            response = model.generate_content(prompt)

            if not response.parts:
                 self.logger.warning("A resposta do modelo (JSON mode) não contém 'parts'. Pode ter sido bloqueada.")
                 return None

            response_text = response.text
            return json.loads(response_text)

        except json.JSONDecodeError:
            self.logger.error(f"Falha ao decodificar JSON. O modelo não retornou um JSON válido. Resposta: {response_text}")
            return None
        except Exception as e:
            self.logger.error(f"Erro durante a chamada para a API Gemini (JSON mode): {e}", exc_info=True)
            return None
        
    def generate_json_from_multimodal_prompt(
            self, 
            text_prompt: str, 
            images: List[Image.Image], 
            model_name: str
        ) -> Optional[Dict]:
            if not self._is_configured:
                self.logger.error("Cliente Gemini não configurado. Impossível gerar JSON multimodal.")
                return None
            if not images:
                self.logger.error("Nenhuma imagem fornecida para o prompt multimodal.")
                return None
    
            # Configuração para forçar a saída em JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
            
            try:
                self.logger.info(f"Gerando JSON com o modelo multimodal: {model_name}...")
                
                model = genai.GenerativeModel(model_name, generation_config=generation_config)
                
                # Constrói o conteúdo da requisição com o texto de instrução primeiro,
                # seguido pela lista de imagens das páginas do documento.
                content_parts = [text_prompt] + images
                
                response = model.generate_content(content_parts)
    
                if not response.parts:
                     self.logger.warning("A resposta do modelo multimodal não contém dados.")
                     return None
    
                response_text = response.text
                return json.loads(response_text)
    
            except json.JSONDecodeError:
                self.logger.error(f"Falha ao decodificar JSON. O modelo multimodal não retornou um JSON válido. Resposta: {response_text}")
                return None
            except Exception as e:
                self.logger.error(f"Erro durante a chamada para a API Gemini (multimodal): {e}", exc_info=True)
                return None