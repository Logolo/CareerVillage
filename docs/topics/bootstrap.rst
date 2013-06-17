Bootstrap
=========

Ruby and Gems
-------------
::

    gem install vagrant
    gem install vagrant-vbguest
    vagrant up

PyCharm
-------

Create PyCharm remote directory
::

    vagrant ssh
    sudo mkdir /opt/pycharm
    sudo chown vagrant:vagrant /opt/pycharm

Go to: ``File > Settings > Python Interpreters > Add``
::

    Host: localhost
    Port: 2222
    User: vagrant
    Auth Type: Password
    Password: vagrant

    Python Interpreter: /opt/careervillage/venv/bin/python
    Copy Pycharm helpers to: /opt/pycharm

Edit your /etc/hosts
--------------------
::

    127.0.0.1       development.careervillage.org
    127.0.0.1       logging.development.careervillage.org

Run CareerVillage
============
::

    vagrant ssh
    ./manage.py reset_db
    ./manage.py runserver


Browse
::

    http://development.careervillage.org:8000/

Forwarded ports
---------------

80 => 8000 (http)

5432 => 5433 (postgres)


Before deploying
================

Add the following to your ~/.ssh/config
::

	Host careervillage_pro
	       	Hostname careervillage.org
        	User ubuntu
	        Port 22
        	IdentityFile /home/%u/.ssh/careervillage_pro

	Host careervillage_sta
	        HostName staging.careervillage.org
        	User ubuntu
        	Port 22
	        IdentityFile /home/%u/.ssh/careervillage_sta
