import os
import fitz  # PyMuPDF
from typing import Dict, List

from app.core.logger import Logger
from app.core.models import ProjectState
from app.core.pdf_generator import PdfGenerator
from app.core.report_config_manager import ReportConfigManager



class ExportManager:

    def __init__(
        self,
        logger: Logger,
        pdf_generator: PdfGenerator,
        report_config_manager: ReportConfigManager
    ):
        self.logger = logger
        self.pdf_generator = pdf_generator
        self.report_config_manager = report_config_manager
        self.logger.info("ExportManager inicializado.")

    def _get_project_source_pdfs(self, project_data: ProjectState) -> List[str]:
        """
        Coleta uma lista de todos os caminhos de PDF originais do projeto.
        """
        all_files = []
        if project_data and project_data.base_files:
            for category_files in project_data.base_files.values():
                for file_path in category_files:
                    if file_path.lower().endswith('.pdf'):
                        all_files.append(file_path)
        
        self.logger.info(f"Encontrados {len(all_files)} arquivos PDF de origem no projeto.")
        return all_files

    def generate_full_package(
        self,
        project_data: ProjectState,
        user_overrides: Dict,
        export_dir: str
    ) -> str:
        
        project_name = project_data.name
        self.logger.info(f"Iniciando geração do pacote de exportação para o projeto '{project_name}'.")

        # 1. Gerar o PDF do formulário de requisição
        form_pdf_path = os.path.join(export_dir, f"temp_form_{project_name}.pdf")
        report_config = self.report_config_manager.get_full_config()

        success = self.pdf_generator.create_request_pdf(
            project_data=project_data,
            report_config=report_config,
            user_overrides=user_overrides,
            output_path=form_pdf_path
        )

        if not success:
            self.logger.error("Falha ao gerar o PDF do formulário. Abortando a exportação.")
            raise IOError("Não foi possível gerar o PDF do formulário de requisição.")

        # 2. Coletar todos os outros PDFs do projeto
        source_pdfs = self._get_project_source_pdfs(project_data)
        
        # 3. Concatenar todos os PDFs em um único arquivo
        final_pdf_path = os.path.join(export_dir, f"REQUISICAO_{project_name}.pdf")
        
        try:
            self.logger.info(f"Concatenando {len(source_pdfs) + 1} PDFs em um único arquivo...")
            final_doc = fitz.open()  # Cria um novo documento PDF vazio
            
            # Adiciona o formulário primeiro
            final_doc.insert_pdf(fitz.open(form_pdf_path))
            
            # Adiciona os documentos do usuário
            for pdf_path in source_pdfs:
                if os.path.exists(pdf_path):
                    final_doc.insert_pdf(fitz.open(pdf_path))
                else:
                    self.logger.warning(f"Arquivo PDF de origem não encontrado e será pulado: {pdf_path}")
            
            # Salva o resultado final
            final_doc.save(final_pdf_path)
            final_doc.close()
            self.logger.info(f"Pacote de requisição final salvo com sucesso em: {final_pdf_path}")
            
            return final_pdf_path
            
        except Exception as e:
            self.logger.error(f"Falha ao concatenar os PDFs: {e}", exc_info=True)
            raise IOError("Ocorreu um erro ao unir os documentos PDF.")
        finally:
            # Limpa o arquivo de formulário temporário
            if os.path.exists(form_pdf_path):
                os.remove(form_pdf_path)