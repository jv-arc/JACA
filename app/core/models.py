from pydantic import BaseModel
from typing import List, Dict, Optional
import json

# Estrutura para dados extraídos com campos estruturados
class StructuredExtraction(BaseModel):  
    content_fields: Dict[str, str] = {}
    ignored_fields: Dict[str, str] = {}
    consolidated_text: str = ""
    workflow_used: str = ""
    extracted_at: Optional[str] = None
    last_modified: Optional[str] = None
    reviewed: bool = False

# Container para todos os dados extraídos do projeto
class ExtractedDataType(BaseModel):
    estatuto: Optional[StructuredExtraction] = None
    ata: Optional[StructuredExtraction] = None
    identificacao: Optional[Dict] = None  # Estrutura diferente para identificações
    licenca: Optional[StructuredExtraction] = None
    programacao: Optional[StructuredExtraction] = None

# Container para os dados do projeto
class ProjectState(BaseModel):
    name: str
    path: Optional[str] = None 
    base_files: Dict = {}
    extracted_data: Optional[ExtractedDataType] = None
    criteria_results: Dict = {}
    current_step: int = 1 
    created_at: str
    last_modified: str
    
    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.model_dump(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, path: str):
        with open(path, 'r') as f:
            return cls(**json.load(f))
