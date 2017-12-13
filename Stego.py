#encoding:utf-8
from PIL import Image
from os.path import basename, abspath, dirname, join

class BmpStego:
    def __init__(self,imgfile):
        self.imgFile = imgfile
        self.img = Image.open(self.imgFile)
        self.pixel = self.img.load()
        self.imgSize = self.img.size
        if not self.img.mode.startswith("RGB"):
            raise Exception("只支持24位真彩色的图片隐写")

    def writeData(self,data,startpos):
        """
        数据写入方式为行写入，同时一个像素最多保存三个比特位，一个字节最终保存为：GRBGRBGR。
        三个像素保存一个字节
        :param data: instance of bytes
        :param startpos: (x,y)
        :return:
        """
        length_of_data = len(data)
        pixel_to_write = length_of_data * 3
        tmp_x = startpos[0]
        tmp_y = startpos[1]
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

    def saveImg(self):
        abs_path = abspath(self.imgFile)
        dir_name = dirname(abs_path)
        try:
            dot_index = self.imgFile.index(".")
        except ValueError:
            dot_index = 0
        if dot_index!=0 and dot_index!=len(self.imgFile)-1:
            file_name = self.imgFile[:dot_index]
            file_ext = self.imgFile[dot_index+1:]
        else:
            file_name = self.imgFile
            file_ext = ""
        self.img.save(join(dir_name,file_name+".steg."+file_ext))

if __name__=="__main__":
    test = BmpStego(r"d:\test.jpg")
    test.writeData(b"abc",(0,0))
    test.saveImg()