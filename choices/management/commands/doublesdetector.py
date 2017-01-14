# Hello, this script is written in Python - http://www.python.org
# doublesdetector.py 1.0p
import os
import os.path
import string
import sys
import sha as shafunction

message = """
doublesdetector.py 1.0p

This script will search for files that are identical
(whatever their name/date/time).

  Syntax : python %s <directories>

      where <directories> is a directory or a list of directories
      separated by a semicolon (;)

Examples : python %s c:\windows
           python %s c:\;d:\;e:\ > doubles.txt
           python %s c:\program files > doubles.txt

This script is public domain. Feel free to reuse and tweak it.
The author of this script Sebastien SAUVAGE <sebsauvage at sebsauvage dot net>
http://sebsauvage.net/python/
""" % ((sys.argv[0], )*4)


def files_sha(filepath):
    """ Compute SHA (Secure Hash Algorythm) of a target_file.
        Input : filepath : full path and name of file (eg. 'c:\windows\emm386.exe')
        Output : string : contains the hexadecimal representation of the SHA of the target_file.
                          returns '0' if file could not be read (file not found, no read rights...)
    """
    try:
        target_file = open(filepath, 'rb')
        digest = shafunction.new()
        data = target_file.read(65536)
        while len(data) != 0:
            digest.update(data)
            data = target_file.read(65536)
        target_file.close()
    except Exception as e:
        print(e)
        return '0'
    else:
        return digest.hexdigest()


def detect_doubles(directories):
    fileslist = {}
    # Group all files by size (in the fileslist dictionnary)
    for directory in directories.split(';'):
        directory = os.path.abspath(directory)
        sys.stderr.write('Scanning directory '+directory+'...')
        os.path.walk(directory, callback, fileslist)
        sys.stderr.write('\n')

    sys.stderr.write('Comparing files...')
    # Remove keys (filesize) in the dictionnary which have only 1 file
    for (filesize, listoffiles) in fileslist.items():
        if len(listoffiles) == 1:
            del fileslist[filesize]

    # Now compute SHA of files that have the same size,
    # and group files by SHA (in the filessha dictionnary)
    filessha = {}
    while len(fileslist) > 0:
        (filesize, listoffiles) = fileslist.popitem()
        for filepath in listoffiles:
            sys.stderr.write('.')
            current_sha = files_sha(filepath)
            if current_sha in filessha:
                filessha[current_sha].append(filepath)
            else:
                filessha[current_sha] = [filepath]
    if '0' in filessha:
        del filessha['0']

    # Remove keys (current_sha) in the dictionnary which have only 1 file
    for (current_sha, listoffiles) in filessha.items():
        if len(listoffiles) == 1:
            del filessha[current_sha]
    sys.stderr.write('\n')
    return filessha


def callback(fileslist, directory, files):
    sys.stderr.write('.')
    for fileName in files:
        filepath = os.path.join(directory, fileName)
        if os.path.isfile(filepath):
            filesize = os.stat(filepath)[6]
            if filesize in fileslist:
                fileslist[filesize].append(filepath)
            else:
                fileslist[filesize] = [filepath]

if len(sys.argv) > 1:
    doubles = detect_doubles(" ".join(sys.argv[1:]))
    print 'The following files are identical:'
    print '\n'.join(["----\n%s" % '\n'.join(doubles[filesha]) for filesha in doubles.keys()])
    print '----'
else:
    print message


# if len(sys.argv) > 1:
#     doubles = detect_doubles(" ".join(sys.argv[1:]))
#     for filesha in doubles.keys():
#         n = 0
#         for filename in doubles[filesha]:
#             if filename.split('.')[-1] == 'mp3':
#                 if n > 0:
#                     os.remove(filename)
#                     print "%s (removed)" % filename
#                 else:
#                     print filename
#                 n += 1
#         print "\n"
# else:
#     print message
