import shutil
import os
import sys

def moveFiles(inputPath, outputPath, move=True):
    if move:    # And moving is the specified action...
        shutil.move(inputPath, outputPath) # Move the input path to the output path
    else:   # Otherwise, copying is taking place, so copy the inputPath to the outputPath (different for files vs directories)
        if os.path.isdir(inputPath):
            # Since shutil.copytree can't move to a directory that already exists, we need to get
            # the name of the directory we're moving, and add it to the outputPath, so that we can
            # move the encrypted/decrypted files. This problem doesn't exist with single files.
            headDir = getFileFromPath(inputPath)
            shutil.copytree(inputPath, outputPath + '/' + headDir)
        else:
            shutil.copy(inputPath, outputPath)

def removeFiles(input_path, extension='', removeExtension=True):
    # This function allows you to remove file(s)/directories(s), by either removing a file
    # with a specific extension, or by removing files without that specific extension.
    if os.path.isdir(input_path):
        # If the path is to a directory...
        for fileName in os.listdir(input_path):
            fullPath = input_path + '/' + fileName
            # Iterate through each file in the directory.
            if os.path.isdir(fullPath):
                # If it is a directory, go into the directory
                removeFiles(fullPath, extension, removeExtension)
            elif (extension != '') and (fileName[-len(extension):] == extension) and removeExtension:
                # If and extension was specified, the extension matches the file's extension, and removeExtension is true...
                os.remove(fullPath) # Remove the file
            elif (extension != '') and (fileName[-len(extension):] != extension) and not removeExtension:
                # If an extension was specified, and the extension doesn't match, and removeExtension is false...
                os.remove(fullPath)  # Remove the file
            elif (extension == ''):
                # If no extension was specified,
                os.remove(fullPath)  # Remove the file
    else:
        # If it's not a directory, it's a single file, so just remove it.
        os.remove(input_path)


def getFileFromPath(path):
# This function returns the last file/directory from a path passed to it. It does this by starting at the end of the
# path, and going through each character and recording it, until you hit a character that is either '/' or '\'. When
# either character is hit, the loop breaks and the string is reversed, giving you the name of the last file/directory
    name = ''
    alteredInputPath = ''
    if ('/' in path) or ('\\' in path):
        # Get the input file from the inputPath (the last characters of the path, until you reach either / or \\)
        for i in reversed(path):
            if i != '\\' and i != '/':
                name += i
            else:
                break
        name = name[::-1]
        return name
    else:
        return path

# What you decided was to just send all the files in a folder to the host, then the host will just rebuild the file
# system using the path's that are sent to it.
def getFileSystem(path, fileSystem):    # fileSystem is a dictionary
    if os.path.isdir(path):
        for fileName in os.listdir(path):
            fullPath = path + '/' + fileName
            if os.path.isdir(fullPath):
                getFileSystem(fullPath, fileSystem)
            else:
                with open(fullPath, 'rb') as readFile:
                    fileSystem[fullPath] =
