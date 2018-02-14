import os, random, struct
import sys
from Crypto.Cipher import AES

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

        # Write the original size of the file, then the iv used for the file, then the out_filename, then the file
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

def getKey(key_path, key_size):
    # Gets the key from the user, whether through the command line or through a file
    if os.path.isfile(key_path):    # If the argument passed for args.key_path is a regular file...
        with open(key_path, 'r') as keyFile:
            if key_size:   # Ff a key_size was specified, read in the key according to the specified size
                key = keyFile.read(int(key_size/8))    # Dividing it by 8 will give us the # of bytes
            else:   # Otherwise, read in 16 bytes (the default key size)
                key = keyFile.read(16)
    else:   # Otherwise, the argument passed for args.key_path is the actual key
        key = key_path
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
