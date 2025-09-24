from pathlib import Path
from typing import List, Dict

#================================================================
# CLASSE: PathManager
#----------------------------------------------------------------
# Centraliza os metodos para lidar com caminhos dentro do JACA
#================================================================


class PathManager:

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Metodos para obter os caminhos principais para os diretorios 
# da aplicacao
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #-----------------------------------------------------------
    # obtem o diretorio base da aplicacao "path" (/JACA/app/)
    #-----------------------------------------------------------
    @staticmethod
    def get_app_path() -> Path:
        return Path(__file__).parent.parent

    #-------------------------------------------------------------------------
    # obtem o diretorio para os dados da aplicacao "data" (/JACA/app/data)
    #-------------------------------------------------------------------------
    @staticmethod
    def get_data_dir() -> Path:
        return PathManager.get_app_path() / "data"





    #-----------------------------------------------------------------------
    # obtem o diretorio para o codigo da aplicacao "core" (/JACA/app/core)
    #-----------------------------------------------------------------------
    @staticmethod
    def get_core_dir() -> Path:
        return PathManager.get_app_path() / "core"





    #----------------------------------------------------------------
    # obtem o diretorio para a UI da aplicacao "ui" (/JACA/app/ui)
    #----------------------------------------------------------------
    @staticmethod
    def get_ui_dir() -> Path:
        return PathManager.get_app_path() / "ui"







#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Metodos para obter os caminhos para os projetos e seus arquivos
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #-------------------------------------------------------------
    # obtem o diretorio de projetos "/JACA/app/data/projects/"
    #-------------------------------------------------------------
    @staticmethod
    def get_project_dir() -> Path :
        return PathManager.get_data_dir() / "projects"
    
    #--------------------------------------------------------------------------------
    # obtem o diretorio de um projeto especifico ".../projects/<nome do projeto>"
    #--------------------------------------------------------------------------------
    @staticmethod
    def get_project_path(project_name:str) -> Path:
        safe_project_name = "project_" + PathManager.get_safe_name(project_name) 
        return PathManager.get_project_dir() / safe_project_name





    #-----------------------------------------------------------------------------------------------
    # obtem o diretorio de arquivos de um projeto especifico ".../projects/<nome do projeto>/files"
    #-----------------------------------------------------------------------------------------------
    @staticmethod
    def get_project_files_dir(project_name: str) -> Path:
        return PathManager.get_project_path(project_name) / "files"





    #----------------------------------------------------------------------------------------------------------
    # obtem o diretorio de dados extraidos de um projeto especifico ".../projects/<nome do projeto>/extracted"
    #----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_project_extracted_dir(project_name: str) -> Path:
        return PathManager.get_project_path(project_name) / "extracted"



    #--------------------------------------------------------------------------------------------------------------
    # obtem o diretorio dos criterios avalidados de um projeto especifico ".../projects/<nome do projeto>/criteria"
    #--------------------------------------------------------------------------------------------------------------
    @staticmethod 
    def get_project_criteria_dir(project_name: str) -> Path:
        return PathManager.get_project_path(project_name) / "criteria"






    #----------------------------------------------------------------------------------------------------------
    # obtem o diretorio das exportacoes de um projeto especifico ".../projects/<nome do projeto>/exports"
    #----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_project_exports_dir(project_name: str) -> Path:
        return PathManager.get_project_path(project_name) / "exports"


    #----------------------------------------------------------------------------------------------------------
    # obtem o caminho dos metadados de um projeto especifico ".../projects/<nome do projeto>/projects.json"
    #----------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_project_json_path(project_name: str) -> Path:
        return PathManager.get_project_path(project_name) / "project.json"




    #-----------------------------------------------------------------------------------
    # retorna um dicinario com todos os caminhos para o subdiretorios de uma vez so
    #-----------------------------------------------------------------------------------
    @staticmethod
    def get_all_project_subdirs(project_name: str) -> Dict[str, Path]:
        return {
            'base': PathManager.get_project_path(project_name),
            'files': PathManager.get_project_files_dir(project_name),
            'extracted': PathManager.get_project_extracted_dir(project_name),
            'criteria': PathManager.get_project_criteria_dir(project_name),
            'exports': PathManager.get_project_exports_dir(project_name)
        }






#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Metodos para obter os caminhos para arquivos de configuracao
# da aplicacao (Em "data")
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #---------------------------------------------------------------------------
    # obtem configuracoes gerais do aplicativo "JACA/app/data/app_config.json"
    #---------------------------------------------------------------------------
    @staticmethod
    def get_app_config() -> Path:
        return PathManager.get_data_dir() / "app_config.json"




    #--------------------------------------------------------------------------------
    # obtem configuracoes gerais do aplicativo "JACA/app/data/report_config.json"
    #--------------------------------------------------------------------------------
    @staticmethod
    def get_report_config() -> Path:
        return PathManager.get_data_dir() / "report_config.json"




    #--------------------------------------------------------------------------------
    # obtem configuracoes gerais do aplicativo "JACA/app/data/criteria_dabase.json"
    #--------------------------------------------------------------------------------
    @staticmethod
    def get_criteria_database() -> Path:
        return PathManager.get_data_dir() / "criteria_database.json"






    #---------------------------------------------------------
    # obtem diretorio temporario em "JACA/app/data/temp"
    #---------------------------------------------------------
    @staticmethod
    def get_temp_dir() -> Path:
        return PathManager.get_data_dir() / "temp"







    #---------------------------------------------------------
    # obtem diretorio de logs em "JACA/app/data/logs"
    #---------------------------------------------------------
    @staticmethod
    def get_logs_dir() -> Path:
        return PathManager.get_data_dir() / "logs"





    #---------------------------------------------------------
    # obtem diretorio de backups em "JACA/app/data/backup"
    #---------------------------------------------------------
    @staticmethod
    def get_backup_dir() -> Path:
        return PathManager.get_data_dir() / "backups"
    





    #-----------------------------------------------
    # obtem o caminho para um arquivo temporario
    #-----------------------------------------------
    @staticmethod
    def get_temp_file_path(filename: str) -> Path:
        return PathManager.get_temp_dir() / PathManager.get_safe_name(filename)






#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Obtem caminhos para arquivos nos projetos
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #-------------------------------------------------------------------
    # obtem arquivo JSON com dados extraidos "extracted/{category}.json"
    #-------------------------------------------------------------------
    @staticmethod
    def get_extracted_file_path(project_name: str, category: str) -> Path:

        return PathManager.get_project_extracted_dir(project_name) / f"{category}.json"
    




    #--------------------------------------------------------------------
    # obtem arquivo com resultados dos criterios "criteria/results.json"
    #--------------------------------------------------------------------
    @staticmethod
    def get_criteria_results_path(project_name: str) -> Path:
        return PathManager.get_project_criteria_dir(project_name) / "results.json"
    




    #---------------------------------------------------------------------
    # obtem caminho para arquivo upado "files/{category}_{safe_filename}"
    #---------------------------------------------------------------------
    @staticmethod
    def get_uploaded_file_path(project_name: str, category: str, filename: str) -> Path:
        safe_filename = PathManager.get_safe_name(filename)
        return PathManager.get_project_files_dir(project_name) / f"{category}_{safe_filename}"
    





    #------------------------------------------------------------------------------
    # obtem caminho para pdf de exportacao "exports/REQUISICAO_{project_name}.pdf"
    #------------------------------------------------------------------------------
    @staticmethod
    def get_export_package_path(project_name: str) -> Path:
        return PathManager.get_project_exports_dir(project_name) / f"REQUISICAO_{project_name}.pdf"







#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Obtem caminhos para assets
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #-------------------------------------------
    # Obtem caminho para diretorio de assets
    #-------------------------------------------
    @staticmethod
    def get_assets_dir() -> Path:
        return PathManager.get_app_path() / "assets"
    



    #-----------------------------------------------------------
    # Obtem arquivo especifico dentro do diretorio de assets
    #-----------------------------------------------------------
    @staticmethod
    def get_asset(asset_name: str) -> Path:
        return PathManager.get_assets_dir() / asset_name




    #----------------------------------------------
    # Converte Path em string para acessibilidade 
    #----------------------------------------------
    @staticmethod
    def get_asset_str(asset_name: str) -> str:
        return str(PathManager.get_asset(asset_name))





#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Caminhos da UI
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #------------------------------------------
    # Obtem caminho para diretorio de paginas
    #------------------------------------------
    @staticmethod
    def get_page_dir() -> Path:
        return PathManager.get_ui_dir() / "pages"
    



    #----------------------------------------------------------------
    # Obtem caminho para uma pagina especifica no formato de string
    #----------------------------------------------------------------
    @staticmethod
    def get_page_str(page_name: str) -> str:
        page_obj = PathManager.get_page_dir() / page_name
        return str(page_obj)





#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Utilitarios e Validacao
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    

    #------------------------------------------------------
    # obtem todos os arquivos de uma determinada categoria
    #------------------------------------------------------
    @staticmethod
    def get_files_in_category(project_name: str, category: str) -> List[Path]:
        files_dir = PathManager.get_project_files_dir(project_name)
        if not files_dir.exists():
            return []
        
        pattern = f"{category}_*"
        return list(files_dir.glob(pattern))
    



    #------------------------------------------------
    # extrai o nome do projeto a partir do diretorio
    #------------------------------------------------
    @staticmethod
    def extract_project_name_from_path(project_path: Path) -> str:
        safe_name = project_path.name
        if safe_name.startswith("project_"):
            return safe_name[8:]
        return safe_name
    



    #-------------------------------------------------
    # Verifica se o projeto tem a estrutura adequada
    #-------------------------------------------------
    @staticmethod
    def is_valid_project_structure(project_name: str) -> bool:
        project_json = PathManager.get_project_json_path(project_name)
        return project_json.exists()




    #--------------------------------------------
    # gera nomes seguros para arquivos e pastas
    #--------------------------------------------
    @staticmethod
    def get_safe_name(name: str) -> str:
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        safe_name = "".join(c if c in safe_chars else "_" for c in name)
        return safe_name




    #---------------------------------------------------
    # valida nome do projeto para o sistema de arquivos
    #---------------------------------------------------
    @staticmethod
    def validate_project_name(project_name: str) -> bool:
        if not project_name or len(project_name.strip()) == 0:
            return False
        if len(project_name) > 100:
            return False
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        return not any(char in project_name for char in invalid_chars)





    #--------------------------------------------------
    # verifica se o caminho esta na pasta de projetos
    #--------------------------------------------------
    @staticmethod
    def is_under_projects_dir(target_path: Path) -> bool:
        try:
            target_path.resolve().relative_to(PathManager.get_project_dir().resolve())
            return True
        except ValueError:
            return False




    #--------------------------------------
    # gera um nome unico usando timestamp
    #--------------------------------------
    @staticmethod
    def generate_unique_filename(base_name: str, extension: str = '') -> str:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_base = PathManager.get_safe_name(base_name)
        return f"{safe_base}_{timestamp}{extension}"




    #---------------------------------
    # extrai extensao com seguranca
    #---------------------------------
    @staticmethod
    def get_file_extension(filename: str) -> str:
        return Path(filename).suffix.lower()

