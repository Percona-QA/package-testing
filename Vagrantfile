# -*- mode: ruby -*-
# vi: set ft=ruby :

playbook = "playbooks/common_56.yml"
deb_distro = "sgallen/wily64" 
deb1_playbook = "playbooks/pxc56.yml"
deb_common_playbook = "playbooks/pxc56_common.yml"
deb_garbd_playbook = "playbooks/pxc56_garbd.yml"
rhel_distro = "bento/centos-6.7"
rhel1_playbook = "playbooks/percona1.yml"
rhel_playbook = "playbooks/common_rpm.yml"

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most pxb configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  config.vm.define :wheezy do |wheezy_config|
    wheezy_config.vm.box = "bento/debian-7.9"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    wheezy_config.vm.host_name = "wheezy"
  end

  config.vm.define :jessie do |jessie_config|
    jessie_config.vm.box = "bento/debian-8.2"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    jessie_config.vm.host_name = "jessie"
    jessie_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024", "--ioapic", "on" ]
    end
  end

  config.vm.define :precise do |precise_config|
    precise_config.vm.box = "bento/ubuntu-12.04"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    precise_config.vm.host_name = "precise"
  end

  config.vm.define :trusty do |trusty_config|
    trusty_config.vm.box = "bento/ubuntu-14.04"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    trusty_config.vm.host_name = "trusty"
    trusty_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "256", "--ioapic", "on" ]
    end
  end

  config.vm.define :wily do |wily_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    wily_config.vm.box = "sgallen/wily64"
    wily_config.vm.host_name = "wily"
    wily_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024", "--ioapic", "on" ]
    end
  end

  config.vm.define :vivid do |vivid_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    vivid_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "1024", "--ioapic", "on" ]
    end
    vivid_config.vm.box = "bento/ubuntu-15.04"
    vivid_config.vm.host_name = "vivid"
  end

  config.vm.define :centos6 do |centos6_config|
    centos6_config.vm.box = "bento/centos-6.7"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos6_config.vm.host_name = "centos6"
  end

  config.vm.define :centos5 do |centos5_config|
    centos5_config.vm.box = "bento/centos-5.11"
    config.vm.provision "shell", path: "centos5.sh"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos5_config.vm.host_name = "centos5"
  end

  config.vm.define :centos7 do |centos7_config|
    centos7_config.vm.box = "bento/centos-7.2"
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    centos7_config.vm.host_name = "centos7"
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
      vb.customize ["modifyvm", :id, "--memory", "2048", "--ioapic", "on" ]
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
    pxc2_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "2048", "--ioapic", "on" ]
    end
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
    pxc3_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "2048", "--ioapic", "on" ]
    end
    pxc3_config.vm.network :private_network, ip: "192.168.70.63"
  end

  config.vm.define :pxc4 do |pxc4_config|
    config.vm.provision "ansible" do |ansible|
      ansible.playbook = deb_garbd_playbook
      ansible.sudo = "true"
      ansible.host_key_checking = "false"
    end
    pxc4_config.vm.box = deb_distro
    pxc4_config.vm.host_name = "pxc4"
    pxc4_config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "2048", "--ioapic", "on" ]
    end
    pxc4_config.vm.network :private_network, ip: "192.168.70.64"
  end

  config.vm.define :percona1 do |percona1_config|
       if rhel_distro == "bento/centos-5.11" then
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
        if rhel_distro == "bento/centos-5.11" then
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
        if rhel_distro == "bento/centos-5.11" then
          config.vm.provision "shell", path: "centos5.sh"
        end   
         config.vm.provision "ansible" do |ansible|
          ansible.playbook = rhel_playbook
          ansible.sudo = "true"
          ansible.host_key_checking = "false"
        end
        percona3_config.vm.box = rhel_distro
        percona3_config.vm.host_name = "percona3"
        percona3_config.vm.network :private_network, ip: "192.168.70.73"
  end

end


