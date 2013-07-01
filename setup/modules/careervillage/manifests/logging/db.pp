class careervillage::logging::db {

    include careervillage::db

    postgresql::database { "cvlogging":
      charset => "utf8",
      require => Class["careervillage::db"];
    }

    postgresql::database_grant { "cvlogging-all":
        privilege => "ALL",
        db        => "cvlogging",
        role      => "careervillage",
        require   => Postgresql::Database["cvlogging"];
    }

    postgresql::database_grant { "cvlogging-connect":
        privilege => "CONNECT",
        db        => "cvlogging",
        role      => "careervillage",
        require   => Postgresql::Database["cvlogging"];
    }

}