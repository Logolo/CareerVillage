Bootstrap
=========

Ruby and Gems
-------------

Install Ruby: https://rvm.io/

::

    gem install vagrant
    gem install vagrant-vbguest
    vagrant up dev

PyCharm Configuration
---------------------

Create PyCharm remote directory
::

    vagrant ssh dev
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

Run Site
========
::

    vagrant ssh dev
    ./manage.py reset_db
    ./manage.py runserver


Run Celery
==========
::

    python manage.py celery worker --loglevel=info --autoreload


Browse
::

    http://development.careervillage.org:8000/
    http://logging.development.careervillage.org:9000/

Forwarded ports
---------------
::

    80    => 8000  (http)
    9001  => 9000  (sentry)
    5432  => 5433  (postgres)
    55672 => 55673 (rabbitmq)


Before deploying
================

Add the following to your ~/.ssh/config
::

	Host careervillage_pro
	       	Hostname careervillage.webfactional.com
        	User careervillage
	        Port 22
        	IdentityFile /home/%u/.ssh/careervillage_pro

	Host careervillage_sta
	        HostName staging.careervillage.org
        	User ubuntu
        	Port 22
	        IdentityFile /home/%u/.ssh/careervillage_sta
