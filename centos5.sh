yum install -y python-simplejson.x86_64 vim-enhanced
wget anorien.csc.warwick.ac.uk/mirrors/epel/5/x86_64/epel-release-5-4.noarch.rpm
rpm -ivH epel-release-5-4.noarch.rpm
rpm -ivH /vagrant/percona-release-0.1-3.noarch.rpm
yum install -y Percona-Server-shared-compat.x86_64 
