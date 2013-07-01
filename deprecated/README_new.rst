CareerVillage
=============

CareerVillage is an online community which helps students discover post-education career options and understand what they've got to do to pursue those careers. The primary feature of the site is a Q&A forum where students can ask career and professional development questions, and where working professionals can answer those questions. 

CareerVillage is a non-profit organization. You can find out more, and see the site live, at www.careervillage.org 

Cloning and installing CareerVillage
====================================
CareerVillage has a two-step install process, aided by the script `install_cv.sh`. Assuming you're on a *nix machine, navigate to wherever you want careervillage to install and run these commands in a terminal:

	$ curl -0 https://github.com/jchubber/CareerVillage/blob/master/install_cv.sh
	$ . install_cv.sh

And you're done!

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
