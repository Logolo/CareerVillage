class careervillage::cache {

    class { "memcached":
        subscribe => Vcsrepo['source'];
    }

}