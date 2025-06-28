import json
import os
import configparser

def load_project_data():
    """Load project files data from JSON"""
    with open("config/project_files.json", "r") as json_file:
        return json.load(json_file)

def load_script_data():
    """Load script files data from JSON"""
    with open("config/scripts.json", "r") as json_file:
        return json.load(json_file)

def load_extension_data():
    """Load extension files data from JSON"""
    with open("config/extensions.json", "r") as json_file:
        return json.load(json_file)

def load_presets_data():
    """Load presets data from JSON"""
    with open("config/presets.json", "r") as presets_file:
        return json.load(presets_file)

def load_bot_config():
    """Load bot configuration from ryujin.json"""
    with open('config/ryujin.json') as json_file:
        data = json.load(json_file)
        for p in data['settings']:
            return {
                'token': p['token'],
                'stats_channel': p['stats-channel'],
                'info_channel': p['info-channel'],
                'welcome_leave_channel': p['welcome-leave-channel']
            }

def load_removebg_config():
    """Load remove background API configuration"""
    config_path = os.path.join("config", "removebg-api.json")
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        return config.get("api_keys", [])

def load_messages_config():
    """Load messages configuration"""
    with open('config/messages.json', 'r') as f:
        return json.load(f)

def save_messages_config(config):
    """Save messages configuration"""
    with open('config/messages.json', 'w') as f:
        json.dump(config, f, indent=4)

def count_presets_in_categories():
    """Count presets in each category"""
    presets_data = load_presets_data()
    presetscategories = presets_data.get("presetscategories", {})
    category_counts = {}
    for category_name, folder_name in presetscategories.items():
        folder_path = os.path.join("resources/presets", folder_name)
        assets = [f for f in os.listdir(folder_path) if f.endswith(".ffx")]
        category_counts[category_name] = len(assets)
    
    return category_counts 