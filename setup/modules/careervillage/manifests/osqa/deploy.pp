class careervillage::osqa::deploy {

    include supervisor
    include careervillage::venv

    if $careervillage::target != 'dev' {

        file { "${careervillage::app_dir}/settings_local.py":
            owner   => $careervillage::user,
            group   => $careervillage::group,
            ensure  => present,
            content => template("${module_name}/osqa/settings_local.py.erb"),
            require => Vcsrepo['source'];
        }

        if $careervillage::target != 'pro' and $::careervillage_reset_db == 'true' {
            exec { 'careervillage::osqa::deploy::db':
                command   => "python manage.py reset_db --traceback",
                cwd       => $careervillage::app_dir,
                user      => $careervillage::user,
                group     => $careervillage::group,
                path      => "${careervillage::venv_dir}/bin",
                logoutput => "on_failure",
                require   => [Postgresql::Database_grant["cvosqa-all"],
                            File["${careervillage::app_dir}/settings_local.py"],
                            Class["careervillage::venv"]];
            }
        } else {
            exec { 'careervillage::osqa::deploy::db':
                command   => "python manage.py syncdb --noinput --migrate --traceback",
                cwd       => $careervillage::app_dir,
                user      => $careervillage::user,
                group     => $careervillage::group,
                path      => "${careervillage::venv_dir}/bin",
                logoutput => "on_failure",
                require   => [Postgresql::Database_grant["cvosqa-all"],
                            File["${careervillage::app_dir}/settings_local.py"],
                            Class["careervillage::venv"]];
            }
        }

        supervisor::app { "cvosqa_celery":
            command     => "python manage.py celery worker --loglevel=info",
            directory   => $careervillage::app_dir,
            environment => "PATH=\"${careervillage::venv_dir}/bin\"",
            user        => $careervillage::user,
            require     => [Exec['careervillage::osqa::deploy::db']],
            stdout_logfile => "${careervillage::log_dir}/osqa_celery_supervisor_stdout.log",
            stderr_logfile => "${careervillage::log_dir}/osqa_celery_supervisor_stderr.log";
        }

        exec { "cvosqa_celery_restart":
             command => "/usr/bin/supervisorctl restart cvosqa_celery",
             require => Supervisor::App["cvosqa_celery"];
        }

    }
}