class careervillage::newrelic {

    class { "newrelic":
        license => "{$::careervillage_newrelic_license}"
    }

}