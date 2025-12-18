
import yaml

def load_config(config_path, required_keys):
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            raise ValueError("Config file is not a valid YAML dictionary.")
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required config key: {key}")
        return config
    except Exception as e:
        raise RuntimeError(f"Error loading config: {str(e)}")
    
