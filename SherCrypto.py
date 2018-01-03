import os, random, struct
import sys
import argparse
from Crypto.Cipher import AES
import shutil

# Using argparse for command-line options. Here are the options a user can has
parser = argparse.ArgumentParser(description='Encryptor/Decryptor tool')
# Mandatory arguments
parser.add_argument('file_path', help='File to be encrypted/decrypted.', type=str)
parser.add_argument('key', help='Key (128 bit default) used to encrypt/decrypt a file. Can be read from a file or entered as a command line argument (note: entering through the commmand line can cause problems, due to special characters like ! in bash, so it isn\'t recommended).', type=str)
# Optional arguments
parser.add_argument('-o', '--output_path', help='Specifies the path where the encrypted/decrypted files will be transferred.', type=str)
parser.add_argument('-s', '--save_original', help='Specifies that if an output_path was specified, the input_path will not be removed (removed by default).', action='store_true')
parser.add_argument('-k', '--key_size', help='Specifies the size of the key being used. 128 bit is default,', choices=[128, 192, 256], type=int)
parser.add_argument('-d', '--decrypt', help='Specifies decryption should be performed (encrypts by default).', action='store_true')
parser.add_argument('-n', '--no_removal', help='Specifies that the file that was encrypted/decrypted should not be removed after encryption/decryption.', action='store_true')
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

def crypto(path, key):
    if os.path.isdir(path):
        # If the file is a directory, iterate through all files in the directory
        for filename in os.listdir(path):
            fullPath = path + '/' + filename
            if os.path.isdir(fullPath): # If the file within the directory is a directory...
                crypto(fullPath, key) # Iterate through all files in that directory
            else:   # Otherwise, encrypt or decrypt the files within the directory
                if args.decrypt:
                    decrypt_file(key, len(key), fullPath)
                else:
                    encrypt_file(key, len(key), fullPath)
                if not args.no_removal: # If the user doesn't specify otherwise, remove the original file
                    os.remove(fullPath)
    else:       # If the file is not a directory, encrypt/decrypt the file, and return the name of
                # the encrypted/decrypted file, because it's needed if the user specified an output_path
        if args.decrypt:
            cryptoFile = decrypt_file(key, len(key), path)
        else:
            cryptoFile = encrypt_file(key, len(key), path)
        if not args.no_removal:
            os.remove(path)
        return cryptoFile

def main():
    # First, before any encryption/decryption is done, get the key from the user
    if os.path.isfile(args.key):    # If the argument passed for args.key is a file...
        with open(args.key, 'r') as keyFile:
            if args.key_size:   # And if a key_size was specified, read in the key according to the specified size
                key = keyFile.read(int(args.key_size/8))
            else:   # Otherwise, read in 16 bytes (the default key size)
                key = keyFile.read(16)
    else:   # Otherwise, the argument passed for args.key is the actual key
        key = args.key
    key.encode('utf-8') # You must encode the key, because pycrypto only works with bytes objects, encoded by utf-8

    # Encrypt/Decrypt the file(s).
    path = args.file_path
    newFile = crypto(path, key)

    # If the user wants the file(s) saved else where, move them to the specified path
    if args.output_path:
        # If the user is copying the encrypted/decrypted files from their location, We need to get the name of the
        # file/directory they wanted encrypted from the path. The name will be used to create a directory that will
        # hold the encrypted/decrypted file(s)
        if args.save_original or not os.path.isdir(path):
            removeStr = ''
            if ('/' in path) or ('\\' in path):
                for i in reversed(path):
                    if i != '\\' and i != '/':
                        removeStr += i
                    else:
                        break
                removeStr = removeStr[::-1]
                nPath = path.replace(removeStr,'')
                #newFile = nPath + newFile
                if os.path.isdir(path):
                    shutil.copytree(args.file_path, args.output_path + '/' + removeStr)
                else:
                    if args.save_original:
                        shutil.copy(newFile, args.output_path)
                    else:
                        shutil.move(newFile, args.output_path)  # Need to check this case, cause I don't think it will work because of newFile
        else:   # Otherwise, just move the file/directory to output_path
                shutil.move(args.file_path, args.output_path)

if __name__ == "__main__":
    main()
