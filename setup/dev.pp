class dev {

    $target = "dev"
    $root_dir = "/home/vagrant/careervillage"
    $user = "vagrant"
    $group = "vagrant"

    host {
        "careervillage.logging.db":
            ip => "127.0.0.1";
        "careervillage.logging.sentry":
            ip => "127.0.0.1";
        "careervillage.osqa.db":
            ip => "127.0.0.1";
    }

    class { "careervillage":
        target => $target,
        root_dir => $root_dir,
        user => $user,
        group => $group;
    }

    class { "careervillage::osqa::site": }

    class { "careervillage::osqa::db": }

    class { "careervillage::logging::site": }

    class { "careervillage::logging::db": }

    class { "careervillage::cache": }

}

class { "dev": }