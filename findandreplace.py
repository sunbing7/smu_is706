# ------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
# Filename: FindAndReplace.py
# Purpose:  Simple find and replace string in files (recursive) script
# Usage:	python FindAndReplace.py [Old String] [New String]
#				[File Filters(ex/default:".txt,.html,.erb")] [Directory To Check]
# Requirement: Files must be text (non-binary) files
#              (this is why we force you to pick the file pattern/filter)
# WARNING: This will overwrite files matching [File Filters]. All occurrences of [Old String]
#			will be replaced with [New String]. Make sure you really, really want to do this.
# ------------------------------------------------------------------------------

import os
import sys
import traceback
from shutil import copyfile
import re
#from packaging import version


def usage():
    print('Usage: python FindAndReplace.py [groupId] [artifactId] [newVersion] '
          '[File Filters(default:".txt,.html,.erb")] [Directory To Check(.)]')


def replaceStringInFile(fileName, filegroupId, fileartifactId, filenewVersion):
    if not (os.path.isfile(fileName) and os.access(fileName, os.W_OK)):
        print("WARNING: Skipping...File does not exist or and is not writeable:" + fileName)
        return False

    fileUpdated = False

    # credit/taken/adapted from: http://stackoverflow.com/a/4128194
    # copy file and rename old file
    try:
        os.remove(fileName + '.old')
    except:
        print("no existing file")
    os.rename(fileName, fileName+'.old')
    copyfile(fileName+'.old', fileName)
    # Read in old file
    dependenciesFound = False
    groupIdFound = False
    artifactFound = False
    previousLine = []
    with open(fileName, 'r') as f:
        newlines = []
        addline = []
        for line in f.readlines():
            if (groupIdFound):
                if ('artifactId' in line) and (fileartifactId in line):
                    fileUpdated = True
                    groupIdFound = False
                    artifactFound = True
                    previousLine = line
                    newlines.append(line)
                    continue
                #if ('</dependency>' in line):
                    # insert
                #previousLine = line
                #newlines.append(line)
                #continue

            if (artifactFound):
                if ('version' in line):
                    #'(.*?)'
                    oldVersoin = re.search(">(.*?)<", line).group(1)
                    line = line.replace(oldVersoin, filenewVersion)
                else:
                    #line = '        <version>'+filenewVersion+'</version>\n'
                    addline = previousLine.replace('artifactId', 'version')
                    addline = addline.replace(fileartifactId, filenewVersion)

                    newlines.append(addline)
                    #newlines.append(line)

                artifactFound = False

            if ('groupId' in line) and (filegroupId in line):
                groupIdFound = True
                previousLine = line
                newlines.append(line)
                continue
            previousLine = line
            newlines.append(line)
    # if artifact not found; add to dependencies
    if (fileUpdated == False):
        with open(fileName, 'r') as f:
            newlines = []
            for line in f.readlines():
                if (fileUpdated == False) and ('</dependencies>' in line):
                    # add groupId, artifactId and version needed
                    nubmerSpace = re.search('\S', line).start()
                    addline = ' ' * (nubmerSpace + 2)
                    addline = addline+'<dependency>\n'
                    newlines.append(addline)
                    addline = ' ' * (nubmerSpace + 4)
                    addline = addline+'<groupId>'+filegroupId+'</groupId>\n'
                    newlines.append(addline)
                    addline = ' ' * (nubmerSpace + 6)
                    addline = addline+'<artifactId>'+fileartifactId+'</artifactId>\n'
                    newlines.append(addline)
                    addline = ' ' * (nubmerSpace + 8)
                    addline = addline+'<version>'+filenewVersion+'</version>\n'
                    newlines.append(addline)
                    addline = ' ' * (nubmerSpace + 2)
                    addline = addline+'</dependency>\n'
                    newlines.append(addline)
                    fileUpdated = True
                newlines.append(line)

    # Write changes to same file
    if fileUpdated:
        print("String Found and Updating File: " + fileName)
        try:
            with open(fileName, 'w') as f:
                for line in newlines:
                    f.write(line)
        except:
            print('ERROR: Cannot open/access existing file for writing: ' + fileName)

    return fileUpdated


def main():
    try:

        DEFAULT_PATH = '.'

        if len(sys.argv) < 4:
            usage()
            # old/new string required parameters, exit if not supplied
            sys.exit(-1)
        else:
            groupId = sys.argv[1]
            artifactId = sys.argv[2]
            newVersion = sys.argv[3]

        if len(sys.argv) < 5:
            patterns = ['.xml']
        else:
            stringFilter = sys.argv[4]
            patterns = stringFilter.split(',')

        if len(sys.argv) < 6:
            path = DEFAULT_PATH
        else:
            path = sys.argv[5]

        print('[groupId]         : ' + groupId)
        print('[artifactId]         : ' + artifactId)
        print('[newVersion]         : ' + newVersion)
        print('[File Filters]       : ' + ', '.join(patterns))
        print('[Directory To Check] : ' + path)

        if not os.path.exists(path):
            raise Exception("Selected path does not exist: " + path)

        # Walks through directory structure looking for files matching patterns
        matchingFileList = \
            [os.path.join(dp, f) \
             for dp, dn, filenames in os.walk(path) \
             for f in filenames \
             if os.path.splitext(f)[1] in patterns]

        print('Files found matching patterns: ' + str(len(matchingFileList)))
        fileCount = 0
        filesReplaced = 0

        for currentFile in matchingFileList:

            fileCount += 1
            fileReplaced = replaceStringInFile(currentFile, groupId, artifactId, newVersion)
            if fileReplaced:
                filesReplaced += 1

        print("Total Files Searched         : " + str(fileCount))
        print("Total Files Replaced/Updated : " + str(filesReplaced))

    except Exception as err:
        print(traceback.format_exception_only(type(err), err)[0].rstrip())
        sys.exit(-1)


if __name__ == '__main__':
    main()