class master {

    $target = $::careervillage_target
    $root_dir = "/home/careervillage/careervillage"
    $user = "careervillage"
    $group = "careervillage"

    host {
        "careervillage.osqa.db":
            ip => $::careervillage_osqa_db_address;
        "careervillage.osqa.cache":
            ip => $::careervillage_osqa_cache_address;
    }

    class { "careervillage":
        target => $target,
        root_dir => $root_dir,
        user => $user,
        group => $group;
    }

    class { "careervillage::osqa::site": }

    class { "careervillage::osqa::db": }

    class { "careervillage::osqa::deploy": }

    class { "careervillage::cache": }

    class { "careervillage::rabbitmq": }

    if $target != 'local' {

        class { "newrelic":
            license => "${::careervillage_newrelic_license}"
        }

    }

}

class { "master": }