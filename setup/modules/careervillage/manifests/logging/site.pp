class careervillage::logging::site {

    $sentry_dir = "${careervillage::extras_dir}/sentry"
    $sentry_source = "${sentry_dir}/source"
    $sentry_venv = "${sentry_dir}/venv"

    include nginx
    include supervisor

    nginx::vhost { "careervillage::logging::site":
        name    => "careervillage_logging",
        content => template("${module_name}/logging/nginx.conf"),
        require => [Class["careervillage"], Class["nginx"]];
    }

    file {
        $sentry_dir:
            owner  => $careervillage::user,
            group  => $careervillage::group,
            ensure => directory;
        $sentry_source:
            owner   => $careervillage::user,
            group   => $careervillage::group,
            ensure  => directory,
            require => File[$sentry_dir];
        "${sentry_source}/requirements.pip":
            ensure  => file,
            source  => "puppet:///modules/${module_name}/logging/requirements.pip",
            require => File[$sentry_source];
        "${sentry_source}/settings.py":
            ensure  => file,
            content => template("${module_name}/logging/settings.py.erb"),
            notify  => Service["supervisor"],
            require => File[$sentry_source];
        "${sentry_source}/sentry.json":
            ensure  => file,
            source  => "puppet:///modules/${module_name}/logging/fixture.json",
            require => File[$sentry_source];
    }

    python::venv { $sentry_venv:
        requirements => "${sentry_source}/requirements.pip",
        user         => $careervillage::user,
        group        => $careervillage::group,
        require      => [Class["careervillage"], File["${sentry_source}/requirements.pip"]];
    }

    exec { "sentry --config=settings.py loaddata sentry.json":
        path    => "${sentry_venv}/bin",
        cwd     => "${sentry_source}",
        require => [Python::Venv[$sentry_venv], File["${sentry_source}/sentry.json"]];
    }

    supervisor::app { "cvlogging_site":
        command     => "${sentry_venv}/bin/sentry --config=settings.py start",
        directory   => "${sentry_source}",
        environment => "PATH=\"${sentry_venv}/bin\"",
        user        => $careervillage::user,
        require     => Python::Venv[$sentry_venv],
        stdout_logfile => "${careervillage::log_dir}/logging_site_stdout.log",
        stderr_logfile => "${careervillage::log_dir}/logging_site_stderr.log";
    }

    exec { "cvlogging_site_restart":
         command => "/usr/bin/supervisorctl restart cvlogging_site",
         require => Supervisor::App["cvlogging_site"];
    }

}