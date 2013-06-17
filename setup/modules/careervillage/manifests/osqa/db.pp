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

}