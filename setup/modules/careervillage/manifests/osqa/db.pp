class careervillage::osqa::db () {

    include careervillage::db

    postgresql::database { "cvosqa":
      charset => "utf8",
      owner   => "careervillage",
      require => Class["careervillage::db"];
    }

    postgresql::database_grant { "cvosqa-all":
        privilege => "ALL",
        db => "cvosqa",
        role => "careervillage",
        require   => Postgresql::Database["cvosqa"];
    }

    postgresql::database_grant { "cvosqa-connect":
        privilege => "CONNECT",
        db => "cvosqa",
        role => "careervillage",
        require   => Postgresql::Database["cvosqa"];
    }

    if $careervillage::target == 'pro' {

        file { "${careervillage::extras_dir}/dump.sh":
            owner   => $user,
            group   => $group,
            mode    => '755',
            content => template("${module_name}/osqa/dump.sh.erb"),
            require => Class["careervillage"];
        }

        cron { logrotate:
          command => "",
          user    => root,
          minute  => '*/5',
          require => File["${careervillage::extras_dir}/dump.sh"];
        }

    }

}