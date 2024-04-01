#! /usr/bin/env python3

import os
import sys
from buf import BufferedFdReader, BufferedFdWriter

def createArch(archName,fileList):
    #open the defined archive file
    arch_fd = os.open(archName, os.O_WRONLY| os.O_CREAT)
    writer = BufferedFdWriter(arch_fd)

    #Archive all files listed
    for file in fileList:
        curFile = os.open(file, os.O_RDONLY)
        reader = BufferedFdReader(curFile)
        file_size = os.path.getsize(file)

        #Archive file begins with fileheader
        fileHeader = bytearray(64)
        for i in range(len(file)):
            fileHeader[i] = file[i].encode()[0]#encode the file name
        for i in range(len(str(file_size))):
            fileHeader[i+32] = str(file_size)[i].encode()[0]# then 32 bits later encode the file_size

        #store file contents outside of fileheader
        bt = reader.readByte()
        content = []
        while bt is not None:
            content.append(bt)
            bt=reader.readByte()

        #combine fileheader and contents to be written
        toWrite = fileHeader +  bytearray(content)
        for i in toWrite:
            writer.writeByte(i)
        reader.close()
    writer.close()


def extractArch(archName):
    # Open the archive file for reading
    arch_fd = os.open(archName, os.O_RDONLY)
    reader = BufferedFdReader(arch_fd)
    
    # Loop to extract files
    while True:
        # Read file header
        fileHeader = bytearray(64)
        for i in range(len(fileHeader)):
            byte = reader.readByte()
            if byte is None:
                break
            fileHeader[i] = byte
        
        # Break if there are no more files
        if not any(fileHeader):
            break
        
        # Extract filename and file size from the header
        fileName = fileHeader[:32].decode().strip('\x00')
        fileSize = int(fileHeader[32:64].decode().strip('\x00'))
        
        # Read file content
        fileContent = bytearray()
        for _ in range(fileSize):
            byte = reader.readByte()
            if byte is None:
                break
            fileContent.append(byte)
        
        # Write file to its respective path
        curFile = os.open(fileName, os.O_WRONLY | os.O_CREAT)
        writer = BufferedFdWriter(curFile)
        for i in fileContent:
            writer.writeByte(i)
        writer.close()
    # Close the archive file
    reader.close()

    
def ibArchive(archName, archList):
    arch_fd = os.open(archName, os.O_WRONLY | os.O_CREAT)
    writer = BufferedFdWriter(arch_fd)
    terminator = b'\\'

    
    for fName in archList:
        curFile = os.open(fName, os.O_RDONLY)
        fileHeader = bytearray(32)
        for i in range(len(fName)):
            fileHeader[i] = fName[i].encode()[0]
   
        content = []
        reader = BufferedFdReader(curFile)
        bt = reader.readByte()
        while bt is not None:
            content.append(bt)
            bt = reader.readByte()
        toWrite = fileHeader + bytearray(content) + terminator
        for i in toWrite:
            writer.writeByte(i)
        reader.close()
    writer.close()

def ibExtract(archName):
    #NOT WORKING
    arch_fd = os.open(archName, os.O_RDONLY)
    reader = BufferedFdReader(arch_fd)
    terminator = b'\\'

    #working separation of fileheader for first file
    while True:
        fileHeader = bytearray(32)
        for i in range(len(fileHeader)):
            bt = reader.readByte()
            if bt is None:
                break
            fileHeader[i] = bt
        print(fileHeader) #debugging help
        fileName = fileHeader.decode().strip('\x00')
        if not fileName:
            print("Here 2")
            break
        curFile = os.open(fileName, os.O_WRONLY | os.O_CREAT)
        writer = BufferedFdWriter(curFile)
        bt = reader.readByte()
        while bt is not None:
            if bytes([bt]) == terminator:
                break
            writer.writeByte(bt)
            bt = reader.readByte()
        writer.close()
        if bt is None:
            break
    reader.close()
            




    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        errorMsg = "Missing Arguments. Input format: tar [command] [create/read file] [optional: archiveable file]\n"
        os.write(2, errorMsg.encode())
        exit()
    cmd = sys.argv[1]
    if cmd == 'c':
        archive = sys.argv[2]
        archList = sys.argv[3:]
        createArch(archive,archList)
        os.write(1,"Done!\n".encode())
    elif cmd == 'x':
        archive = sys.argv[2]
        extractArch(archive)
        os.write(1,"Done!\n".encode())
    elif cmd == 'ic':
        archive = sys.argv[2]
        archList = sys.argv[3:]
        ibArchive(archive,archList)
        os.write(1,"Done!\n".encode())
    elif cmd == 'ix':
        archive = sys.argv[2]
        ibExtract(archive)
        os.write(1,"Done!\n".encode())
        
