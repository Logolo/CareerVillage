Environments
============

* Puts your ec2 keys and git keys on /keys directory.
* Populate your tools/cvt/cvt/conf/settings_local.py

DEV (development)
-----------------

See :topcis/bootstrap: page.


LOCAL
-----

Edit your /etc/hosts and add:
::

    10.1.0.10       local.careervillage.org

Run
::

    vagrant up local
    ./cvt setup -r master


STA (staging)
-------------

Deploy staging:

* Create a EC2 machine (OS: Ubuntu and Key: careervillage_sta_ec2)
* Add the following tags: Role=master Target=sta

::

    ./cvt setup -r master -t sta


PRO (production)
----------------

* Create a EC2 machine (OS: Ubuntu and Key: careervillage_pro_ec2)
* Add the following tags: Role=master Target=pro

Deploy production:

::

    ./cvt setup -r master -t pro

