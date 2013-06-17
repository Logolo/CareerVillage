class uwsgi {

  package { "uwsgi":
    ensure => installed;
  }

  exec { "uwsgi_pip_install":

      path => "/usr/local/bin:/usr/bin:/bin",

      command => "pip install http://projects.unbit.it/downloads/uwsgi-1.2.tar.gz",

      creates => "/usr/local/bin/uwsgi";

  }

}
