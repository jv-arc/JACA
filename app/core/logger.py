import logging
import sys
from logging.handlers import RotatingFileHandler

#=================================================================================
# CLASS: Logger
#---------------------------------------------------------------------------------
# Uma classe wrapper para o módulo logging do Python.
# Configura um logger para exibir logs no console e, opcionalmente, em um arquivo.
#=================================================================================
    
class Logger:
    
    def __init__(self, name: str):
        self.name = name
        self.logfile = "/home/jvctr/0/NOW/JACA/app/core/log.txt"
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        
        # Evita adicionar handlers duplicados se a instância for criada múltiplas vezes
        if not self.logger.handlers:
            # Handler para o Console
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            stream_handler.setFormatter(stream_format)
            self.logger.addHandler(stream_handler)
            
            # Handler para Arquivo (com rotação)
            if self.logfile:
                file_handler = RotatingFileHandler(
                    self.logfile, 
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
                file_format = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
                )
                file_handler.setFormatter(file_format)
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str):
        self.logger.critical(message)