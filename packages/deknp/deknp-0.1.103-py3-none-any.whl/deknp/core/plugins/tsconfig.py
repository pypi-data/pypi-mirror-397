import os
import json
from .base import Plugin


class PluginTsconfig(Plugin):
    dek_key_tsconfig = 'tsconfig.json'
    vue_config_marker = '//@marker-config-add'

    def run(self):
        files = []
        keys = self.dek_key_tsconfig.rsplit('.', 1)
        keys[0] += '.'
        keys[1] = '.' + keys[1]
        for file in os.listdir(self.project_dir):
            if len(file) > len(self.dek_key_tsconfig) and file.startswith(keys[0]) and file.endswith(keys[-1]):
                if os.path.isfile(os.path.join(self.project_dir, file)):
                    files.append(file)
        data = {
            "files": [],
            "references": [
                {"path": f"./{file}"} for file in files
            ]
        }
        self.save_text(self.tsconfig_filepath, json.dumps(data, indent=2))

    @property
    def tsconfig_filepath(self):
        return os.path.join(self.project_dir, self.dek_key_tsconfig)
