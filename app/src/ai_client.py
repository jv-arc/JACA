# src/ai/gemini_client.py
import google.generativeai as genai
import json
from typing import Dict, Optional

from src.config.settings import Settings

class GeminiClient:
    """
    Uma classe cliente para interagir com a API do Google Gemini.
    
    Esta classe lida com a configuração da API, seleção de modelos e
    envio de prompts, retornando as respostas do modelo.
    """

    def __init__(self, settings: Settings):
        """
        Inicializa o cliente Gemini.

        Args:
            settings (Settings): Um objeto de configuração que contém a API key
                                 e os nomes dos modelos.
        
        Raises:
            ValueError: Se a API key não for fornecida nas configurações.
        """
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

    def generate_text_from_prompt(self, prompt: str, model_name: str) -> Optional[str]:
        """
        Gera texto a partir de um prompt usando um modelo Gemini específico.

        Args:
            prompt (str): O prompt a ser enviado para o modelo.
            model_name (str): O nome do modelo a ser usado (ex: "gemini-1.5-flash").

        Returns:
            Optional[str]: O texto gerado pelo modelo, ou None em caso de falha.
        """
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

    def generate_json_from_prompt(self, prompt: str, model_name: str) -> Optional[Dict]:
        """
        Gera uma saída JSON estruturada a partir de um prompt.

        Utiliza o modo JSON da API do Gemini para garantir que a resposta
        seja um objeto JSON válido.

        Args:
            prompt (str): O prompt, que deve instruir o modelo a retornar JSON.
            model_name (str): O nome do modelo a ser usado.

        Returns:
            Optional[Dict]: Um dicionário Python com os dados extraídos, 
                            ou None em caso de falha.
        """
        if not self._is_configured:
            print("❌ Cliente Gemini não está configurado. Verifique a API key.")
            return None

        # Configuração para forçar a saída em JSON
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

            # Tenta carregar a resposta de texto como JSON
            response_text = response.text
            return json.loads(response_text)

        except json.JSONDecodeError:
            print(f"❌ Erro: O modelo não retornou um JSON válido.")
            print(f"   Resposta recebida: {response_text}")
            return None
        except Exception as e:
            print(f"❌ Erro durante a chamada para a API Gemini (JSON mode): {e}")
            return None