Vagrant::Config.run do |config|

    config.vm.host_name = "careervillage"
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    config.vm.customize ["modifyvm", :id, "--rtcuseutc", "on"]

    config.vm.define :dev do |master_config|

        master_config.vm.share_folder "project", "/home/vagrant/careervillage/source", "."

        master_config.vm.forward_port 80,    8000    #app
        master_config.vm.forward_port 9001,  9000    #sentry
        master_config.vm.forward_port 5432,  5433    #postgres
        master_config.vm.forward_port 55672, 55673   #rabbitmq

        master_config.vm.provision :puppet do |puppet|
          puppet.manifests_path = "setup"
          puppet.module_path = "setup/modules"
          puppet.manifest_file  = "dev.pp"
          puppet.options = "--verbose --debug"
        end

      end

      config.vm.define :master do |master_config|

        master_config.vm.network :hostonly, "10.0.1.10"

      end

end