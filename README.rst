CareerVillage
=============

CareerVillage is an online community which helps students discover post-education career options and understand what they've got to do to pursue those careers. The primary feature of the site is a Q&A forum where students can ask career and professional development questions, and where working professionals can answer those questions. 

CareerVillage is a non-profit organization. You can find out more, and see the site live, at www.careervillage.org 

Cloning and installing CareerVillage
====================================

The following describes the steps required to fully install CareerVillage on a development machine 

External dependencies
---------------------

CareerVillage is extended from the OSQA platform. It has the following external dependencies:

- Django, at least version 1.1
- Python markdown
- html5lib
- Python OpenId
- South 

Assuming you have python, django, and git installed, we recommend easy_install for acquiring the external dependencies:

    easy_install markdown
    easy_install html5lib
    easy_install south
    easy_install python-openid
    easy_install django-debug-toolbar 

Clone this repository
---------------------

Clone the repo with the following command   

    git clone git@github.com:jchubber/CareerVillage.git

Edit settings
-------------

Get into the OSQQA sources folder. Copy the file settings_local.py.dist and rename the copy settings_local.py. Open this new settings_local.py file for editing. Find the database settings and edit them to reflect the settings for the database you will be using. If you are using sqlite3, you should use the following settings:

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
    
Open a browser and go to http://localhost:8000/ to see the skeleton OSQA site up and running.

Create the main admin
---------------------

The first user to be created is automatically the admin, so create the account quickly. You can go straight to the new account creation page here: http://localhost:8000/account/local/register/

Apply site customization settings
---------------------------------

The site requires CSS customization. Log into the site and navigate to the administration area. Copy and paste the following CSS styles into the appropriate setion of the "Custom CSS" page.

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

CareerVillage site: http://www.careervillage.org/
CareerVillage blog: http://careervillage.wordpress.com/
OSQA main site: http://www.osqa.net/
OSQA Installation and Upgrade Guides: http://wiki.osqa.net/display/docs/OSQA+Installation+and+Upgrade+Guides
Setting up a development environment: http://wiki.osqa.net/display/docs/Setting+up+a+development+environment+on+Windows