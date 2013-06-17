class pro {

    $target = "pro"
    $root_dir = "/home/careervillage/careervillage"
    $user = "careervillage"
    $group = "careervillage"

    host {
        "careervillage.logging.db":
            ip => $::careervillage_logging_db_address;
        "careervillage.logging.sentry":
            ip => $::careervillage_logging_sentry_address;
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

    class { "careervillage::osqa::db": }

    class { "careervillage::osqa::deploy" }

    class { "careervillage::logging::site": }

    class { "careervillage::logging::db": }

    class { "careervillage::cache": }

}

class { "pro": }