#!/usr/bin/env python3

import os
import sys
import time


class File:

    def __init__(self, timestamp: float, filepath: str):
        self.timestamp = timestamp
        self.strftime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(timestamp))
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
                        self.files.append(File(float(fields[0]), fields[1]))

    def store(self):
        with open(self.infopath, 'w') as infofile:
            infofile.write('[Trash Info]\n')
            for file in self.files:
                infofile.write('%s %s\n' % (str(file.timestamp), file.filepath))

    def list(self):
        if len(self.files) == 0:
            print('[Trash] Void')
        else:
            print('[Trash] Total %d' % len(self.files))
            print('\tDeletionTime\t\tFilePath')
            for index, file in enumerate(self.files):
                print('[%d] \t%s\t%s' % (index, file.strftime, file.filepath))

    def include(self, file: File):
        ret = os.system('mv %s %s' % (file.filepath, file.trashpath(self.rootpath)))
        if ret == 0:
            self.files.append(file)

    def restore(self, file: File):
        ret = os.system('mv %s %s' % (file.trashpath(self.rootpath), file.filepath))
        if ret == 0:
            self.files.remove(file)

    def remove(self, file: File):
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
            for filepath in sys.argv[2:]:
                file = File(time.time(), filepath)
                trash.include(file)
        elif sys.argv[1] == 'restore':
            for index in sys.argv[2:]:
                file = trash.files[int(index)]
                trash.restore(file)
        elif sys.argv[1] == 'remove':
            for index in sys.argv[2:]:
                file = trash.files[int(index)]
                trash.remove(file)
