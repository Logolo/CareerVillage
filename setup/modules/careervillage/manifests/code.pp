class careervillage::code ($user, $group, $source_dir) {

        $git_repo   = "${::careervillage_git_repo}"
        $git_branch = "${::careervillage_git_branch}"
        $git_key = "careervillage_git"

        file {
            "/home/${user}/.ssh":
                owner  => $user,
                group  => $group,
                ensure => directory;
            "/home/${user}/.ssh/${git_key}":
                owner   => $user,
                group   => $group,
                mode    => '600',
                ensure  => present,
                source  => "/tmp/careervillage_git",
                require => File["/home/${user}/.ssh"];
            "/home/${user}/.ssh/${git_key}.pub":
                owner   => $user,
                group   => $group,
                ensure  => present,
                source  => "/tmp/careervillage_git.pub",
                require => File["/home/${user}/.ssh"];
        }

        vcsrepo { 'source':
            ensure   => latest,
            provider => git,
            source   => "${git_repo}",
            revision => "${git_branch}",
            owner    => $user,
            user     => $user,
            group    => $group,
            path     => $source_dir,
            identity => "/home/${user}/.ssh/${git_key}",
            require  => File["/home/$user/.ssh/${git_key}"];
        }

}