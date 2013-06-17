class code {

    $target = $::careervillage_target
    $root_dir = "/opt/careervillage"
    $user = "yoda"
    $group = "careervillage"

    class { 'careervillage::code':
        user       => $user,
        group      => $group,
        source_dir => "${root_dir}/source";
    }

}

class { "code": }