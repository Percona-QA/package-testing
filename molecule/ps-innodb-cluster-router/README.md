ps-innodb-cluster-router
========================

This role installs mysql shell and router into vagrant instance and then does
setup and verification of InnoDB cluster.
It depends on ps-innodb-cluster-server which creates PS instances for the cluster.

Requirements
------------

python modules: molecule ansible python-vagrant testinfra pytest wheel
PS cluster setup with role ps-innodb-cluster-server.

Role Variables
--------------

export TEST_DIST="bento/ubuntu-18.04"
export INSTALL_REPO="testing"
export PS_NODE1_IP="192.168.33.50"
export PS_NODE2_IP="192.168.33.51"
export PS_NODE3_IP="192.168.33.52"
export MYSQL_ROUTER_IP="192.168.33.53"
export UPSTREAM_VERSION="8.0.17"
export PS_VERSION="8"
export PS_REVISION="868a4ef"

Dependencies
------------

ps-innodb-cluster-server role

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: ps-innodb-cluster-router, x: 42 }

License
-------

GPLv3

Author Information
------------------

