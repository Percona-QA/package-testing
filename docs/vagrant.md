<h1>changing existing vagrant box</h1>
```
vagrant init <base box>
vagrant up
vagrant ssh 
sudo apt-get update
sudo apt-get upgrade
sudo apt-get clean
sudo dd if=/dev/zero of=/EMPTY bs=1M
sudo rm -f /EMPTY
cat /dev/null > ~/.bash_history && history -c && exit
vagrant halt
vagrant package --output mynew.box
vagrant box add mynewbox mynew.box
vagrant destroy
rm Vagrantfile
```
