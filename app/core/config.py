import json
from app.core.path_manager import PathManager

class _Settings:

    def __init__(self, file_path):
        self.api_key = ''
        self.extraction_model = ''
        self.criteria_model = ''
        self.debug_mode = False
        self.config_path = file_path

        if not self.config_path.exists() :
            self.config_path.touch()

        try:
            self.load_config()
        except:
            self.create_empty_config()
            self.load_config()


    def create_empty_config(self) -> None:    
        self.api_key = ''
        self.extraction_model = "gemini-2.5-Flash"
        self.criteria_model = "gemini-2.0-flash"
        self.debug_mode = False
        self.save_config()

    
    def load_config(self) -> None:
        json_string = self.config_path.read_text()
        data = json.loads(json_string)
        self.api_key = data.get('api_key', '')
        self.extraction_model = data.get('extraction_model', '')
        self.criteria_model = data.get('criteria_model', '')
        self.debug_mode = data.get('debug_mode', '')
    

    def save_config(self) -> None:
        data = {
            'api_key': self.api_key,
            'extraction_model': self.extraction_model,
            'criteria_model': self.criteria_model,
            'debug_mode': self.debug_mode
        }
        json_string = json.dumps(data, indent=2)
        self.config_path.write_text(json_string)

    def update_api_key(self, new_key: str) -> None:
        self.api_key = new_key
        self.save_config()

    def update_extraction_model(self, new_model: str) -> None:
        self.extraction_model = new_model
        self.save_config()

    def update_criteria_model(self, new_model: str) -> None:
        self.criteria_model = new_model
        self.save_config()

    def update_debug_mode(self, new_status: bool) -> None:
        self.debug_mode = new_status
        self.save_config()

settings = _Settings(PathManager.get_app_config())