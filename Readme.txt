Last Update: 7/13/2020 by Mark Gardner
*****************************************************************************************************************
Requirements:
	Python 3.x (3.6 or higher is preferred)
	pip (Comes Standard with newer versions of Python)
*****************************************************************************************************************
*****************************************************************************************************************
You can use this command set to take care of all of the installs and configurations at once:

#Assuming that you can run pip directly. You may need to run pip command as pip3 depending on your environment
#You can also set up a link/alias to pip3 command if your pip version is pip3.x
for package in "Flask flask-wtf flask-sqlalchemy flask-bcrypt flask-login Pillow"; do sudo pip install $package; done

#change directory to package location:
The program should run fine from Project Directory by running: python titan2.py

However, you can also run the engine separately or add the flask engine to /etc/init.d (rc.d)
To run it:
	#cd to application home directory and type:
	# export FLASK_APP=titan2.py
	# export FLASK_DEBUG=1 for DEV. (Allows Server to Continue Running and provides debug info.)
	#		Turn off Debug for PROD use. ('export FLASK_DEBUG=0')
	# flask run
******************************************************************************************************************
