#!/usr/bin/env python3

import os
import sys
import time


class File:

    def __init__(self, timestamp: float, filetype: str, filepath: str):
        self.timestamp = timestamp
        self.strftime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(timestamp))
        self.filetype = filetype
        self.filepath = os.path.abspath(filepath)

    def trashpath(self, rootpath):
        return os.path.join(rootpath, str(self.timestamp))


class Trash:

    def __init__(self, rootpath: str):
        self.rootpath = os.path.abspath(rootpath)
        self.infopath = os.path.join(rootpath, '.trashinfo')
        self.files = list()

    def __enter__(self):
        self.init()
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store()

    def init(self):
        if not os.path.isdir(self.rootpath):
            os.system('mkdir -p %s' % self.rootpath)

    def load(self):
        if os.path.isfile(self.infopath):
            with open(self.infopath, 'r') as infofile:
                lines = infofile.readlines()
                if lines[0].strip() == '[Trash Info]':
                    for line in lines[1:]:
                        fields = line.split()
                        self.files.append(File(float(fields[0]), fields[1], fields[2]))

    def store(self):
        with open(self.infopath, 'w') as infofile:
            infofile.write('[Trash Info]\n')
            for file in self.files:
                infofile.write('%s %s %s\n' % (str(file.timestamp), file.filetype, file.filepath))

    def list(self):
        if len(self.files) == 0:
            print('[Trash] Void')
        else:
            print('\033[1m[Trash] Total %d\033[0m' % len(self.files))
            print('\033[1m\tDeletionTime\t\tOriginalPath\033[0m')
            for index, file in enumerate(self.files):
                if file.filetype[0] == '*':
                    if file.filetype[1:] == 'dir':
                        print('\033[1m[%d]\033[0m \t%s\t\033[0;36m%s*\033[0m' % (index, file.strftime, file.filepath))
                    else:
                        print('\033[1m[%d]\033[0m \t%s\t%s*' % (index, file.strftime, file.filepath))
                else:
                    if file.filetype == 'dir':
                        print('\033[1m[%d]\033[0m \t%s\t\033[0;36m%s\033[0m' % (index, file.strftime, file.filepath))
                    else:
                        print('\033[1m[%d]\033[0m \t%s\t%s' % (index, file.strftime, file.filepath))

    def include(self, file: File):
        ret = os.system('mv %s %s' % (file.filepath, file.trashpath(self.rootpath)))
        if ret == 0:
            self.files.append(file)

    def restore(self, file: File):
        ret = os.system('mv %s %s' % (file.trashpath(self.rootpath), file.filepath))
        if ret == 0:
            self.files.remove(file)

    def exclude(self, file: File):
        ret = os.system('rm -r %s' % file.trashpath(self.rootpath))
        if ret == 0:
            self.files.remove(file)


if __name__ == '__main__':
    rootpath = os.path.join(os.environ['HOME'], '.local/share/Trash')
    with Trash(rootpath) as trash:
        if len(sys.argv) < 2:
            trash.list()

        elif sys.argv[1] == 'list':
            trash.list()

        elif sys.argv[1] == 'include':
            files = []
            for filepath in sys.argv[2:]:
                if os.path.isdir(filepath):
                    filetype = 'dir'
                else:
                    filetype = 'file'
                if os.path.islink(filepath):
                    filetype = '*' + filetype
                files.append(File(time.time(), filetype, filepath))
            for file in files:
                if os.path.exists(file.filepath):
                    trash.include(file)
                    print('\033[1;32m[Trash Include]\033[0;32m %s\033[0m' % file.filepath)
                else:
                    print('\033[1;33m[Trash Include]\033[0;33m %s not exists\033[0m' % file.filepath)

        elif sys.argv[1] == 'restore':
            files = []
            for index in sys.argv[2:]:
                files.append(trash.files[int(index)])
            for file in files:
                if os.path.exists(file.filepath):
                    print('\033[1;33m[Trash Restore]\033[0;33m %s already exists\033[0m' % file.filepath)
                else:
                    trash.restore(file)
                    print('\033[1;32m[Trash Restore]\033[0;32m %s\033[0m' % file.filepath)

        elif sys.argv[1] == 'exclude':
            files = []
            for index in sys.argv[2:]:
                files.append(trash.files[int(index)])
            for file in files:
                trash.exclude(file)
                print('\033[1;31m[Trash Exclude]\033[0;31m %s\033[0m' % file.filepath)
