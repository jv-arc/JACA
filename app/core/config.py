import json
from app.core.path_manager import PathManager

CONFIG_PATH = PathManager.get_app_config()

class Settings:

    def __init__(self):
        self.api_key = None
        self.extraction_model = None
        self.criteria_model = None
        self.debug_mode = None
        self.load_or_create_config()

    def load_or_create_config(self):
        if CONFIG_PATH.exists(): 
            try:
                json_string = CONFIG_PATH.read_text()
                data = json.loads(json_string)

                self.api_key = data.get('api_key', '')
                self.extraction_model = data.get('extraction_model', '')
                self.criteria_model = data.get('criteria_model', '')
                self.debug_mode = data.get('debug_mode', '')

            except (json.JSONDecodeError, FileNotFoundError):
                self.api_key = ''
                self.extraction_model = ''
                self.criteria_model = ''
                self.debug_mode = ''
                self.save_config()
        else:
            self.api_key = ''
            self.extraction_model = "gemini-2.5-Flash"
            self.criteria_model = "gemini-2.0-flash"
            self.debug_mode = False
            self.save_config()


    def save_config(self):
        data = {
            'api_key': self.api_key,
            'extraction_model': self.extraction_model,
            'criteria_model': self.criteria_model,
            'debug_mode': self.debug_mode
        }
        json_string = json.dumps(data, indent=2)
        CONFIG_PATH.write_text(json_string)

    def update_api_key(self, new_key):
        self.api_key = new_key
        self.save_config()


    def update_extraction_model(self, new_model: str) -> None:
        self.extraction_model = new_model
        self.save_config()

    def update_criteria_model(self, new_model: str) -> None:
        self.criteria_model = new_model
        self.save_config()

    def update_debug_mode(self, new_status: bool):
        self.debug_mode = new_status
        self.save_config() 