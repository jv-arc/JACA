import os
import json
import fitz  # PyMuPDF
import docx  # python-docx
from PIL import Image
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path


from app.core.ai_client import GeminiClient
from app.core.prompt_manager import PromptManager
from app.core.logger import Logger
from app.core.models import StructuredExtraction
from app.core.path_manager import PathManager

# Orquestra o processo de extração de dados de diferentes formatos de documentos,
# preparando o conteúdo para análise por IA (texto ou multimodal).
    
class ExtractedDataManager:

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self.prompt_manager = PromptManager()
        self.path = PathManager
        self.logger = Logger(name="ExtractedDataManager")
        
        # Era melhor tirar isso daqui
        self.workflows = {
            'estatuto': {
                'content_fields': [
                    'article_1', 'article_2', 'article_3', 'objectives',
                    'governance', 'bylaws_text', 'main_content'
                ],
                'ignored_fields': [
                    'headers', 'footers', 'page_numbers', 'signatures',
                    'stamps', 'letterhead', 'carimbo'
                ]
            },
            'ata': {
                'content_fields': [
                    'meeting_date', 'attendees', 'agenda', 'decisions',
                    'resolutions', 'meeting_content', 'main_content'
                ],
                'ignored_fields': [
                    'headers', 'footers', 'page_numbers', 'signatures',
                    'stamps', 'letterhead', 'carimbo', 'formatting'
                ]
            },
            'licenca': {
                'content_fields': [
                    'license_number', 'validity', 'conditions', 'restrictions',
                    'license_content', 'main_content'
                ],
                'ignored_fields': [
                    'headers', 'footers', 'page_numbers', 'signatures',
                    'stamps', 'letterhead', 'carimbo'
                ]
            },
            'programacao': {
                'content_fields': [
                    'schedule', 'activities', 'timeline', 'program_content',
                    'main_content'
                ],
                'ignored_fields': [
                    'headers', 'footers', 'page\_numbers', 'signatures',
                    'stamps', 'letterhead', 'carimbo'
                ]
            }
        }
        self.logger.info("Classe inicializada com sucesso.")



    # Verifica se existe texto extraído para uma categoria
    def has_extracted_text(self, project_name: str, category: str) -> bool:

        try:
            extracted_dir = self.path.get_project_extracted_dir(project_name)
            extracted_file = os.path.join(extracted_dir, f'{category}.json')
            if not os.path.exists(extracted_file):
                return False

            # Verifica se tem conteúdo útil
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Se tem consolidated_text ou pelo menos um content_field preenchido
            if data.get('consolidated_text', '').strip():
                return True
            
            content_fields = data.get('content_fields', {})
            return any(value.strip() for value in content_fields.values())
        
        except Exception as e:
            print(f'Erro ao verificar texto extraído: {e}')
            return False


    def _extract_content_from_files(self, file_paths: List[Path]) -> Dict:
        texts: List[str] = []
        images: List[Image.Image] = []
        docx_endings = [".docx", ".DOCX"]
        pdf_endings = [".pdf", ".PDF"]

        for path in file_paths:
            self.logger.info(f"Processando arquivo {os.path.basename(path)}...")
            try:
                if path.suffix in docx_endings:
                    doc = docx.Document(str(path))
                    full_text = [p.text for p in doc.paragraphs if p.text.strip()]
                    texts.append("\n".join(full_text))

                elif path.suffix in pdf_endings:
                    pdf_doc = fitz.open(path)
                    has_text_content = False
                    for page_num in range(len(pdf_doc)):
                        page = pdf_doc[page_num]
                        page_text = page.get_text()
                        if page_text.strip():
                            texts.append(page_text)
                            has_text_content = True
                        else:
                            self.logger.warning(f"Página {page_num+1} de {os.path.basename(path)} não contém texto. Tratando como imagem.")
                            pix = page.get_pixmap()
                            img = Image.frombytes(
                                "RGB", (pix.width, pix.height), pix.samples
                            )
                            images.append(img)
                    if has_text_content:
                        self.logger.info(f"PDF '{os.path.basename(path)} processado como documento de texto")
                    pdf_doc.close()

                else:
                    self.logger.warning(f"Formato não suportado: {path}")
            except Exception as e:
                self.logger.error(f"Erro ao processar {path}: {e}")

        if texts:
            return {"type": "text", "content": "\n\n".join(texts)}
        if images:
            return {"type": "images", "content": images}
        return {"type": "empty", "content": None}
    
    # ===========================================================
    # MÉTODO DE ORQUESTRAÇÃO DA EXTRAÇÃO
    # ===========================================================

    def run_extraction(self, file_paths: List[Path], category: str) -> Optional[Dict]:
        self.logger.info(f"Iniciando processo de extração para a categoria '{category}'.")

        if not file_paths:
            self.logger.warning(f"Nenhum arquivo encontrado para a categoria '{category}'. Abortando extração.")
            return None

        extracted_content = self._extract_content_from_files(file_paths)
        extracted_json = None
        workflow = self.workflows.get(category, {})
        model_name = self.gemini_client.settings.extraction_model

        if extracted_content['type'] == 'text':
            self.logger.info("Conteúdo de texto detectado. Usando o fluxo de extração textual.")
            document_text = extracted_content['content']
            prompt = self.prompt_manager.get_extraction_prompt(
                category=category,
                document_text=document_text,
                content_fields=workflow.get('content_fields', []),
                ignored_fields=workflow.get('ignored_fields', [])
            )
            extracted_json = self.gemini_client.generate_json_from_prompt(prompt, model_name)

        elif extracted_content['type'] == 'images':
            self.logger.info("Conteúdo de imagem detectado. O fluxo de extração multimodal será usado.")
            prompt = self.prompt_manager.get_multimodal_extraction_prompt(
                category=category,
                content_fields=workflow.get('content_fields', []),
                ignored_fields=workflow.get('ignored_fields', [])
            )
            images = extracted_content['content']

            if extracted_content.get('auxiliary_text'):
                prompt += "\n\n--- INFORMAÇÕES ADICIONAIS (TEXTO EXTRAÍDO) ---\n" + extracted_content['auxiliary_text']

            extracted_json = self.gemini_client.generate_json_from_multimodal_prompt(
                text_prompt=prompt,
                images=images,
                model_name=model_name
            )

        elif extracted_content['type'] == 'empty':
            self.logger.error("Nenhum conteúdo (texto ou imagem) pôde ser extraído dos arquivos.")
            return None
        
        if not extracted_json:
            self.logger.error("Falha ao extrair dados. A resposta da IA foi nula ou inválida.")
            return None
            
        self.logger.info("Extração da IA concluída. Retornando dados estruturados.")
        return extracted_json




    def consolidate_content_fields(self, contentfields: Dict[str, str]) -> str:
        useful_texts = [v.strip() for v in contentfields.values() if v and v.strip()]
        return "\n\n".join(useful_texts)





    def create_empty_extraction_data(self, category: str) -> StructuredExtraction:
        
        wf = self.workflows.get(category, {})
        return StructuredExtraction(
            content_fields={f: "" for f in wf.get("content_fields", [])},
            ignored_fields={f: "" for f in wf.get("ignored_fields", [])},
            consolidated_text="",
            workflow_used=category,
            extracted_at=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            reviewed=False
        )
    

    # Salva/atualiza texto consolidado para uma categoria
    def save_extracted_text(self, project_name: str, category: str, text: str) -> bool:

        try:
            extracted_dir = self.path.get_project_extracted_dir(project_name)
            extracted_file = os.path.join(extracted_dir, f'{category}.json')
            # Carrega dados existentes ou cria novos
            if os.path.exists(extracted_file):
                with open(extracted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = self._create_empty_extraction_data(category)
            # Atualiza texto consolidado
            data['consolidated_text'] = text
            data['last_modified'] = datetime.now().isoformat()
            data['reviewed'] = True
            # Salva de volta
            with open(extracted_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f'Erro ao salvar texto extraído: {e}')
            return False

    # Carrega texto consolidado para uma categoria
    def load_extracted_text(self, project_name: str, category: str) -> Optional[str]:
        try:
            extracted_dir = self.path.get_project_extracted_dir(project_name)
            extracted_file = os.path.join(extracted_dir, f'{category}.json')
            if not os.path.exists(extracted_file):
                return None
            with open(extracted_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('consolidated_text', '')
        except Exception as e:
            print(f'Erro ao carregar texto extraído: {e}')
            return None
        
    def _consolidate_content_fields(self, content_fields: Dict[str, str]) -> str:
        # Remove campos vazios e consolida
        useful_texts = [value.strip() for value in content_fields.values() if value.strip()]
        return '\n\\n'.join(useful_texts)
                             
    def get_workflow_fields(self, category: str) -> Dict[str, List[str]]:
        return self.workflows.get(category, self.workflows['estatuto'])


    # Cria estrutura vazia para uma categoria
    def _create_empty_extraction_data(self, category: str) -> Dict:
        workflow = self.workflows.get(category, self.workflows['estatuto'])
        return {
            'content_fields': {field: '' for field in workflow['content_fields']},
            'ignored_fields': {field: '' for field in workflow['ignored_fields']},
            'consolidated_text': '',
            'workflow_used': category,
            'extracted_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'reviewed': False
        }
    
    def _extract_text_from_pdfs(self, file_paths: List[str]) -> str:
            consolidated_text = []
            for path in file_paths:
                try:
                    with fitz.open(path) as doc:
                        self.logger.info(f"Lendo texto do arquivo: {os.path.basename(path)}")
                        for page in doc:
                            consolidated_text.append(page.get_text())
                except Exception as e:
                    self.logger.error(f"Não foi possível ler o arquivo PDF '{path}'. Erro: {e}")
            
            return "\n\n".join(consolidated_text)
    

    def save_dict_to_file(self, project_name: str, category:str, data: Dict) -> bool:
        file_obj = self.path.get_extracted_file_path(project_name, category)
        
        try: 
            file_obj.write_text(json.dump(data))
            self.logger.info(f"Dados ds categoria '{category}' para projeto '{project_name}' escritos.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao escrever dados de categoria '{category}' em '{file_obj}' para projeto '{project_name}': \n\n {e}")
            return False

    