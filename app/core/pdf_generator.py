import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from fpdf import FPDF, XPos, YPos
from app.core.logger import Logger
from app.core.models import ProjectState
from app.core.path_manager import PathManager

class _DataResolver:
    def __init__(self, project_data: ProjectState, report_config: Dict, user_overrides: Dict, logger: Logger):
        self.project_data = project_data
        self.report_config = report_config
        self.user_overrides = user_overrides
        self.logger = logger
        self.resolved_cache = {}
        self._prepare_dynamic_placeholders()

    def _prepare_dynamic_placeholders(self):
        """Prepara placeholders que não dependem dos dados do projeto."""
        self.resolved_cache['data_atual'] = datetime.now().strftime('%d de %B de %Y')
        self.resolved_cache['cidade_requerimento'] = self.get_value('municipio_transmissor').split('/')[0]

        # Busca e armazena os nomes para as assinaturas
        self.resolved_cache['nome_representante_legal'] = self.get_value_from_config("Representante Legal (Presidente)")
        self.resolved_cache['nome_tecnico_responsavel'] = self.get_value('nome_tecnico_responsavel', "____________________")
        self.resolved_cache['crea_tecnico'] = self.get_value('crea_tecnico', "____________________")


    def get_value_from_config(self, field_label: str, default_override: Any = None) -> Any:
        """Busca um valor com base na sua label na configuração."""
        all_tables = self.report_config.get('tables', [])
        for table in all_tables:
            for field in table.get('fields', []):
                if field.get('label') == field_label:
                    return self.get_value(field.get('id') or field.get('data_key'), field.get('default'))
        return default_override or f"CAMPO '{field_label}' NÃO ENCONTRADO"

    def get_value(self, key: str, default: Any = "Não informado") -> Any:
        """
        Obtém um valor na seguinte ordem de prioridade:
        1. Cache de valores já resolvidos.
        2. Input do usuário (`user_overrides`).
        3. Dados extraídos do projeto (`project_data`).
        4. Valor padrão (`default`).
        """
        if key in self.resolved_cache:
            return self.resolved_cache[key]

        # 1. Prioridade máxima: input do usuário no formulário
        if key in self.user_overrides and self.user_overrides[key]:
            return self.user_overrides[key]

        # 2. Dados extraídos
        if '.' in key: # Indica um caminho como 'estatuto.main_content.cnpj'
            try:
                doc_name, field_group, field_name = key.split('.')
                doc_data = getattr(self.project_data.extracted_data, doc_name, None)
                if doc_data and hasattr(doc_data, 'content_fields'):
                    value = doc_data.content_fields.get(field_name)
                    if value:
                        return value
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Não foi possível resolver a data_key '{key}': {e}")
        
        # 3. Valor padrão
        return default
        
    def format_text(self, text: str) -> str:
        """Substitui placeholders como {chave} no texto."""
        placeholders = [p.strip('{}') for p in text.split() if p.startswith('{') and p.endswith('}')]
        for p in placeholders:
            resolved_value = str(self.get_value(p))
            text = text.replace(f'{{{p}}}', resolved_value)
        return text

class PdfGenerator(FPDF):
    """
    Gera o PDF da requisição, herdando de FPDF para customização.
    """
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self.set_auto_page_break(auto=True, margin=25)
        self.add_font("DejaVu", "", PathManager.get_asset_str("DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", PathManager.get_asset_str("DejaVuSans-Bold.ttf"))

    def header(self):
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 10, "Requerimento de Outorga - RadCom", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    def _draw_title(self, title: str):
        self.set_font("DejaVu", "B", 14)
        self.multi_cell(0, 10, title, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def _draw_table(self, table_config: Dict, resolver: _DataResolver):
        # Título da tabela
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, table_config['header'], border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.ln(5)

        # Campos da tabela
        for field in table_config.get('fields', []):
            label = field['label']
            value_key = field.get('id') or field.get('data_key')
            value = resolver.get_value(value_key, field.get('default'))

            self.set_font("DejaVu", "B", 10)
            self.multi_cell(50, 6, f"{label}:")
            
            self.set_xy(self.get_x() + 50, self.get_y() - 6)
            
            self.set_font("DejaVu", "", 10)
            self.multi_cell(0, 6, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2) # Espaçamento entre linhas
        self.ln(8)

    def _write_formatted_text(self, text: str, resolver: _DataResolver):
        formatted_text = resolver.format_text(text)
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 7, formatted_text, align='J', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def create_request_pdf(
        self,
        project_data: ProjectState,
        report_config: Dict,
        user_overrides: Dict,
        output_path: str
    ) -> bool:
        """
        Método principal que cria e salva o PDF completo.
        """
        self.logger.info(f"Iniciando geração de PDF para '{output_path}'...")
        try:
            resolver = _DataResolver(project_data, report_config, user_overrides, self.logger)
            self.set_title(report_config.get("request_title", "Requerimento"))
            self.add_page()

            # Desenha o título principal
            self._draw_title(report_config.get("request_title", ""))

            # Desenha as tabelas
            for table_conf in report_config.get('tables', []):
                self._draw_table(table_conf, resolver)

            # Escreve o texto padrão (boilerplate)
            self._write_formatted_text(report_config.get('boilerplate_text', ""), resolver)

            # Desenha a declaração final e assinaturas
            final_decl = report_config.get('final_declaration', {})
            self.set_font("DejaVu", "B", 12)
            self.cell(0, 10, final_decl.get('header', ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            self.ln(5)
            self._write_formatted_text(final_decl.get('text', ""), resolver)
            
            self.ln(15) # Espaço para assinaturas
            self._write_formatted_text(final_decl.get('signature_location_date', ""), resolver)
            self.ln(10)
            self._write_formatted_text(final_decl.get('signature_line_1', ""), resolver)
            self.ln(10)
            self._write_formatted_text(final_decl.get('signature_line_2', ""), resolver)
            
            # Salva o arquivo
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.output(output_path)
            self.logger.info(f"PDF gerado e salvo com sucesso em '{output_path}'.")
            return True
        except Exception as e:
            self.logger.error(f"Falha ao gerar o PDF: {e}", exc_info=True)
            return False