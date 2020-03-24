import os
import sys
import traceback
from shutil import copyfile
import re
import setuptools

from findandreplace import replaceStringInFile

#from packaging import version


#<conflictJar groupId-artifactId="org.apache.httpcomponents:httpcore" versions="4.4.4/4.1.2" riskLevel="3">

def usage():
    print('Usage: python parseresultfile.py [filepath]')

def findconflict(fileName):
    group_id = []
    artifact_id = []
    version_loaded = []
    version_shadowed = []
    if not (os.path.isfile(fileName) and os.access(fileName, os.R_OK)):
        print("WARNING: Skipping...File does not exist or and is not readable:" + fileName)
        return False
    foundConflict_l3 = False
    with open(fileName, 'r') as f:
        for line in f.readlines():
            if (foundConflict_l3 == True):
                if ('versionId' in line):
                    is_loaded = re.search("<version versionId=\"(.*?)\" loaded=\"(.*?)\">", line).group(2)
                    if (is_loaded == 'true'):
                        version_loaded.append(re.search("<version versionId=\"(.*?)\" loaded=\"(.*?)\">", line).group(1))
                    else:
                        version_shadowed.append(
                            re.search("<version versionId=\"(.*?)\" loaded=\"(.*?)\">", line).group(1))
                    foundConflict_l3 = False
                continue
            if ('riskLevel="3"' in line):
                group_id.append(re.search("groupId-artifactId=\"(.*?):(.*?)\"", line).group(1))
                artifact_id.append(re.search("groupId-artifactId=\"(.*?):(.*?)\"", line).group(2))
                foundConflict_l3 = True
                continue
    return group_id, artifact_id, version_loaded, version_shadowed

def main():
    try:

        tot_conflict_l3 = 0
        tot_fix_l3 = 0
        group_id = []
        artifact_id = []
        version_loaded = []
        version_shadowed = []

        if len(sys.argv) < 2:
            usage()
            # old/new string required parameters, exit if not supplied
            sys.exit(-1)
        else:
            path = sys.argv[1]
            pomname = sys.argv[2]
        print('[path]         : ' + path)

        if not os.path.exists(path):
            raise Exception("Selected path does not exist: " + path)

        group_id, artifact_id, version_loaded, version_shadowed = findconflict(path)
        tot_conflict_l3 = len(artifact_id)

        #fix    fileName, filegroupId, fileartifactId, filenewVersion
        for i in range (0, tot_conflict_l3):
            if (replaceStringInFile(pomname, group_id[i], artifact_id[i], version_shadowed[i]) != False):
                tot_fix_l3 += 1


        print("Total Level 3 Conflict found : " + str(tot_conflict_l3))
        print("Total Level 3 Conflict fixed : " + str(tot_fix_l3))

    except Exception as err:
        print(traceback.format_exception_only(type(err), err)[0].rstrip())
        sys.exit(-1)


if __name__ == '__main__':
    main()