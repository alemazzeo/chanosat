import os
import shutil


class FileTools():

    @classmethod
    def file_exist(cls, fullname, default_path='./'):
        path, name, extension = cls.splitname(fullname)
        name0 = fullname + extension
        name1 = default_path + name
        name2 = default_path + name + extension

        if os.path.isfile(fullname):
            return fullname
        elif os.path.isfile(name0):
            return name0
        elif os.path.isfile(name1):
            return name1
        elif os.path.isfile(name2):
            return name2

    @classmethod
    def splitname(cls, fullname):
        fullname, extension = os.path.splitext(fullname)
        path, name = os.path.split(fullname)
        return path, name, extension

    @classmethod
    def newname(cls, fullname, default='../data/temp.npy'):
        path, name, extension = cls.splitname(fullname)
        dpath, dname, dext = cls.splitname(default)

        if extension == '':
            extension = dext

        if path == '':
            path = dpath

        os.makedirs(path, exist_ok=True)

        if name == '':
            name = dname

        if os.path.isfile(path + '/' + name + '0' + extension):
            i = 0
            newname = name + str(i)
            while os.path.isfile(path + '/' + newname + extension):
                i += 1
                newname = name + str(i)
            name = newname
        else:
            name = name + '0'

        return os.path.normpath(path + '/' + name + extension)

    @classmethod
    def move(cls, files, dest, copy=False, verbose=False):
        changes = list()
        newlist = list()
        for fullname in files:
            path, name, extension = cls.splitname(fullname)
            dpath, dname, dextension = cls.splitname(dest)

            if (path == dpath and name[:len(dname)] == dname):
                newlist.append(fullname)
            else:
                newname = cls.newname(dest)
                if copy:
                    shutil.copyfile(fullname, newname)
                    if verbose:
                        print(fullname + ' copy to ' + newname)
                else:
                    os.rename(fullname, newname)
                    if verbose:
                        print(fullname + ' move to ' + newname)

                newlist.append(newname)
                changes.append([fullname, newname])

        return newlist, changes
