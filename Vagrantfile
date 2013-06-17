Vagrant::Config.run do |config|

  config.vm.host_name = "careervillage"
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.customize ["modifyvm", :id, "--rtcuseutc", "on"]

  config.vm.share_folder "project", "/opt/careervillage/source", "."

  config.vm.forward_port 80,    8000    #app
  config.vm.forward_port 9000,  9001    #sentry
  config.vm.forward_port 5432,  5433    #postgres
  config.vm.forward_port 55672, 55673   #rabbit

  master_config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "setup"
    puppet.module_path = "setup/modules"
    puppet.manifest_file  = "dev.pp"
    puppet.options = "--verbose --debug"
  end

end