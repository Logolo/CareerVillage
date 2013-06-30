class careervillage ($target, $root_dir, $user, $group) {

    $source_dir = "${root_dir}/source"
    $log_dir    = "${root_dir}/log"
    $run_dir    = "${root_dir}/run"
    $extras_dir = "${root_dir}/extras"
    $data_dir   = "${root_dir}/data"
    $cache_dir  = "${root_dir}/cache"
    $venv_dir   = "${root_dir}/venv"
    $app_dir    = "${source_dir}/app"

    Exec {
        path => '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    }

    class { 'apt':
        always_apt_update => true;
    }

    group { $group:
        ensure => present;
    }

    user { $user:
        ensure     => present,
        managehome => true,
        shell      => '/bin/bash',
        gid        => $user,
        groups     => [$group],
        require    => Group[$group];
    }


    file {
        $root_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => User[$user];
        $log_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
        $run_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
        $data_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
        $cache_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
        $extras_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
    }

    file { "/home/${user}/.bashrc":
        owner   => $user,
        group   => $group,
        mode    => '755',
        content => template("${module_name}/bashrc.erb"),
        require => User[$user];
    }

    if $target == 'dev' {
        file { $source_dir:
            owner   => $user,
            group   => $group,
            ensure  => directory,
            require => [File[$root_dir], User[$user]];
        }
    }

    if $target == 'pro' or $target == 'local' {

        class { 'careervillage::code':
            user       => $user,
            group      => $group,
            source_dir => $source_dir;
        }

    }

    package { 'libjpeg8-dev':
        ensure   => 'installed',
        provider => 'apt';
    }

    package { 'libjpeg8':
        ensure   => 'installed',
        provider => 'apt';
    }

    package { 'libfreetype6':
        ensure   => 'installed',
        provider => 'apt';
    }

    package { 'libfreetype6-dev':
        ensure   => 'installed',
        provider => 'apt';
    }

    package { 'zlib1g-dev':
        ensure   => 'installed',
        provider => 'apt';
    }

    package { ['libxml2-dev', 'libxslt1-dev', 'libpng-dev',
               'liblcms1-dev', 'libpq-dev', 'make',
               'subversion', 'git-core']:
        ensure   => installed,
        provider => 'apt';
    }

    #install libs for PIL
    file {
        '/usr/lib/libjpeg.so':
            ensure  => link,
            target  => '/usr/lib/x86_64-linux-gnu/libjpeg.so',
            require => [Package['libjpeg8'], Package['libjpeg8-dev']];
        '/usr/lib/libfreetype.so':
            ensure  => link,
            target  => '/usr/lib/x86_64-linux-gnu/libfreetype.so',
            require => [Package['libfreetype6-dev'], Package['libfreetype6']];
        '/usr/lib/libz.so':
            ensure  => link,
            target  => '/usr/lib/x86_64-linux-gnu/libz.so',
            require => Package['zlib1g-dev'];
    }

}