import os
import shutil
import py_compile
import zipfile
import ConfigParser
import json
from string import Template

BUILD_DIR = 'build'
CONFIG = 'config.ini'
FILELIST = 'files.json'

def get_config():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read(CONFIG)

    parameters = dict(
        package     = inifile.get('mod', 'package'),
        package_id  = inifile.get('mod', 'package_id'),
        logfile     = inifile.get('mod', 'logfile'),
        name        = inifile.get('mod', 'name'),
        author      = inifile.get('mod', 'author'),
        version     = inifile.get('mod', 'version'),
        description = inifile.get('mod', 'description'),
        support_url = inifile.get('mod', 'support_url'),
        github_page = inifile.get('mod', 'github_page'),
        wot_version = inifile.get('wot', 'version')
    )
    return parameters


def compile_python(src, dst, virtualdir):
    py_compile.compile(file=src, cfile=dst, dfile=os.path.join(virtualdir, src), doraise=True)

def apply_template(src, dstdir, parameters):
    with open(src, 'r') as in_file, open(os.path.join(dstdir, src), 'w') as out_file:
        out_file.write(Template(in_file.read()).substitute(parameters))

def split(path):
    head, tail = os.path.split(path)
    if not head:
        return [ tail ]
    result = split(head)
    result.append(path)
    return result

def read_filelist(parameters=None):
    paths = []
    with open(FILELIST, 'r') as f:
        desc = json.load(f)
        for target in desc:
            if target['method'] == 'apply+python':
                for src in target['files']:
                    root, ext = os.path.splitext(src)
                    dst = root + '.pyc'
                    apply_template(src, BUILD_DIR, parameters)
                    compile_python(os.path.join(BUILD_DIR, src), os.path.join(BUILD_DIR, dst), target['reldir'])
                    paths.append((dst, os.path.join(target['root'], target['reldir'], dst)))
            elif target['method'] == 'apply':
                for src in target['files']:
                    apply_template(src, BUILD_DIR, parameters)
                    paths.append((src, os.path.join(target['root'], target['reldir'], src)))
            elif target['method'] == 'plain':
                for src in target['files']:
                    shutil.copy(src, BUILD_DIR)      
                    paths.append((src, os.path.join(target['root'], target['reldir'], src)))
    return paths

def main():
    parameters = get_config()
    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass
    os.makedirs(BUILD_DIR)

    paths = read_filelist(parameters=parameters)

    package_path = os.path.join(BUILD_DIR, parameters['package'])
    donelist = []
    with zipfile.ZipFile(package_path, 'w', compression=zipfile.ZIP_STORED) as package_file:
        for source, target in paths:
            for dir in split(target)[0:-1]:
                if dir not in donelist:
                    package_file.write('.', dir, zipfile.ZIP_STORED)
                    donelist.append(dir)
            package_file.write(os.path.join(BUILD_DIR, source), target, zipfile.ZIP_STORED)
            donelist.append(target)

if __name__ == "__main__":
    main()
