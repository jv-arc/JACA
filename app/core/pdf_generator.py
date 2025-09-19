import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from fpdf import FPDF, XPos, YPos
from app.core.logger import Logger
from app.core.models import ProjectState

class DataResolver:
    """
    Classe auxiliar para resolver e formatar os dados que preencherão o PDF.
    """
    def __init__(self,
                 projectdata: ProjectState,
                 reportconfig: Dict,
                 useroverrides: Dict,
                 logger: Logger):
        self.projectdata = projectdata
        self.reportconfig = reportconfig
        self.useroverrides = useroverrides
        self.logger = logger
        self.resolvedcache: Dict[str, Any] = {}
        self._prepare_dynamic_placeholders()

    def _prepare_dynamic_placeholders(self):
        # Prepara placeholders que não dependem dos dados do projeto
        self.resolvedcache["dataatual"] = datetime.now().strftime("%d de %B de %Y")
        mun_text = self.getvalue("municipiotransmissor", "")
        self.resolvedcache["cidaderequerimento"] = mun_text.split()[0] if mun_text else ""
        self.resolvedcache["nomerepresentantelegal"] = self.getvalue("nomefantasia", "")
        self.resolvedcache["nometecnicoresponsavel"] = self.getvalue("nometecnicoresponsavel", "")
        self.resolvedcache["createcnico"] = self.getvalue("createcnico", "")

    def _find_field_in_config(self, fieldlabel: str) -> Dict:
        # Busca o objeto de field config pelo label
        for table in self.reportconfig.get("tables", []):
            for field in table.get("fields", []):
                if field.get("label") == fieldlabel:
                    return field
        return {}

    def getvalue(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor na seguinte ordem de prioridade:
        1. Cache de placeholders
        2. Input do usuário (useroverrides)
        3. Dados extraídos do projeto
        4. Valor padrão
        """
        if key in self.resolvedcache:
            return self.resolvedcache[key]

        if key in self.useroverrides:
            return self.useroverrides[key]

        # Dados extraídos
        try:
            if "." in key:
                docname, fieldname = key.split(".", 1)
                docdata = getattr(self.projectdata.extracteddata, docname, None)
                if docdata:
                    value = docdata.contentfields.get(fieldname)
                    if value:
                        return value
        except Exception:
            self.logger.warning(f"Não foi possível resolver a datakey {key}")

        return default

    def formattext(self, text: str) -> str:
        """
        Substitui placeholders no texto.
        """
        result = text
        for ph, val in self.resolvedcache.items():
            result = result.replace(f"{{{{{ph}}}}}", str(val))
        return result


class PdfGenerator(FPDF):
    """
    Gera o PDF da requisição, herdando de FPDF para customização.
    """
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.set_auto_page_break(auto=True, margin=25)
        # Fontes com suporte Unicode
        self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 10, "Requerimento de Outorga - RadCom", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def _draw_title(self, title: str):
        self.set_font("DejaVu", "B", 14)
        self.multi_cell(0, 10, title, align="C")
        self.ln(10)

    def _draw_table(self, tableconf: Dict, resolver: DataResolver):
        # Título da tabela
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, tableconf["header"], border="B", ln=1)
        self.ln(5)

        for field in tableconf.get("fields", []):
            label = field["label"]
            key = field.get("id") or field.get("datakey")
            default = field.get("default", "")
            value = resolver.getvalue(key, default)

            self.set_font("DejaVu", "B", 10)
            self.cell(50, 6, f"{label}:", ln=0)
            self.set_font("DejaVu", "", 10)
            self.multi_cell(0, 6, str(value))
            self.ln(2)

        self.ln(8)

    def _write_formatted_text(self, text: str, resolver: DataResolver):
        formatted = resolver.formattext(text)
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 7, formatted, align="J")
        self.ln(10)

    def create_request_pdf(self,
                           projectdata: ProjectState,
                           reportconfig: Dict,
                           useroverrides: Dict,
                           outputpath: str) -> bool:
        """
        Método principal que cria e salva o PDF completo.
        """
        try:
            resolver = DataResolver(projectdata, reportconfig, useroverrides, self.logger)

            # Página inicial
            self.set_title(reportconfig.get("requesttitle", "Requerimento"))
            self.add_page()

            # Título principal
            self._draw_title(reportconfig.get("requesttitle", ""))

            # Tabelas configuradas
            for tableconf in reportconfig.get("tables", []):
                self._draw_table(tableconf, resolver)

            # Texto boilerplate
            self._write_formatted_text(reportconfig.get("boilerplatetext", ""), resolver)

            # Declaração final e assinaturas
            final = reportconfig.get("finaldeclaration", {})
            self.set_font("DejaVu", "B", 12)
            self.cell(0, 10, final.get("header", ""), ln=1, align="C")
            self.ln(5)
            self._write_formatted_text(final.get("text", ""), resolver)
            self.ln(15)
            self._write_formatted_text(final.get("signaturelocationdate", ""), resolver)
            self.ln(10)
            self._write_formatted_text(final.get("signatureline1", ""), resolver)
            self.ln(10)
            self._write_formatted_text(final.get("signatureline2", ""), resolver)

            # Salvar arquivo
            os.makedirs(os.path.dirname(outputpath), exist_ok=True)
            self.output(outputpath)
            self.logger.info(f"PDF gerado e salvo com sucesso em {outputpath}")
            return True

        except Exception as e:
            self.logger.error("Falha ao gerar o PDF", exc_info=True)
            return False
