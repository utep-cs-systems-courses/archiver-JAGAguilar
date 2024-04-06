#! /usr/bin/env python3

import os
import sys
#buf.py is the buffered reader provided by Freudenthal
from buf import BufferedFdReader, BufferedFdWriter

def createArch(fileList):
    #Initialize where the full data to be written will be stored
    archive = b''
    for file in fileList:
        curFile = os.open(file,os.O_RDONLY)
        reader = BufferedFdReader(curFile)
        file_size = os.path.getsize(file)

        #Create a fileHeader to store the file name/path and the file size
        fileHeader = bytearray(64)
        for i in range(len(file)):
            fileHeader[i] = file[i].encode()[0]
        for i in range(len(str(file_size))):
            fileHeader[i+32]= str(file_size)[i].encode()[0]#store file size 32 bytes later in header

        #read through file and store contents in array
        bt = reader.readByte()
        content = []
        while bt is not None:
            content.append(bt)
            bt = reader.readByte()
        reader.close()
        #Store both file header and contents casted as a byte array in fileContents
        #store complete file data in archive then loop
        fileContents = fileHeader+ bytearray(content)
        archive += fileContents
    return archive #return to write to byte stream


def extractArch(archName):
    # Open the archive file for reading
    arch_fd = os.open(archName, os.O_RDONLY)
    reader = BufferedFdReader(arch_fd)
    contents = b''

    #Reader whole archive and store the contents in contents
    while(bt := reader.readByte()) is not None:
        contents += bytes([bt])
    reader.close()

    #while there are contents to read
    while len(contents):
        #Take first 64 bytes as set by framer and take the name out
        fileHeader = contents[:64]
        fileName = fileHeader[:32].decode().strip('\x00')

        #Slice the last 32 bytes to get the file size
        fileSize = fileHeader[32:64].decode().strip('\x00')
        fileSize = int(fileSize)

        #Get the file contents outside of file header
        fileContents = contents[64:64+fileSize]

        #update contents
        contents = contents[64+fileSize:]

        #Write contents to file
        fd = os.open(fileName, os.O_WRONLY | os.O_CREAT)
        writer = BufferedFdWriter(fd)
        for i in fileContents:
            writer.writeByte(i)
        writer.close()
        
    
def ibArchive(archList):
    #Set terminator to add to end of file
    #initialize archive
    terminator = b'\e'
    archive = b''
    for fName in archList:
        #As in out of band creating file header but only for name
        curFile = os.open(fName, os.O_RDONLY)
        fileHeader = bytearray(32)
        for i in range(len(fName)):
            fileHeader[i] = fName[i].encode()[0]

        #Initialize empty list for contents of file
        content = []
        reader = BufferedFdReader(curFile)
        
        while (bt := reader.readByte()) is not None:
            #add an extra \ if current byte is \
            if bytes([bt]) == b'\\':
                content.append(ord(b'\\'))
            content.append(bt)

        #complete file with header, contents and terminator
        file_data = fileHeader + bytearray(content) + terminator
        archive += file_data
    reader.close()
    return archive

def ibExtract(archName):
    arch_fd = os.open(archName, os.O_RDONLY)
    reader = BufferedFdReader(arch_fd)

    while (bt := reader.readByte()) is not None:
        fileName = b''
        for i in range(32):
            #read file header for file name
            fileName += bytes([bt])
            bt = reader.readByte()
        fileName = fileName.decode().strip('\x00')

        #open file or create file if not found
        fd = os.open(fileName, os.O_WRONLY | os.O_CREAT)
        writer = BufferedFdWriter(fd)

        
        while bt is not None:
            #If we read a \ read next byte
            if bytes([bt]) == b'\\':
                bt = reader.readByte()
                #if we read an e we have hit the terminator close file and break
                if bytes([bt]) == b'e':
                    writer.close()
                    break
                #Else we write current byte ignoring the additional \
                else:
                    writer.writeByte(bt)
                    bt = reader.readByte()
            else:
                #writes bytes that aren't \
                writer.writeByte(bt)
                bt = reader.readByte()
    reader.close()
    
            




    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        errorMsg = "Missing Arguments. Input format: tar [command] [archive list/readable archive] > [optional: outfiles]\n"
        os.write(2, errorMsg.encode())
        exit()
    cmd = sys.argv[1]
    if cmd == 'c':
        archList = sys.argv[2:]
        data = createArch(archList)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    elif cmd == 'x':
        archive = sys.argv[2]
        extractArch(archive)
    elif cmd == 'ic':
        archList = sys.argv[2:]
        data = ibArchive(archList)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    elif cmd == 'ix':
        archive = sys.argv[2]
        ibExtract(archive)
