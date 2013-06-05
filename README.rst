CareerVillage
=============

CareerVillage is an online community which helps students discover post-education career options and understand what they've got to do to pursue those careers. The primary feature of the site is a Q&A forum where students can ask career and professional development questions, and where working professionals can answer those questions. 

CareerVillage is a non-profit organization. You can find out more, and see the site live, at www.careervillage.org 

Cloning and installing CareerVillage
====================================

The following describes the steps required to fully install CareerVillage on a development machine 

Getting "pip"
------------
Assuming you're on a Mac or running Linux, pip will help install the rest of CareerVillage's dependencies quickly and easily. Run these commands from a terminal::

	$ curl -O http://python-distribute.org/distribute_setup.py
	$ python distribute_setup.py

Or, if you have easy_install on your machine, do this instead::

	$ sudo easy_install pip

Installing Dependencies
-----------------------
Virtual environments help keep local settings and global settings between projects seperate, so that configuring CareerVillage doesn't accidentally break other projects. 

To create the virtual environment, 
	$ curl -0 https://github.com/jchubber/CareerVillage/blob/master/install_cv.sh
	$ . install_cv.sh

The script is very simple; open it up and see. It creates the virtual environment, and then runs around installing dependencies using pip.

Edit settings
-------------

Open settings_local.py for editing. Find the database settings and edit them to reflect the settings for the database you will be using. If you are using sqlite3, you should use the following settings:

    DATABASE_NAME = "whatever" #You can put whatever you want here  
    DATABASE_USER = "whatever" #You can put whatever you want here  
    DATABASE_PASSWORD = ""  
    DATABASE_ENGINE = "sqlite3"  
    DATABASE_HOST = ''  
    DATABASE_PORT = ''  
    
Create the database schema
--------------------------

Open a shell, get into the folder where this repo lives, and run:

    python manage.py syncdb --all  
    python manage.py migrate forum --fake  

If you have all of the dependencies, this should setup the databases. 

Run the development server
--------------------------

Now run:

    python manage.py runserver
    python manage.py celery worker --loglevel=info --autoreload
    
Open a browser and go to http://localhost:8000/ to see the skeleton OSQA site up and running.

Create the main admin
---------------------

The first user to be created is automatically the admin, so create the account quickly. You can go straight to the new account creation page here: http://localhost:8000/account/local/register/

Apply site customization settings
---------------------------------

The site requires CSS customization. Log into the site and navigate to the administration area. Copy and paste the following CSS styles into the appropriate setion of the "Custom CSS" page.
::
    .boxA {background-color: #FF6600;}  
    body {background-color: #3CA0D1;}  
    #wrapper {background-color: #FFFFFF;}  
    #ground {background-color: #FFFFFF;}  
    
    #top {  
        /* background-color: #00a2d3; */  
        background-color: #ffffff;  
        font-weight: bold;  
    }  
    
    #searchBar {background-color: #AEE8FB;}  
    #searchBar form {background-color: #AEE8FB;}  
    #CARight h2 {color:#A40000;}  

Resources
=========
::
CareerVillage site: http://www.careervillage.org/
CareerVillage blog: http://careervillage.wordpress.com/
OSQA main site: http://www.osqa.net/
OSQA Installation and Upgrade Guides: http://wiki.osqa.net/display/docs/OSQA+Installation+and+Upgrade+Guides
Setting up a development environment: http://wiki.osqa.net/display/docs/Setting+up+a+development+environment+on+Windows
