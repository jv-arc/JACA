from google import genai
from google.genai import types

import json
from typing import Dict, Optional, List

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
            # Criar o cliente com a API key
            self.client = genai.Client(api_key=self.settings.api_key)
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
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            if response.text:
                return response.text
            else:
                self.logger.warning("A resposta do modelo não contém texto. Pode ter sido bloqueada ou estar vazia.")
                return None

        except Exception as e:
            self.logger.error(f"Erro durante a chamada para a API Gemini: \n\n {e}", exc_info=True)
            return None


    #---------------------------------------------------------------------------------
    # Gera um Dicionário com Gemini
    #---------------------------------------------------------------------------------
    # Recebe: um prompt, um nome de modelo
    # Retorno: Retorna um dicionário Python com os dados extraídos ou none 
    #---------------------------------------------------------------------------------
    def generate_json_from_prompt(self, prompt: str, model_name: str) -> Optional[Dict]:
        if not self._is_configured:
            self.logger.error("Cliente Gemini não configurado. Impossível gerar JSON.")
            return None
        
        try:
            self.logger.info(f"Gerando JSON com o modelo: {model_name}...")
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if not response.text:
                 self.logger.warning("A resposta do modelo (JSON mode) não contém texto. Pode ter sido bloqueada.")
                 return None

            response_text = response.text
            return json.loads(response_text)

        except json.JSONDecodeError:
            self.logger.error(f"Falha ao decodificar JSON. O modelo não retornou um JSON válido. Resposta: {response_text}")
            return None
        except Exception as e:
            self.logger.error(f"Erro durante a chamada para a API Gemini (JSON mode): {e}", exc_info=True)
            return None
        
    #---------------------------------------------------------------------------------
    # Gera JSON com prompt multimodal (texto + imagens)
    #---------------------------------------------------------------------------------
    def generate_json_from_multimodal_prompt(
            self, 
            text_prompt: str, 
            images: List[bytes], 
            model_name: str
        ) -> Optional[Dict]:
            if not self._is_configured:
                self.logger.error("Cliente Gemini não configurado. Impossível gerar JSON multimodal.")
                return None
            if not images:
                self.logger.error("Nenhuma imagem fornecida para o prompt multimodal.")
                return None
            
            try:
                self.logger.info(f"Gerando JSON com o modelo multimodal: {model_name}...")

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[ text_prompt,
                        [types.Part.from_bytes(data=img_bytes, mime_type='images/jpeg') for img_bytes in images]
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
    
                if not response.text:
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


        