import os
import fitz  # PyMuPDF
from typing import Dict, Optional
from src.logger import Logger
from src.pdf_generator import PdfGenerator
from src.report_config_manager import ReportConfigManager


class ExportManager:
    """
    Orquestração de exportação de requisições.
    Gera o PDF de formulário, concatena com documentos do usuário
    e produz o pacote final para download.
    """

    def __init__(
        self,
        logger: Logger,
        pdf_generator: PdfGenerator,
        report_config_manager: ReportConfigManager,
    ):
        self.logger = logger
        self.pdf_generator = pdf_generator
        self.report_config_manager = report_config_manager

    def generate_full_package(
        self,
        project_data,
        user_overrides: Dict,
        export_dir: str,
    ) -> Optional[str]:
        """
        1. Gera o PDF do formulário de requisição.
        2. Coleta todos os PDFs de entrada do projeto.
        3. Concatena o formulário e os demais PDFs em um único PDF.
        4. Retorna o caminho para o pacote final.
        """
        # 1. Preparar diretório de exportação
        os.makedirs(export_dir, exist_ok=True)

        # 2. Carregar configurações de relatório
        report_config = self.report_config_manager.get_full_config()

        # 3. Gerar formulário preenchido
        form_path = os.path.join(export_dir, f"REQUISICAO_{project_data.name}.pdf")
        try:
            self.logger.info(f"Gerando formulário de requisição em {form_path}")
            success = self.pdf_generator.create_request_pdf(
                project_data,
                report_config,
                user_overrides,
                output_path=form_path,
            )
            if not success:
                self.logger.error("Falha ao gerar o PDF do formulário")
                return None
        except Exception as e:
            self.logger.error("Erro ao gerar formulário de requisição", exc_info=True)
            return None

        # 4. Coletar PDFs de entrada do projeto (estatuto, ata, etc.)
        source_pdfs = project_data.get_all_pdf_paths()

        # 5. Concatena o formulário e os demais PDFs
        final_path = os.path.join(export_dir, f"PACOTE_FINAL_{project_data.name}.pdf")
        try:
            self.logger.info(f"Concatenando {len(source_pdfs)+1} PDFs em {final_path}")
            final_doc = fitz.open()  # PDF vazio

            # 5.1 Inserir formulário primeiro
            final_doc.insert_pdf(fitz.open(form_path))

            # 5.2 Inserir demais PDFs
            for pdf_path in source_pdfs:
                if os.path.exists(pdf_path):
                    final_doc.insert_pdf(fitz.open(pdf_path))
                else:
                    self.logger.warning(f"Arquivo de origem não encontrado: {pdf_path}")

            final_doc.save(final_path)
            final_doc.close()
            self.logger.info(f"Pacote final salvo em {final_path}")
            return final_path

        except Exception as e:
            self.logger.error("Falha ao concatenar os PDFs", exc_info=True)
            return None
