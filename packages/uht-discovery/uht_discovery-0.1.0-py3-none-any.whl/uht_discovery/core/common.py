import os 

def project_dir(task_key, cfg):
    env = f"{task_key.upper()}_PROJECT_ID"
    return os.getenv(env) or cfg.get(f"{task_key}_project_directory", "")
