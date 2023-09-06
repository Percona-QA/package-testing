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
staticUDFs=("SELECT mask_canada_sin('046454286A');" "SELECT mask_canada_sin('046454286A', '#');" \
         "SELECT mask_iban('LC14BOSL12345678901234567890123422');" "SELECT mask_iban('LC14BOSL12345678901234567890123422', '#');" \
         "SELECT mask_inner('This is a string', 4, 1);" "SELECT mask_inner('This is a string', 1, 4);" \
         "SELECT mask_inner('This is a string', 4, 1, '#');" "SELECT mask_outer('This is a string', 11, 1);" \
         "SELECT mask_outer('This is a string', 1, 12);" "SELECT mask_outer('This is a string', 11, 1, '#');" \
         "SELECT mask_pan('01234567891234');" "SELECT mask_pan('01234567891234', '#');" \
         "SELECT mask_pan_relaxed('01234567891234');" "SELECT mask_pan_relaxed('01234567891234', '#');" \
         "SELECT mask_ssn('909-63-6922');" "SELECT mask_ssn('909-63-6922', '#');" \
         "SELECT mask_uk_nin('QQ123456C');" "SELECT mask_uk_nin('QQ123456C', '#');" \
         "SELECT mask_uuid('79546566-9997-0850-0038-757090134161');" "SELECT mask_uuid('79546566-9997-0850-0038-757090134161', '#');" \
         "SELECT masking_dictionary_term_add('test_dict1','test_term1_1');" "SELECT masking_dictionary_term_add('test_dict1','test_term1_2');" \
         "SELECT masking_dictionary_term_add('test_dict2','test_term2_1');" "SELECT masking_dictionary_term_add('test_dict2','test_term2_2');" \
         "SELECT masking_dictionary_term_remove('test_dict2','test_term2_2');" "SELECT gen_blocklist('test_term1_1', 'test_dict1', 'test_dict2');" \
         "SELECT gen_dictionary('test_dict2');" "SELECT masking_dictionary_remove('test_dict1');")
referenceList=("XXXXXXXXXX" "##########" \
         "LC********************************" "LC################################" \
         "ThisXXXXXXXXXXXg" "TXXXXXXXXXXXring" \
         "This###########g" "XXXXXXXXXXXtrinX" \
         "XhisXXXXXXXXXXXX" "###########trin#" \
         "XXXXXXXXXX1234" "##########1234" \
         "012345XXXX1234" "012345####1234" \
         "***-**-6922" "###-##-6922" \
         "QQ*******" "QQ#######" \
         "********-****-****-****-************" "########-####-####-####-############" \
         "1" "1" \
         "1" "1" \
         "1" "test_term2_1" \
         "test_term2_1" "1" )
# randomUDFs=("SELECT gen_range(1, 10);" "SELECT gen_rnd_canada_sin();" \
#          "SELECT gen_rnd_email();" "SELECT gen_rnd_email(3,4,'mydomain.com');" \
#          "SELECT gen_rnd_iban();" "SELECT gen_rnd_iban('UA',20);" \
#          "SELECT gen_rnd_pan();" "SELECT gen_rnd_ssn();" \
#          "SELECT gen_rnd_uk_nin();" "SELECT gen_rnd_us_phone();" \
#          "SELECT gen_rnd_uuid();")
for i in ${!staticUDFs[@]}; do 
    result=$(mysql -uroot -S/tmp/mysql_24000.sock -NBe "${staticUDFs[$i]}")
    if [ "${result}" == "${referenceList[$i]}" ]; then
        echo 'Equal'
    else
        echo "${staticUDFs[$i]} result is incorrect. Current result is: ${result}. Expected result is: ${referenceList[$i]}"
        fails='1'
    fi
done
# for i in ${randomUDFs[@]}; do

#     result=$(mysql -uroot -S/tmp/mysql_24000.sock -NBe "${i}")
#     if [[ -z "${result}" ]]; then
#         fails='2'
#         echo "There is and error"
#     fi
#     echo ${i} has result ${result}
# done
# Disable Data Masking plugin
mysql -uroot -S/tmp/mysql_24000.sock -NBe "UNINSTALL PLUGIN data_masking';

if [[ "${fails}" == '1' ]]; then
    echo "Exiting because there were failed UDFs!"
    exit 1
fi

