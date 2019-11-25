ps-innodb-cluster-server
========================

This role creates 3 PS server instances and configures them for group replication.
Dependant role "ps-innodb-cluster-router" is used to install mysql router and shell
on separate instance and then setup and verify InnoDB cluster.

Requirements
------------

pip modules: molecule ansible python-vagrant testinfra pytest wheel
ps-innodb-cluster-router role

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


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: ps-innodb-cluster-server, x: 42 }

License
-------

GPLv3

Author Information
------------------

