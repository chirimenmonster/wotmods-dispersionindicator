import os
import shutil
import py_compile
import zipfile
import ConfigParser
from string import Template

SCRIPT_NAME = 'mod_dispersionindicator'

WOTMOD_ROOTDIR = 'res'
SCRIPT_RELDIR = 'scripts/client/gui/mods'

BUILD_DIR = 'build'

files = [
    (SCRIPT_NAME + '.py', SCRIPT_NAME + '.pyc', SCRIPT_RELDIR),
]

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
    
def main():
    inifile = ConfigParser.SafeConfigParser()
    inifile.read('config.ini')

    class config:
        name        = inifile.get('mod', 'name')
        author      = inifile.get('mod', 'author')
        version     = inifile.get('mod', 'version')
        description = inifile.get('mod', 'description')
        support_url = inifile.get('mod', 'support_url')
        github_page = inifile.get('mod', 'github_page')
        wot_version = inifile.get('wot', 'version')

    parameters = dict(
        package     = '{}.{}_{}.wotmod'.format(config.author, config.name, config.version).lower(),
        package_id  = '{}.{}'.format(config.author, config.name).lower(),
        name        = config.name,
        author      = config.author,
        version     = config.version,
        description = config.description,
        support_url = config.support_url,
        github_page = config.github_page,
        wot_version = config.wot_version
    )

    try:
        shutil.rmtree(BUILD_DIR)
    except:
        pass
    os.makedirs(BUILD_DIR)

    paths = []
    for target in files:
        if isinstance(target, list) or isinstance(target, tuple):
            src, dst, reldir = target
            apply_template(src, BUILD_DIR, parameters)
            compile_python(os.path.join(BUILD_DIR, src), os.path.join(BUILD_DIR, dst), reldir)
            paths.append((dst, os.path.join(WOTMOD_ROOTDIR, reldir, dst)))
        else:
            apply_template(target, BUILD_DIR, parameters)      
            paths.append((target, target))

    package_path = os.path.join(BUILD_DIR, parameters['package'])
    with zipfile.ZipFile(package_path, 'w', compression=zipfile.ZIP_STORED) as package_file:
        for source, target in paths:
            for dir in split(target)[0:-1]:
                package_file.write('.', dir, zipfile.ZIP_STORED)
            package_file.write(os.path.join(BUILD_DIR, source), target, zipfile.ZIP_STORED)

if __name__ == "__main__":
    main()
