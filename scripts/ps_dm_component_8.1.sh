#!/bin/bash

#install the data masking component
mysql -NBe "INSTALL COMPONENT 'file://component_masking_functions';"
install_result=$?
if [[ "${install_result}" == '1' ]]; then
    echo "Exiting because there was failure during component install!"
    exit 1
fi

# make sure DM component is in place
DM_COMPONENT=$(mysql -NBe "select * from mysql.component;" | grep -c component_masking_functions)

if [ ${DM_COMPONENT} == 1 ]; then
   echo "DM component is installed"
else
   echo "ERROR: DM component isn't installed"
   exit 1
fi

# create data masking dictionary table and give permissions to user
mysql -NBe "CREATE TABLE IF NOT EXISTS mysql.masking_dictionaries (Dictionary VARCHAR(256) NOT NULL,\
      Term VARCHAR(256) NOT NULL, UNIQUE INDEX dictionary_term_idx (Dictionary, Term), INDEX dictionary_idx (Dictionary))\
      ENGINE = InnoDB DEFAULT CHARSET=utf8mb4;"
mysql -NBe "GRANT MASKING_DICTIONARIES_ADMIN on *.* to 'root'@'localhost';"



#Create lists of static UDFs (we know expected result), reference list for static UDFs and list for random UDFs
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
randomUDFs=("SELECT gen_range(1, 10);" "SELECT gen_rnd_canada_sin();" \
         "SELECT gen_rnd_email();" "SELECT gen_rnd_email(3,4,'mydomain.com');" \
         "SELECT gen_rnd_iban();" "SELECT gen_rnd_iban('UA',20);" \
         "SELECT gen_rnd_pan();" "SELECT gen_rnd_ssn();" \
         "SELECT gen_rnd_uk_nin();" "SELECT gen_rnd_us_phone();" \
         "SELECT gen_rnd_uuid();")

#Check static UDFs results (we know expected result in advance) by comparing UDF result to reference value
for i in ${!staticUDFs[@]}; do 
    result=$(mysql -NBe "${staticUDFs[$i]}")
    if [[ "${result}" != "${referenceList[$i]}" ]]; then
        echo "${staticUDFs[$i]} result is incorrect. Current result is: ${result}. Expected result is: ${referenceList[$i]}"
        fails='1'
    fi
done

#Check UDFs that generate random result. MySQL ERRORs have empty result.
for i in "${randomUDFs[@]}"; do
    result=$(mysql -NBe "${i}")
    if [[ -z "${result}" ]]; then
        fails='1'
        echo "${i} has empty result."
    fi
done

# set -e
# Disable Data Masking component
mysql -NBe "DROP TABLE IF EXISTS mysql.masking_dictionaries;"
mysql -NBe "UNINSTALL COMPONENT 'file://component_masking_functions';"
uninstall_result=$?

#Exit script with an error if any of the checks failed.
if [[ "${fails}" == '1' ]]; then
    echo "Exiting because there were failed UDFs!"
    exit 1
elif [[ "${uninstall_result}" == '1' ]]; then
    echo "Exiting because there was failure during component uninstall!"
    exit 1
fi

