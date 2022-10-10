#!/bin/bash

#deployment of LARA_GAMES as Virtual machine

#default os centos7

GIT_URL=https://github.com/vadim566/laragames.git  #git url
DIR_NAME=laragames


yum --help #check if centos
if [ $? -eq 0 ]
then
	#general centos updates
	
	#sudo yum update -y
	sudo yum install git -y
	
	##get git latest version
	git clone $GIT_URL
	
	##get python
	sudo yum install python3 -y

	##create python virtual enviorment
	cd $DIR_NAME/
 	sudo python3 -m venv venv
	source venv/bin/activate
	
	##upgrade pip
	pip install --upgrade pip
	pip install -r requirements.txt
	
	##run app
	source venv/bin/activate
	python3 app.py
else
	echo "The script built for centos7"
	
fi