import os
import yaml

def load_config(path="config.yaml"):
    """
    Load config from a YAML file and override any <task>_project_directory
    if the corresponding <TASK>_PROJECT_ID environment variable is set.
    """
    # 1) Load defaults from YAML
    with open(path) as f:
        cfg = yaml.safe_load(f)

    # 2) Override <task>_project_directory keys if env var exists
    for key in list(cfg.keys()):
        if key.endswith("_project_directory"):
            # Extract the task name (e.g., "blaster" from "blaster_project_directory")
            task = key[:-len("_project_directory")]
            # Build the environment variable name, replacing hyphens with underscores
            env_var = f"{task.replace('-', '_').upper()}_PROJECT_ID"
            override = os.getenv(env_var)
            if override:
                cfg[key] = override
    return cfg
