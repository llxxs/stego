#encoding:utf-8
from PIL import Image
from os.path import abspath, dirname, join
import sys

class BmpStego:
    def __init__(self,imgfile):
        self.imgFile = imgfile
        self.img = Image.open(self.imgFile)
        self.pixel = self.img.load()
        self.imgSize = self.img.size
        if (not self.img.mode.startswith("RGB")) and (self.img.format not in ["BMP","PNG"]):
            raise Exception("只支持24位真彩色的BMP/PNG图片隐写")

    def writeData(self,data,offset):
        """
        数据写入方式为行写入，同时一个像素最多保存三个比特位，一个字节最终保存为：GRBGRBGR。
        三个像素保存一个字节
        :param data: instance of bytes
        :param startpos: (x,y)
        :return:
        """
        length_of_data = len(data)
        tmp_x, tmp_y = self.offsetToPoint(offset)
        i = 0
        while i < length_of_data:
            abyte = bin(data[i])[2:]
            abyte = "0"*(8-len(abyte)) + abyte #补齐八位
            try:
                for no in range(3):
                    R, G, B, *other = self.pixel[tmp_x, tmp_y]
                    R &= 0b11111110
                    R |= int(abyte[8 - 1 - 3 * no])
                    G &= 0b11111110
                    G |= int(abyte[8 - 2 - 3 * no])
                    if no!=2:
                        B &= 0b11111110
                        B |= int(abyte[8 - 3 - 3 * no])
                    self.pixel[tmp_x,tmp_y] = (R, G, B) + tuple(other)
                    if tmp_x+1 == self.imgSize[0]:
                        if tmp_y+1 == self.imgSize[1]:
                            raise IndexError()
                        else:
                            tmp_y += 1
                            tmp_x = 0
                    else:
                        tmp_x += 1
            except IndexError:
                raise IndexError("读取索引超出范围")
            i += 1
        return length_of_data

    def readData(self,length,offset):
        data = bytearray(length)
        tmp_x, tmp_y = self.offsetToPoint(offset)
        for i in range(length):
            tmp_value = []
            try:
                for no in range(3):
                    R, G, B, *other = self.pixel[tmp_x, tmp_y]
                    R &= 1
                    tmp_value.append(str(R))
                    G &= 1
                    tmp_value.append(str(G))
                    if no!=2:
                        B &= 1
                        tmp_value.append(str(B))
                    if tmp_x+1 == self.imgSize[0]:
                        if tmp_y+1 == self.imgSize[1]:
                            raise IndexError()
                        else:
                            tmp_y += 1
                            tmp_x = 0
                    else:
                        tmp_x += 1
                tmp_value.reverse()
                data[i] = int("".join(tmp_value),2)
            except IndexError:
                raise IndexError("读取索引超出范围")
        return data

    def saveImg(self):
        abs_path = abspath(self.imgFile)
        dir_name = dirname(abs_path)
        self.img.save(join(dir_name,"steg_"+self.imgFile))

    def writeFile(self,filepath):
        offset = 0 #写入的偏移
        with open(filepath,"rb") as file:
            file_data = file.read()
        file_length = len(file_data)
        if self.imgSize[0] * self.imgSize[1] / 3 < file_length:
            print("图片文件太小，无法隐写目标文件")
            exit()
        file_length_data = self.intToFixByte(file_length) #写入四个字节的整数
        offset += self.writeData(file_length_data, offset)
        offset += self.writeData(file_data, offset)
        self.saveImg()
        return file_length

    def extractFile(self,filepath):
        offset = 0 #读取的偏移
        file = open(filepath,"wb")
        file_length_data = self.readData(4,offset)
        offset += 4
        file_length = self.fixByteToInt(file_length_data)
        file_data = self.readData(file_length,offset)
        file.write(file_data)
        return file_length

    def intToFixByte(self,value):
        result = bytearray(4)
        for i in range(4):
            result[3-i] = (value & (0xff<<i*8))>>(i*8)
        return bytes(result)

    def fixByteToInt(self,fixbyte):
        result = 0
        for i in range(4):
            result += fixbyte[3-i] << (i*8)
        return result

    def offsetToPoint(self,offset):
        offset *= 3
        x = offset % self.imgSize[0]
        y = offset // self.imgSize[0]
        return (x,y)

def help():
    helpinfo = """\
Usage:
    %s impact source_file target_file ;Impact target_file into steg_source_file
    %s extract source_file target_file ; Extract target_file from source_file
    For example: %s impact test.bmp test.txt
    """
    helpinfo = helpinfo % ((sys.argv[0],) * 3)
    print(helpinfo)
    exit()

if __name__=="__main__":
    argc = len(sys.argv)
    if argc!=4:
        help()
    action = sys.argv[1]
    source_file = sys.argv[2]
    target_file = sys.argv[3]
    bmp_stego = BmpStego(source_file)
    if action=="impact":
        result = bmp_stego.writeFile(target_file)
        if result:
            print("成功写入")
    else:
        result = bmp_stego.extractFile(target_file)
        if result:
            print("成功解压")
