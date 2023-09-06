#!/bin/bash

#check that data masking plugin is disabled
DM_PLUGIN=$(mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT PLUGIN_NAME, PLUGIN_STATUS FROM INFORMATION_SCHEMA.PLUGINS WHERE PLUGIN_NAME = 'data_masking';" | grep -c ACTIVE)

if [ ${DM_PLUGIN} == 1 ]; then
   echo "DM plugin is installed and active"
   exit 1
else
   echo "ERROR: DM plugin isn't installed or active"
fi

set -e

#install the data masking 
mysql -uroot -S/tmp/mysql_24000.sock -NBe "INSTALL COMPONENT 'file://component_masking';"

# make sure DM plugin is active
DM_COMPONENT=$(mysql -uroot -S/tmp/mysql_24000.sock -NBe "select * from mysql.component;" | grep -c component_masking_functions)

if [ ${DM_COMPONENT} == 1 ]; then
   echo "DM component is installed and active"
else
   echo "ERROR: DM component isn't installed or active"
   exit 1
fi

# create data masking dictionary table and give permissions to user
mysql -uroot -S/tmp/mysql_24000.sock -NBe "CREATE TABLE IF NOT EXISTS mysql.masking_dictionaries (Dictionary VARCHAR(256) NOT NULL,\
      Term VARCHAR(256) NOT NULL, UNIQUE INDEX dictionary_term_idx (Dictionary, Term), INDEX dictionary_idx (Dictionary))\
      ENGINE = InnoDB DEFAULT CHARSET=utf8mb4;"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "GRANT MASKING_DICTIONARIES_ADMIN on *.* to 'root'@'localhost';"



#use the Data Masking functions
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_canada_sin('046454286A');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_canada_sin('046454286A', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_iban('LC14BOSL12345678901234567890123422');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_iban('LC14BOSL12345678901234567890123422', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_inner('This is a string', 5, 1);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_inner('This is a string', 5, 1, '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_inner('This is a string', 1, 5);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_outer('This is a string', 5, 1);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_outer('This is a string', 5, 1, '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_outer('This is a string', 1, 5);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_inner('This is a string', 5, 1, '*');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_outer('This is a string', 5, 1, '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_pan('01234567891234');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_pan('01234567891234', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_pan_relaxed('01234567891234');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_pan_relaxed('01234567891234', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_ssn('909-63-6922');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_ssn('909-63-6922', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_uk_nin('QQ123456C');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_uk_nin('QQ123456C', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_uuid('79546566-9997-0850-0038-757090134161');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT mask_uuid('79546566-9997-0850-0038-757090134161', '#');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_range(1, 10);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_canada_sin();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_email();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_email(3,4,'mydomain.com');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_iban();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_iban('UA',20);"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_pan();" # in our implementation no params are accepted
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_ssn();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_uk_nin();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_us_phone();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_rnd_uuid();"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_term_add('test_dict1','test_term1_1');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_term_add('test_dict1','test_term1_2');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_term_add('test_dict2','test_term2_1');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_term_add('test_dict2','test_term2_2');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_term_remove('test_dict2','test_term2_2');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_blocklist('test_term1_1', 'test_dict1', 'test_dict2');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT gen_dictionary('test_dict1');"
mysql -uroot -S/tmp/mysql_24000.sock -NBe "SELECT masking_dictionary_remove('test_dict1');"


# Disable Data Masking plugin
mysql -uroot -S/tmp/mysql_24000.sock -NBe "UNINSTALL PLUGIN data_masking';

