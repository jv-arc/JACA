from pathlib import Path

def get_app_path():
    return Path(__file__).parent.parent

def get_data_dir():
    return get_app_path() / "data"

def get_src_dir():
    return get_app_path() / "src"

def get_project_path():
    return get_data_dir() / "projects"

def get_app_config():
    return get_data_dir() / "app_config.json"

def get_report_config():
    return get_data_dir() / "report_config.json"

def get_criteria_database():
    return get_data_dir() / "criteria_database.json"