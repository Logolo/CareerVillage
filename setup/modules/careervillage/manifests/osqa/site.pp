class careervillage::osqa::site {

    include careervillage::venv
    include nginx
    include supervisor

    if $careervillage::target != 'dev' {
        file {
            "${careervillage::data_dir}/careervillage_ssl_key":
                owner   => $user,
                group   => $group,
                mode    => '644',
                ensure  => present,
                source  => "/tmp/careervillage_ssl_key";
            "${careervillage::data_dir}/careervillage_ssl_crt":
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


        if $careervillage::target == 'local' {

            supervisor::app { "osqa_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket ${careervillage::run_dir}/osqa_uwsgi.sock

                                        --chmod-socket
                                        --processes 2

                                        --master
                                        --virtualenv ${careervillage::venv_dir}

                                        --pp ${careervillage::app_dir}

                                        --module wsgi:application",

                environment => "DJANGO_SETTINGS_MODULE='settings'",
                user        => $careervillage::user,
                require     => [Class["careervillage::venv"],
                                Class["careervillage"],
                                Class["careervillage::osqa::deploy"]],
                stdout_logfile => "${careervillage::log_dir}/osqa_site_stdout.log",
                stderr_logfile => "${careervillage::log_dir}/osqa_site_stderr.log";
            }

            exec { "osqa_site_restart":
                 command => "/usr/bin/supervisorctl restart osqa_site",
                 require => Supervisor::App["osqa_site"];
            }

        } else {

            exec { 'careervillage::osqa::site::newrelic':
                command   => "newrelic-admin generate-config ${::careervillage_newrelic_license} ${careervillage::data_dir}/newrelic.ini",
                cwd       => $careervillage::app_dir,
                user      => $careervillage::user,
                group     => $careervillage::group,
                path      => "${careervillage::venv_dir}/bin",
                logoutput => "on_failure",
                require   => Class["careervillage::venv"];
            }

            supervisor::app { "osqa_site":
                command     => "/usr/local/bin/uwsgi
                                        --socket ${careervillage::run_dir}/osqa_uwsgi.sock

                                        --chmod-socket
                                        --processes 2

                                        --master
                                        --virtualenv ${careervillage::venv_dir}

                                        --pp ${careervillage::app_dir}

                                        --module wsgi:application",

                environment => "DJANGO_SETTINGS_MODULE='settings',NEW_RELIC_CONFIG_FILE='${careervillage::data_dir}/newrelic.ini'",
                user        => $careervillage::user,
                require     => [Exec["careervillage::osqa::site::newrelic"],
                                Class["careervillage::osqa::deploy"]],
                stdout_logfile => "${careervillage::log_dir}/osqa_site_stdout.log",
                stderr_logfile => "${careervillage::log_dir}/osqa_site_stderr.log";
            }

            exec { "osqa_site_restart":
                 command => "/usr/bin/supervisorctl restart osqa_site",
                 require => Supervisor::App["osqa_site"];
            }

        }
    }

}