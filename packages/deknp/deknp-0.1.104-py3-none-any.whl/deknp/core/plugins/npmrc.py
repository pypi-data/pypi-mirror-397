import os
import io
import configparser
from collections import OrderedDict
from dektools.dict import assign
from dektools.file import remove_path
from .base import Plugin


class PluginNpmrc(Plugin):
    dek_key_npmrc = '.npmrc'

    def run(self):
        target = OrderedDict()
        for data in self.dek_info_list_final:
            target = assign(target, data.get(self.dek_key_npmrc) or {})
        remove_path(self.npmrc_filepath)
        if target:
            self.save_text(self.npmrc_filepath, json_to_npmrc(target))

    @property
    def npmrc_filepath(self):
        return os.path.join(self.project_dir, self.dek_key_npmrc)


def json_to_npmrc(data):
    config = configparser.ConfigParser(interpolation=None, delimiters=('=',))
    config['DEFAULT'] = data
    with io.StringIO() as ss:
        config.write(ss)
        content = ss.getvalue()
    lines = content.splitlines()
    result = []
    for i, line in enumerate(lines):
        if i == 0 and line == '[DEFAULT]':
            continue
        result.append('='.join(x.strip() for x in line.split('=', 1)))
    return '\n'.join(result)
