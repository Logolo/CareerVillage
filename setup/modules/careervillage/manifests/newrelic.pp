class careervillage::newrelic {

    package { "rabbitmq-server": } ->

    exec { "careervillage::rabbitmq::admin":
        command => "/usr/lib/rabbitmq/lib/rabbitmq_server-2.7.1/sbin/rabbitmq-plugins enable rabbitmq_management",
        notify  => Service["rabbitmq-server"],
        refreshonly => true;
    }

    class { "newrelic":
        license => "{$::careervillage_newrelic_license}"
    }

}