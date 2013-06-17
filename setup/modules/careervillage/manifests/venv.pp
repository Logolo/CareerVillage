class careervillage::venv {

    python::venv { $careervillage::venv_dir:
        requirements => "${careervillage::source_dir}/requirements.pip",
        user         => $careervillage::user,
        group        => $careervillage::group,
        require      => Class["CareerVillage"];
    }

}