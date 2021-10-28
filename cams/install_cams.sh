#!/bin/bash

#설정파일 이름
conf=cams.conf

#기존 사이트 제거
sudo a2dissite 000-default.conf

#cams 사이트 추가
sudo ln -f -s `pwd`/$conf /etc/apache2/sites-available/$conf
sudo a2ensite $conf

#설정 테스트
sudo apache2ctl configtest
