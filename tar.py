#! /usr/bin/env python3

import os
import sys
import struct
from buf import BufferedFdReader, BufferedFdWriter

def createArch(archName,fileList):
    arch_fd = os.open(archName, os.O_WRONLY | os.O_CREAT)
    writer = BufferedFdWriter(arch_fd)
    for fName in fileList:
        fBytes = fName.encode()
        writer.writeByte(len(fBytes))
        for byte in fBytes:
            writer.writeByte(byte)
        fSize = os.fstat(fBytes)
        for byte in struct.pack("!Q", fSize):
            writer.writeByte(byte)
        curFile = os.open(fName,os.O_RDONLY)
        reader = BufferedFdReader(curFile)
        bufferedCopy(reader,writer)
        os.close(curFile)
        reader.close()
    writer.close()
    os.close(arch_fd)
        
'''
def extractArch(archName):
    output_dir = os.path.splitext(archName)[0]
    os.makedirs(output_dir,exist_ok=True)

    arch = os.open(archName,os.O_RDONLY)
    reader = BufferedFdReader(arch)
    while True:
        nameByte = reader.readByte()
        if nameByte is None:
            break
        nameSize = int.from_bytes(nameByte, byteorder='big')
        fileNameBytes = b''
        for byte in nameSize:
            fileNameBytes += reader.readByte(byte)
        if fileNameBytes is None:
            break
        fileName = fileNameBytes.decode()
        fileSize = fstat()
    
    
'''
def extractArch(archName):
    readableArch = os.open(archName,os.O_RDONLY)
    read = os.read(readableArch,1).decode()
    while read != "":
        fNameSize = ""
        fSize = ""
        while read != ":":
            fNameSize = fNameSize + read
            read = os.read(readableArch, 1).decode()
        fName = os.read(inputFile, int(fNameSize)).decode()
        outFile = os.open(fName, os.O_WRONLY | os.O_CREAT)
        read = os.read(readableArch, 1).decode()
        while read != ":":
            fSize = fSize + read
            read = os.read(readableArch, 1).decode()
        os.write(outFile, os.read(readableArch, int(fSize)))
        read = os.read(readableArch, 1).decode()
        os.close(outFile)
    os.close(readableArch)

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
        
