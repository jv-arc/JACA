import os
import json
import fitz  # PyMuPDF
import docx  # python-docx
from PIL import Image
from datetime import datetime
from typing import Optional, Dict, List

from src.ai_client import GeminiClient
from src.prompt_manager import PromptManager
from src.logger import Logger
from src.models import StructuredExtraction

class ExtractedDataManager:
    """
    Orquestra o processo de extração de dados de diferentes formatos de documentos,
    preparando o conteúdo para análise por IA (texto ou multimodal).
    """

    WORKFLOWS = {
        "estatuto": {
            "contentfields": [
                "article1", "article2", "article3",
                "objectives", "governance", "bylawstext", "maincontent"
            ],
            "ignoredfields": [
                "headers", "footers", "pagenumbers",
                "signatures", "stamps", "letterhead", "carimbo"
            ],
        },
        "ata": {
            "contentfields": [
                "meetingdate", "attendees", "agenda",
                "decisions", "resolutions", "meetingcontent", "maincontent"
            ],
            "ignoredfields": [
                "headers", "footers", "pagenumbers",
                "signatures", "stamps", "letterhead", "carimbo", "formatting"
            ],
        },
        # outros workflows...
    }

    def __init__(
        self,
        gemini_client: GeminiClient,
        prompt_manager: PromptManager,
        logger: Logger
    ):
        self.geminiclient = gemini_client
        self.promptmanager = prompt_manager
        self.logger = logger
        self.logger.info("ExtractedDataManager com suporte a múltiplos formatos inicializado.")

    def extractcontentfromfiles(self, filepaths: List[str]) -> Dict:
        """
        Extrai conteúdo de uma lista de arquivos (.pdf ou .docx),
        diferenciando entre texto puro e imagens de páginas escaneadas.
        Retorna dict com keys: type ('text', 'images', 'empty'), content e auxiliarytext.
        """
        texts: List[str] = []
        images: List[Image.Image] = []

        for path in filepaths:
            self.logger.info(f"Processando arquivo {os.path.basename(path)}...")
            try:
                if path.lower().endswith(".docx"):
                    doc = docx.Document(path)
                    fulltext = [p.text for p in doc.paragraphs if p.text.strip()]
                    texts.extend(fulltext)

                elif path.lower().endswith(".pdf"):
                    pdf = fitz.open(path)
                    for page in pdf:
                        text = page.get_text()
                        if text.strip():
                            texts.append(text)
                        else:
                            pix = page.get_pixmap()
                            img = Image.frombytes(
                                "RGB", [pix.width, pix.height], pix.samples
                            )
                            images.append(img)
                    pdf.close()

                else:
                    self.logger.warning(f"Formato não suportado: {path}")
            except Exception as e:
                self.logger.error(f"Erro ao processar {path}: {e}")

        if texts:
            return {"type": "text", "content": "\n\n".join(texts)}
        if images:
            return {"type": "images", "content": images}
        return {"type": "empty", "content": None}

    def runextraction(self, filepaths: List[str], category: str) -> Optional[Dict]:
        """
        Executa o fluxo de extração completo para uma lista de arquivos,
        retornando o JSON extraído pela IA (sem salvar em disco).
        """
        self.logger.info(f"Iniciando extração para categoria '{category}'...")
        if not filepaths:
            self.logger.warning(f"Nenhum arquivo fornecido para a categoria '{category}'.")
            return None

        extracted = self.extractcontentfromfiles(filepaths)
        wf = self.WORKFLOWS.get(category, {})
        model = self.geminiclient.settings.extractionmodel

        if extracted["type"] == "text":
            prompt = self.promptmanager.getextractionprompt(
                category, extracted["content"], wf["contentfields"], wf["ignoredfields"]
            )
            return self.geminiclient.generatejsonfromprompt(prompt, model)

        elif extracted["type"] == "images":
            prompt = self.promptmanager.getmultimodalextractionprompt(
                category, wf["contentfields"], wf["ignoredfields"]
            )
            # opcional: texto auxiliar, se disponível
            aux = extracted.get("auxiliarytext", "")
            return self.geminiclient.generatejsonfrommultimodalprompt(
                prompt, extracted["content"], aux, model
            )

        else:
            self.logger.error("Nenhum conteúdo extraível encontrado nos arquivos.")
            return None

    def consolidatecontentfields(self, contentfields: Dict[str, str]) -> str:
        """
        Concatena os valores não vazios de contentfields em um único texto.
        """
        useful_texts = [v.strip() for v in contentfields.values() if v and v.strip()]
        return "\n\n".join(useful_texts)

    def createemptyextractiondata(self, category: str) -> StructuredExtraction:
        """
        Gera um objeto StructuredExtraction vazio para a categoria informada.
        """
        wf = self.WORKFLOWS.get(category, {})
        return StructuredExtraction(
            contentfields={f: "" for f in wf.get("contentfields", [])},
            ignoredfields={f: "" for f in wf.get("ignoredfields", [])},
            consolidatedtext="",
            workflowused=category,
            extractedat=datetime.now().isoformat(),
            lastmodified=datetime.now().isoformat(),
            reviewed=False
        )
