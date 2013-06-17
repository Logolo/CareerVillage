class careervillage::logging::db {

    include careervillage::db

    postgresql::database { "zlogging":
      charset => "utf8",
      require => Class["careervillage::db"];
    }

    postgresql::database_grant { "zlogging-all":
        privilege => "ALL",
        db        => "zlogging",
        role      => "careervillage",
        require   => Postgresql::Database["zlogging"];
    }

    postgresql::database_grant { "zlogging-connect":
        privilege => "CONNECT",
        db        => "zlogging",
        role      => "careervillage",
        require   => Postgresql::Database["zlogging"];
    }

}