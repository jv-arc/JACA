import google.generativeai as genai
import json
from typing import Dict, Optional

from app.core.config import Settings

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
    def __init__(self, settings: Settings):
        if not settings.api_key:
            print("❌ Erro: API key do Gemini não encontrada nas configurações.")
            raise ValueError("A API key não pode ser vazia.")
            
        self.settings = settings
        self._is_configured = False
        try:
            genai.configure(api_key=self.settings.api_key)
            self._is_configured = True 
            print("✅ Cliente Gemini configurado com sucesso.")
        except Exception as e:
            print(f"❌ Falha ao configurar a API do Gemini: {e}")



    #---------------------------------------------------------------------------------
    # Gera Texto com Gemini 
    #---------------------------------------------------------------------------------
    # Recebe: um prompt, um nome de modelo
    # Retorna: o texto gerado pelo model ou none
    #---------------------------------------------------------------------------------
    def generate_text_from_prompt(self, prompt: str, model_name: str) -> Optional[str]:
        if not self._is_configured:
            print("❌ Cliente Gemini não está configurado. Verifique a API key.")
            return None

        try:
            print(f"⚙️  Gerando texto com o modelo: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # Acessa o texto de forma segura
            if response.parts:
                return response.text
            else:
                # Se não houver 'parts', pode ser que a resposta foi bloqueada.
                print("⚠️ A resposta do modelo não contém texto. Pode ter sido bloqueada.")
                return None

        except Exception as e:
            print(f"❌ Erro durante a chamada para a API Gemini: {e}")
            return None

    #---------------------------------------------------------------------------------
    # Gera um Dicionário com Gemini
    #---------------------------------------------------------------------------------
    # Recebe: um prompt, um nome de modelo
    # Retorno: Retorna um dicíonario Python com os dados extraídos ou none 
    #---------------------------------------------------------------------------------
    def generate_json_from_prompt(self, prompt: str, model_name: str) -> Optional[Dict]:
        if not self._is_configured:
            print("❌ Cliente Gemini não está configurado. Verifique a API key.")
            return None

        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        try:
            print(f"⚙️  Gerando JSON com o modelo: {model_name}...")
            model = genai.GenerativeModel(model_name, generation_config=generation_config)
            response = model.generate_content(prompt)

            if not response.parts:
                 print("⚠️ A resposta do modelo não contém dados. Pode ter sido bloqueada.")
                 return None

            response_text = response.text
            return json.loads(response_text)

        except json.JSONDecodeError:
            print(f"❌ Erro: O modelo não retornou um JSON válido.")
            print(f"   Resposta recebida: {response_text}")
            return None
        except Exception as e:
            print(f"❌ Erro durante a chamada para a API Gemini (JSON mode): {e}")
            return None