class careervillage::osqa::site {

    include careervillage::venv
    include nginx
    include supervisor

    if $careervillage::target != 'dev' {
        file {
            "${careervillage::root_dir}/careervillage_ssl_key":
                owner   => $user,
                group   => $group,
                mode    => '644',
                ensure  => present,
                source  => "/tmp/careervillage_ssl_key";
            "${careervillage::root_dir}/careervillage_ssl_crt":
                owner   => $user,
                group   => $group,
                ensure  => present,
                mode    => '644',
                source  => "/tmp/careervillage_ssl_crt";
        }
    }

    nginx::vhost { "careervillage::osqa::site":
        name    => "careervillage_osqa",
        content => template("${module_name}/osqa/nginx.conf"),
        require => [Class["careervillage"], Class["nginx"]];
    }

    if $careervillage::target != 'dev' {

        include uwsgi

        supervisor::app { "osqa_site":
            command     => "/usr/local/bin/uwsgi
                                    --socket ${careervillage::run_dir}/osqa_uwsgi.sock

                                    --chmod-socket
                                    --processes 2

                                    --master
                                    --virtualenv ${careervillage::venv_dir}

                                    --pp ${careervillage::app_dir}

                                    --module django.core.handlers.wsgi:WSGIHandler()",

            environment => "DJANGO_SETTINGS_MODULE='settings'",
            user        => $careervillage::user,
            require     => [Python::Venv[$careervillage::venv_dir], Class['careervillage'],
                            Class['careervillage::osqa::deploy']],
            stdout_logfile => "${careervillage::log_dir}/osqa_site_stdout.log",
            stderr_logfile => "${careervillage::log_dir}/osqa_site_stderr.log";
        }

    }

}