class careervillage::forum::site {

    include careervillage::venv
    include nginx
    include supervisor

    nginx::vhost { "careervillage::osqa::site":
        name    => "careervillage_osqa",
        content => template("${module_name}/osqa/nginx.conf"),
        require => [Class["careervillage"], Class["nginx"]];
    }

    if $careervillage::target == 'pro' or $careervillage::target == 'sta' {

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