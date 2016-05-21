yum install -y python-simplejson.x86_64 vim-enhanced 
wget http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
rpm -ivH percona-release-0.1-3.noarch.rpm
wget anorien.csc.warwick.ac.uk/mirrors/epel/5/x86_64/epel-release-5-4.noarch.rpm
rpm -ivH epel-release-5-4.noarch.rpm
yum install -y Percona-Server-shared-compat.x86_64 python-ssl
