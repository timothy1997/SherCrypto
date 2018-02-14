import os, random, struct
import sys
import argparse
from Crypto.Cipher import AES
import shutil

# Using argparse for command-line options. Here are the options a user can has
parser = argparse.ArgumentParser(description='Encryptor/Decryptor tool')
# Mandatory arguments
parser.add_argument('input_path', help='File/Directory to be encrypted/decrypted.', type=str)
parser.add_argument('key_path', help='Key (128 bit default) used to encrypt/decrypt a file. Can be read from a file or entered as a command line argument (note: entering through commmand line not recommended).', type=str)
# Optional arguments
parser.add_argument('-o', '--output_path', help='Path where the output files will be saved (without keeping input files).', type=str)
parser.add_argument('-so', '--save_original_input', help='Input files will be saved at input path', action='store_true')
parser.add_argument('-sa', '--save_altered_input', help='Output files will be saved at input path, even if output path was specified.', action='store_true')
parser.add_argument('-d', '--decrypt', help='Specifies decryption should be performed (encrypts by default).', action='store_true')
parser.add_argument('-k', '--key_size', help='Specifies the size of the key being used. 128 bit is default,', choices=[128, 192, 256], type=int)
# Other options I may want to specify for the future:
#   The type of encryption algorithm used (AES/RSA)
#   Name all files being encrypted/specify a naming scheme.
args = parser.parse_args()  # Get the command line arguments the user specified

def encrypt_file(key, keysize, in_filename, out_filename=None, chunksize=64*1024):
    # Encrypts a file using AES (CBC mode) with the given key.
    # Key: The encryption key - a string that must be either 16,24, or 32 bytes
    # in_filename: name of input file
    # out_filename: If none, '<in_filename>.enc' will be used.
    # chunksize: Sets the size of the chunk which the function uses to read and
    # encrypt the file. Larger chunk sizes can be faster for some files and machines.
    # chunksizes must be divisible by 16.
    try:
        if not out_filename:
            out_filename = in_filename + '.enc'

        iv = ''.join(chr(random.randint(0x20,0x7F)) for i in range(16))
        iv = iv.encode('utf-8')

        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' '.encode('utf-8') * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))

        print(in_filename) # Print the name of the file that was encrypted
        return out_filename
    except Exception as e:
        print(e)
        sys.exit(1)

def decrypt_file(key, keysize, in_filename, out_filename=None, chunksize=24*1024):
    # Decrypts a file using AES (CBC mode) with the given key. Parameters are
    # similar to encrypt_file, with one difference: out_filename, if not supplied
    # will be in_filename without its last extension (i.e. if in_filename is
    # 'aaa.zip.enc' then out_filename will be 'aaa.zip')
    try:
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)

        print(in_filename) # Print the name of the file that was decrypted
        return out_filename
    except Exception as e:
        print(e)
        sys.exit(1)

def getKey():
    # Gets the key from the user, whether through the command line or through a file
    if os.path.isfile(args.key_path):    # If the argument passed for args.key_path is a regular file...
        with open(args.key_path, 'r') as keyFile:
            if args.key_size:   # Ff a key_size was specified, read in the key according to the specified size
                key = keyFile.read(int(args.key_size/8))    # Dividing it by 8 will give us the # of bytes
            else:   # Otherwise, read in 16 bytes (the default key size)
                key = keyFile.read(16)
    else:   # Otherwise, the argument passed for args.key_path is the actual key
        key = args.key_path
    key.encode('utf-8') # You must encode the key, because pycrypto only works with bytes objects, encoded by utf-8
    return key

def cryptoFilePath(path, key, decrypt=False):
    # Traverses the file path specified and encrypts/decrypts the traversed file(s), either through recursively
    # descending through the input_path (for directories) or encrypting/decrypting the single file specified.
    #  If a single file was specified, the function returns a file path to the file, since the name changed.
    # The function also removes the input files if the user specified so (I may change this later)
    if os.path.isdir(path):
        # If the file is a directory, iterate through all files in the directory
        for filename in os.listdir(path):
            fullPath = path + '/' + filename
            if os.path.isdir(fullPath): # If the file within the directory is a directory...
                cryptoFilePath(fullPath, key, decrypt) # Iterate through all files in that directory
            else:   # Otherwise, encrypt or decrypt the files within the directory
                if decrypt:
                    decrypt_file(key, len(key), fullPath)
                else:
                    encrypt_file(key, len(key), fullPath)
    else:       # If the file is not a directory, encrypt/decrypt the file, and return the name of
                # the encrypted/decrypted file, because it's needed if the user specified an output_path
        if decrypt:
            cryptoFile = decrypt_file(key, len(key), path)
        else:
            cryptoFile = encrypt_file(key, len(key), path)
        return cryptoFile

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

def moveFiles(inputPath, outputPath, move=True):
    if args.output_path:    # If output_path was specified...
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
    else:   # If output_path wasn't specified, inform the user
        print("output_path not specified")

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


def main():
    # Get the input path, key, and other necessary data
    key = getKey()
    inputPath = args.input_path
    if not os.path.exists(inputPath):
        # If the input_path doesn't exist, exit
        print('Error: input path doesn\'t exist.')
        sys.exit(-1)

    decrypt = args.decrypt
    saveOriginal = args.save_original_input;
    if args.output_path:
        # If the user specified an output_path, we need to review the status of
        # the output_path (for example, does the output_path already exist?)
        outputPath = args.output_path
        # We will not only need the name of the output_path, but the name of the
        # path when the encrypted/decrypted directory was moved to the outputPath
        fileName = getFileFromPath(inputPath)
        newPath = outputPath + '/' + fileName
        if inputPath == outputPath:
            print('Error: input path equal to output path.')
            sys.exit(-1)
        if args.output_path and not args.save_original_input and not args.save_altered_input:
            # If we aren't saving the original input or the altered input, then we will be doing a move operation.
            # This part should be checked but it's probably O.K.
            if os.path.exists(outputPath) and os.path.isdir(outputPath):
                value = input('Warning: output_path is directory that already exists. If you continue, input_path will be moved inside output_path. Continue? (y/n)')
                if value == 'n' or value == 'N':
                    sys.exit(-1)
            elif os.path.exists(outputPath) and os.path.isfile(outputPath):
                value = input('Warning: output_path is a file that already exists. If you continue, output_path may be overwritten. Continue? (y/n)')
                if value == 'n' or value == 'N':
                    sys.exit(-1)
        else:
            # This part also needs to be checked...
            # Otherwise, we are doing a copy operation.
            if os.path.isdir(inputPath):
                headDir = getFileFromPath(inputPath)
                if os.path.exists(outputPath + '/' + headDir):
                    # Because of shutil.copytree, we can't copy the input_path to the output_path
                    # if it already exists and is a directory
                    print('Error: output_path is directory that already exists.')
                    sys.exit(-1)
            else:
                if os.path.exists(outputPath) and os.path.isdir(outputPath):
                    value = input('Warning: output_path is a directory that already exists. If you continue, input_path will be copied inside output_path. Continue? (y/n)')
                    if value == 'n' or value == 'N':
                        sys.exit(-1)
                elif os.path.exists(outputPath) and os.path.isfile(outputPath):
                    value = input('Warning: output_path is a file that already exists. If you continue, output_path will be overwritten. Continue? (y/n)')
                    if value == 'n' or value == 'N':
                        sys.exit(-1)

    # Encrypt/Decrypt the file(s).
    alteredInputPath = cryptoFilePath(inputPath, key, decrypt)

    # This block of code is for the file moving and deletion operations that need to take place.
    if args.output_path:
        # If output_path was specified
        if args.save_altered_input and not args.save_original_input:
            # Choice: output_path, save_altered_input, no save_original_input
            if os.path.isdir(inputPath):
                if not decrypt:
                    removeFiles(inputPath, '.enc', removeExtension=False)
                else:
                    removeFiles(inputPath, '.enc', removeExtension=True)
                moveFiles(inputPath, outputPath, move=False)
            else:
                removeFiles(inputPath)
                moveFiles(alteredInputPath, outputPath, move=False)
        elif not args.save_altered_input and args.save_original_input:
            # Choice: output_path, no save_altered_input, save_original_input
            if os.path.isdir(inputPath):
                moveFiles(inputPath, outputPath, move=False)
                if not decrypt:
                    removeFiles(newPath, '.enc', removeExtension=False)
                    removeFiles(inputPath, '.enc', removeExtension=True)
                else:
                    removeFiles(newPath, '.enc', removeExtension=True)
                    removeFiles(inputPath, '.enc', removeExtension=False)
            else:
                moveFiles(alteredInputPath, outputPath, move=False)
                removeFiles(alteredInputPath)
        elif args.save_altered_input and args.save_original_input:
            # Choice: output_path, save_altered_input, save_original_input
            if os.path.isdir(inputPath):
                moveFiles(inputPath, outputPath, move=False)
                if not decrypt:
                    removeFiles(newPath, '.enc', removeExtension=False)
                else:
                    removeFiles(newPath, '.enc', removeExtension=True)
            else:
                moveFiles(alteredInputPath, outputPath, move=False)
        else:
            # Choice: output_path, no save_altered_input, no save_original_input
            if os.path.isdir(inputPath):
                moveFiles(inputPath, outputPath)
                if not decrypt:
                    removeFiles(newPath, '.enc', removeExtension=False)
                else:
                    removeFiles(newPath, '.enc', removeExtension=True)
            else:
                moveFiles(alteredInputPath, outputPath, move=True)
                removeFiles(inputPath)
    elif not saveOriginal:
        # Choice: no output_path or no save_original_input (save_altered_input doesn't apply if no output_path)
        if decrypt:
            # If decryption was done, and the user doesn't want the input saved...
            removeFiles(inputPath, '.enc', removeExtension=True)
        else:
            # If encryption was done, and the user doesn't want the input saved...
            removeFiles(inputPath, '.enc', removeExtension=False)

if __name__ == "__main__":
    main()
