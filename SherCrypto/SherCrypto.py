import os
import sys
import argparse
import files
import crypto

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

def main():
    print('This is a change made.')
    # Get the input path, key, and other necessary data
    key = crypto.getKey(args.key_path, args.key_size)
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
        fileName = fileOps.getFileFromPath(inputPath)
        newPath = outputPath + '/' + fileName
        if inputPath == outputPath:
            print('Error: input path equal to output path.')
            sys.exit(-1)
        if args.output_path and not args.save_original_input and not args.save_altered_input:
            # If we aren't saving the original input or the altered input, then we will be doing a move operation.
            # This part should be checked but it's probably O.K.
            if os.path.exists(newPath) and os.path.isdir(outputPath):
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
                headDir = fileOps.getFileFromPath(inputPath)
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
    alteredInputPath = crypto.cryptoFilePath(inputPath, key, decrypt)

    # This block of code is for the file moving and deletion operations that need to take place.
    if args.output_path:
        # If output_path was specified
        if args.save_altered_input and not args.save_original_input:
            # Choice: output_path, save_altered_input, no save_original_input
            if os.path.isdir(inputPath):
                if not decrypt:
                    fileOps.moveFiles(inputPath, '.enc', removeExtension=False)
                else:
                    fileOps.moveFiles(inputPath, '.enc', removeExtension=True)
                fileOps.moveFiles(inputPath, outputPath, move=False)
            else:
                fileOps.moveFiles(inputPath)
                fileOps.moveFiles(alteredInputPath, outputPath, move=False)
        elif not args.save_altered_input and args.save_original_input:
            # Choice: output_path, no save_altered_input, save_original_input
            if os.path.isdir(inputPath):
                fileOps.moveFiles(inputPath, outputPath, move=False)
                if not decrypt:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=False)
                    fileOps.removeFiles(inputPath, '.enc', removeExtension=True)
                else:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=True)
                    fileOps.removeFiles(inputPath, '.enc', removeExtension=False)
            else:
                fileOps.moveFiles(alteredInputPath, outputPath, move=False)
                fileOps.moveFiles(alteredInputPath)
        elif args.save_altered_input and args.save_original_input:
            # Choice: output_path, save_altered_input, save_original_input
            if os.path.isdir(inputPath):
                fileOps.moveFiles(inputPath, outputPath, move=False)
                if not decrypt:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=False)
                else:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=True)
            else:
                fileOps.moveFiles(alteredInputPath, outputPath, move=False)
        else:
            # Choice: output_path, no save_altered_input, no save_original_input
            if os.path.isdir(inputPath):
                fileOps.moveFiles(inputPath, outputPath)
                if not decrypt:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=False)
                else:
                    fileOps.removeFiles(newPath, '.enc', removeExtension=True)
            else:
                fileOps.moveFiles(alteredInputPath, outputPath, move=True)
                fileOps.moveFiles(inputPath)
    elif not saveOriginal:
        # Choice: no output_path or no save_original_input (save_altered_input doesn't apply if no output_path)
        if decrypt:
            # If decryption was done, and the user doesn't want the input saved...
            fileOps.removeFiles(inputPath, '.enc', removeExtension=True)
        else:
            # If encryption was done, and the user doesn't want the input saved...
            fileOps.removeFiles(inputPath, '.enc', removeExtension=False)

if __name__ == "__main__":
    main()
