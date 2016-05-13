#!/usr/bin/python

# VPK version 2 extractor.
# Source: https://developer.valvesoftware.com/wiki/VPK_File_Format/vpk2_reader.py
# I TOTALLY DO NOT CLAIM IT AS MY CODE, I'VE JUST MADE SOME IMPROVEMENTS!
# ALL THE CODE BELONGS TO IT'S AUTHOR!

import os,struct,binascii,sys

if len(sys.argv) < 3:
	print('Usage: vpk_extractor <path to VPKs> <main vpk file name W/O _dir.vpk> [outdir]')
	sys.exit(0)

# where to place extracted files
outDir = os.getcwd() + os.sep + "vpk_extracted"

if len(sys.argv) == 4:
	outDir = sys.argv[3]
	
vpkDir = sys.argv[1]
mainVpkName = sys.argv[2]

def get_int4():
	return int( struct.unpack("I",index.read(4))[0] )
def get_int2():
	return int( struct.unpack("H",index.read(2))[0] )
 
def get_sz():
	out = ""
	while True:
		cur = index.read(1)
		if cur == b'\x00': break
		out += struct.unpack("c",cur)[0].decode("ASCII")
	return out

index = open(sys.argv[1] + os.sep + mainVpkName + '_dir.vpk', 'rb')
 
print( "Signature:",binascii.b2a_hex(index.read(4)) )
print( "Version:",get_int4() )
print( "Directory length:", get_int4() )
print( "Unknown1:", get_int4() )
unknown2 = get_int4() # footer length?
print( "Unknown2:", unknown2 )
unknown3 = get_int4()
print( "Unknown3:", unknown3 )
print( "Unknown4:", get_int4() )
 
class VpkFile():
	path = ""
	CRC = -1
	archive_index = -1
	offset = -1
	length = -1
	preload = bytes()
 
vpk_files = []
 
while True:
	extension = get_sz()
	if not extension: break		
 
	while True:
		folder = get_sz()
		if not folder: break
 
		while True:
			filename = get_sz()
			if not filename: break
 
			cur_file = VpkFile()
			vpk_files.append(cur_file)
			cur_file.path = "{}/{}.{}".format(folder,filename,extension)
 
			cur_file.CRC = get_int4()
			preload_bytes = get_int2()
			cur_file.archive_index = get_int2()
			if cur_file.archive_index == b'\x7fff':
				print("EMBED")
			cur_file.offset = get_int4()
			cur_file.length = get_int4()
			get_int2() # terminator
 
			if preload_bytes:
				cur_file.preload = index.read(preload_bytes)
 
index.close()
 
print("Extracting...")
for vf in vpk_files:
	print(vf.path,"({} bytes)".format(len(vf.preload)+vf.length))
	full_path = os.path.join(outDir, vf.path.replace("/",os.sep))
	dir = os.path.dirname(full_path)
	if not os.path.isdir(dir):
		os.makedirs(dir)
	out_data = open(full_path,'wb')
	out_data.write(vf.preload)
	if vf.length:
		vpk = open(mainVpkName + "_{}.vpk".format(str(vf.archive_index).zfill(3)),'rb')
		vpk.seek(vf.offset)
		out_data.write(vpk.read(vf.length))
		vpk.close()
	out_data.close()
