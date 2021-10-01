#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paramiko

host = "114.29.154.250"
#host = "bit2farm.iptime.org"

port = 29979

ids = "pheno"
pwd = "kist1966!!!"

# 로컬경로
localPath = "/home/pi/"
#localPath = ""

# 서버경로
serverPath = "/var/www/cams/static/ircam/"
#serverPath = ""

# 파일명
fileName1 = "rgb_ir.jpg"
fileName2 = "B2F_CAMs_1000000000001.jpg"

paramiko.util.log_to_file(localPath + '/sftp.log')


# 소켓 연결 확인
try:
    # 접속
    transport = paramiko.Transport((host, port))
    print(transport.getpeername())
    
    transport.connect(username = ids, password = pwd)
    
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(localPath + fileName1, serverPath + fileName2)
    print("Transfer Success")
finally:
    sftp.close()
    transport.close()


#transport = paramiko.Transport((host, port))
#print(transport.getpeername())
#
#transport.connect(username = ids, password = pwd)
#
#sftp = paramiko.SFTPClient.from_transport(transport)
#sftp.put(localPath + fileName, serverPath + fileName)
#sftp.close()
#transport.close()
