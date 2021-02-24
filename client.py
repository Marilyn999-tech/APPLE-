from socket import *
import sys
from time import sleep


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd=sockfd

    def do_list(self):
        self.sockfd.send(b'L')   #发送请求， 双方协定L表示请求文件列表
        #等待回复
        data=self.sockfd.recv(128).decode()

        if data=='OK':   #请求成功
            data=self.sockfd.recv(4096)   #接收文件列表
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self, filename):
        #发送请求
        self.sockfd.send(('G '+filename).encode())
        #等待回复
        data=self.sockfd.recv(1028).decode()
        if data=='OK':
            fd=open(filename, 'wb')
            #接收内容写入文件
            while True:
                data=self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        try:
            fd = open(filename, 'rb')    #已包含路径
        except Exception:
            print("no such profile")
            return
        # 发送请求
        filename=filename.split('/')[-1] #把路径及文件名分离开来，只取文件名。
        self.sockfd.send(('P ' + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data=fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)


# 发起请求
def request(sockfd):
    ftp = FtpClient(sockfd)

    while True:
        print("\n=====命令选项======")
        print("** list **")
        print("** get file **") #下载文件
        print("** put file **")  # 上传文件
        print("** quit **")
        print("=============================")

        cmd = input("请输入命令： ")
        if cmd.strip() == 'list':  # strip(),去掉两边的空格
            ftp.do_list()
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':  #前三个字母
            filename =cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)



# 网络链接：
def main():
    HOST = '0.0.0.0'
    PORT = 8090
    ADDR = (HOST, PORT)  # 本机地址。如果是网络则写网络地址
    sockfd = socket()

    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print('链接服务器失败')
        return
    else:
        print("****** Data, File, Photo, Audio *******")
        cls = input("请输入文件种类:")
        if cls not in ['Data', 'File', 'Photo', 'Audio']:
            print('Sorry input Error!')
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)  # 发送具体请求


if __name__ == '__main__':
    main()
