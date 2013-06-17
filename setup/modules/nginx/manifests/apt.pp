class nginx::apt {
  apt::source { "nginx":
    location => "http://nginx.org/packages/ubuntu/",
    release => "precise",
    key => "ABF5BD827BD9BF62",
    repos => "nginx";
  }
}
