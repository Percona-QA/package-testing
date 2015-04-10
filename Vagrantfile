# -*- mode: ruby -*-
# vi: set ft=ruby :

deb_distro = "squeeze"
deb1_playbook = "playbooks/pxc55.yml"
deb_common_playbook = "playbooks/pxc55_common.yml"
rhel_distro = "centos5"
rhel1_playbook = "playbooks/percona1.yml"
rhel_playbook = "playbooks/common_rpm.yml"

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most pxb configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  config.vm.define :squeeze do |squeeze_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    squeeze_config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_debian-6.0.10_chef-provisionerless.box"
    squeeze_config.vm.box = "squeeze"
    squeeze_config.vm.host_name = "squeeze"
    squeeze_config.vm.network :private_network, ip: "192.168.20.51"
  end

  config.vm.define :wheezy do |wheezy_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    wheezy_config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_debian-7.8_chef-provisionerless.box"
    wheezy_config.vm.box = "wheezy"
    wheezy_config.vm.host_name = "wheezy"
    wheezy_config.vm.network :private_network, ip: "192.168.20.52"
  end

  config.vm.define :trusty do |trusty_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    trusty_config.vm.box = "trusty"
    trusty_config.vm.box_url = "https://vagrantcloud.com/chef/ubuntu-14.04/version/1.0.0/provider/virtualbox.box"
    trusty_config.vm.host_name = "trusty"
    trusty_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "256", "--ioapic", "on" ]
    end
    trusty_config.vm.network :private_network, ip: "192.168.20.53"
  end

  config.vm.define :utopic do |utopic_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    utopic_config.vm.box = "utopic"
    utopic_config.vm.box_url = "https://vagrantcloud.com/chef/ubuntu-14.10/version/1.0.0/provider/virtualbox.box"
    utopic_config.vm.host_name = "utopic"
    utopic_config.vm.network :private_network, ip: "192.168.20.54"
  end

  config.vm.define :precise do |precise_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    precise_config.vm.box = "precise"
    precise_config.vm.box_url = "https://vagrantcloud.com/chef/ubuntu-12.04/version/1.0.0/provider/virtualbox.box"
    precise_config.vm.host_name = "precise"
    precise_config.vm.network :private_network, ip: "192.168.20.55"
  end

  config.vm.define :lucid do |lucid_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    lucid_config.vm.box = "lucid"
    lucid_config.vm.box_url = "https://vagrantcloud.com/chef/ubuntu-10.04/version/1.0.0/provider/virtualbox.box"
    lucid_config.vm.host_name = "lucid"
    lucid_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "2048", "--ioapic", "on" ]
    end
    lucid_config.vm.network :private_network, ip: "192.168.20.56"
  end

  config.vm.define :centos6 do |centos6_config|
    centos6_config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_centos-6.5_chef-provisionerless.box"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos6_config.vm.box = "centos6"
    centos6_config.vm.host_name = "centos6"
    centos6_config.vm.network :private_network, ip: "192.168.20.57"
  end

  config.vm.define :centos5 do |centos5_config|
    centos5_config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_centos-5.10_chef-provisionerless.box"
    centos5_config.vm.box = "centos5"
    config.vm.provision "shell", path: "centos5.sh"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos5_config.vm.host_name = "centos5"
    centos5_config.vm.network :private_network, ip: "192.168.20.58"
  end

  config.vm.define :centos7 do |centos7_config|
    centos7_config.vm.box_url = "http://opscode-vm-bento.s3.amazonaws.com/vagrant/virtualbox/opscode_centos-7.0_chef-provisionerless.box"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = "playbooks/common.yml"
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos7_config.vm.box = "centos7"
    centos7_config.vm.host_name = "centos7"
    centos7_config.vm.network :private_network, ip: "192.168.20.59"
  end

  config.vm.define :pxc1 do |pxc1_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = deb1_playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    pxc1_config.vm.box = deb_distro
    pxc1_config.vm.host_name = "pxc1"
    pxc1_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024", "--ioapic", "on" ]
    end
    pxc1_config.vm.network :private_network, ip: "192.168.70.61"
  end

  config.vm.define :pxc2 do |pxc2_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = deb_common_playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    pxc2_config.vm.box = deb_distro
    pxc2_config.vm.host_name = "pxc2"
    pxc2_config.vm.network :private_network, ip: "192.168.70.62"
  end

  config.vm.define :pxc3 do |pxc3_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = deb_common_playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    pxc3_config.vm.box = deb_distro
    pxc3_config.vm.host_name = "pxc3"
    pxc3_config.vm.network :private_network, ip: "192.168.70.63"
  end

   config.vm.define :percona1 do |percona1_config|
        if rhel_distro == "centos5" then
          config.vm.provision "shell", path: "centos5.sh"
        end   
        config.vm.provision "ansible" do |ansible|
          ansible.playbook = rhel1_playbook
          ansible.sudo = "true"
          ansible.host_key_checking = "false"
        end
        percona1_config.vm.box = rhel_distro
        percona1_config.vm.host_name = "percona1"
        percona1_config.vm.network :private_network, ip: "192.168.70.71"
  end
  config.vm.define :percona2 do |percona2_config|
        if rhel_distro == "centos5" then
          config.vm.provision "shell", path: "centos5.sh"
        end   
        config.vm.provision "ansible" do |ansible|
          ansible.playbook = rhel_playbook
          ansible.sudo = "true"
          ansible.host_key_checking = "false"
        end
        percona2_config.vm.box = rhel_distro
        percona2_config.vm.host_name = "percona2"
        percona2_config.vm.network :private_network, ip: "192.168.70.72"
  end
  config.vm.define :percona3 do |percona3_config|
        if rhel_distro == "centos5" then
          config.vm.provision "shell", path: "centos5.sh"
        end   
         config.vm.provision "ansible" do |ansible|
          ansible.playbook = rhel1_playbook
          ansible.sudo = "true"
          ansible.host_key_checking = "false"
        end
        percona3_config.vm.box = rhel_distro
        percona3_config.vm.host_name = "percona3"
        percona3_config.vm.network :private_network, ip: "192.168.70.73"
  end

end


