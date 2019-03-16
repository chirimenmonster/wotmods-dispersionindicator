#! /usr/bin/python2

from zipfile import ZIP_DEFLATED
from tools import package

def main():
    control = package.Control(config='config.ini')
    file = control.makePackage()
    print 'create package: {}'.format(file)

    control.setConfig(['config.ini', 'release.ini'])
    file = control.makePackage(package.SECTION_RELEASE, compression=ZIP_DEFLATED)
    print 'create package: {}'.format(file)


if __name__ == "__main__":
    main()
