#!/usr/bin/env bash

set -e

if [ "$#" -ne 1 ]; then
  echo "This script requires product parameter: ps56, ps57 or ps80 !"
  echo "Usage: ./comp_test.sh <prod>"
  exit 1
elif [ $1 != "ps56" -a $1 != "ps57" -a $1 != "ps80" -a $1 != "ps81" ]; then
  echo "Product not recognized!"
  exit 1
fi

SCRIPT_PWD=$(cd `dirname $0` && pwd)

if [ -f /etc/mysql/my.cnf ]; then
  MYCNF="/etc/mysql/my.cnf"
else
  MYCNF="/etc/my.cnf"
fi

# if the server supports RocksDB options for column families need to be specified before running mysql
if [ $1 != "ps56" ]; then
  systemctl stop mysql
  sleep 10
  echo -e "\n[mysqld]" >> ${MYCNF}
#  echo "rocksdb_default_cf_options=compression_per_level=kNoCompression" >> ${MYCNF}
  echo "rocksdb_override_cf_options=cf1={compression=kZlibCompression;bottommost_compression=kZlibCompression};cf2={compression=kLZ4Compression;bottommost_compression=kLZ4Compression};cf3={compression=kZSTDNotFinalCompression;bottommost_compression=kZSTDNotFinalCompression};cf4={compression=kNoCompression;bottommost_compression=kNoCompression}" >> ${MYCNF}
  systemctl start mysql
  sleep 10
fi

tokudb_comp_lib=("no" "default" "zlib" "quicklz" "lzma" "snappy" "dummy")
rocksdb_comp_lib=("no" "default" "zlib" "lz4" "zstd" "dummy")
old="no"
new="no"

mysql -e "DROP DATABASE IF EXISTS comp_test;"
mysql -e "CREATE DATABASE comp_test;"
mysql -e "SET GLOBAL sql_mode = 'TRADITIONAL';"
# needed because of issue in REPEATABLE READ
# ERROR 1105 (HY000) at line 1: Using Gap Lock without full unique key in multi-table or multi-statement transactions is not allowed.
mysql -e "SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED;"

secure_file_priv=$(mysql -N -s -e "select @@secure_file_priv;")
if [ -z ${secure_file_priv} ]; then
  secure_file_priv="/tmp/"
fi
rm -f ${secure_file_priv}/t1*.txt
rm -f ${secure_file_priv}/t2*.txt
rm -f ${secure_file_priv}/t3*.txt

for se in TokuDB RocksDB; do
  for comp_lib in no default zlib lz4 zstd quicklz lzma snappy dummy; do

    if [[ ${se} = "TokuDB" && " ${tokudb_comp_lib[@]} " =~ " ${comp_lib} " ]] || [[ ${se} = "RocksDB" && " ${rocksdb_comp_lib[@]} " =~ " ${comp_lib} " ]]; then
      if [ $1 = "ps56" -a ${se} = "RocksDB" ]; then
        echo "Skipping RocksDB since not supported in PS 5.6"
      elif [ $1 = "ps80" -o $1 = "ps81" -a ${se} = "TokuDB" ]; then
        echo "Skipping TokuDB since not supported in PS 8.0 and PS 8.1"
      else
        if [ ${comp_lib} != "dummy" ]; then
          old="${new}"
          new="${comp_lib}"
          cat ${SCRIPT_PWD}/create_table.sql > /tmp/create_table.sql
          sed -i "s/@@SE_COMP@@/${se}_${comp_lib}/g" /tmp/create_table.sql
          sed -i "s/@@SE@@/${se}/g" /tmp/create_table.sql
          if [ ${se} = "TokuDB" ]; then
            sed -i "s/ @@COMMENT@@//g" /tmp/create_table.sql
            sed -i "s/ @@COMMENT_PARTITIONED@@//g" /tmp/create_table.sql
            old_row_format="${new_row_format}"
            if [ ${comp_lib} = "no" ]; then
              new_row_format="tokudb_uncompressed"
            elif [ ${comp_lib} = "default" ]; then
              new_row_format="tokudb_quicklz"
            elif [ ${comp_lib} = "zlib" ]; then
              new_row_format="tokudb_zlib"
            elif [ ${comp_lib} = "quicklz" ]; then
              new_row_format="tokudb_quicklz"
            elif [ ${comp_lib} = "lzma" ]; then
              new_row_format="tokudb_lzma"
            elif [ ${comp_lib} = "snappy" ]; then
              new_row_format="tokudb_snappy"
            fi
          fi
          if [ ${se} = "RocksDB" ]; then
            old_cf="${new_cf}"
            if [ ${comp_lib} = "no" ]; then
              new_cf="cf4"
            elif [ ${comp_lib} = "default" ]; then
              new_cf=""
            elif [ ${comp_lib} = "zlib" ]; then
              new_cf="cf1"
            elif [ ${comp_lib} = "lz4" ]; then
              new_cf="cf2"
            elif [ ${comp_lib} = "zstd" ]; then
              new_cf="cf3"
            fi
            if [ "${new_cf}" = "" ]; then
              new_comment=""
              new_comment_partitioned=""
            else
              new_comment="COMMENT 'cfname=${new_cf}'"
              new_comment_partitioned="COMMENT 'p0_cfname=${new_cf};p1_cfname=${new_cf};p2_cfname=${new_cf};p3_cfname=${new_cf}'"
            fi
            sed -i "s/ @@COMMENT_PARTITIONED@@/ ${new_comment_partitioned}/g" /tmp/create_table.sql
            sed -i "s/ @@COMMENT@@/ ${new_comment}/g" /tmp/create_table.sql
          fi
          if [ $1 != "ps80" -o $1 != "ps81"]; then
            mysql -e "set global tokudb_row_format=${new_row_format};"
          else
	    echo "Skipping TokuDB since not supported in PS 8.0 and PS 8.1"
	  fi  
	  mysql < /tmp/create_table.sql
        fi

        if [ ${comp_lib} = "no" ]; then
          # insert fresh data into uncompressed tables
          cat ${SCRIPT_PWD}/test_data.sql > /tmp/test_data.sql
          sed -i "s/@@SE@@/${se}/g" /tmp/test_data.sql
          mysql < /tmp/test_data.sql
          for table in t1 t2 t3; do
            mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_${new};" >> /tmp/optimize_table.txt
            mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_${new} INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}.txt';"
          done
        elif [ ${comp_lib} = "dummy" ]; then
          for table in t1 t2 t3; do
            mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no ENGINE=InnoDB ROW_FORMAT=COMPRESSED;"
            mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_no;" >> /tmp/optimize_table.txt
            mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_no INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}_alter_innodb.txt';"
            if [ ${se} = "TokuDB" ]; then
              mysql -e "set global tokudb_row_format=${new_row_format};"
              mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no ENGINE=${se};"
            else
              mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no ENGINE=${se};"
            fi
            mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_no;" >> /tmp/optimize_table.txt
            mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_no INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}_alter_back_${se}.txt';"
          done
        else
          for table in t1 t2 t3; do
            mysql -Dcomp_test -e "INSERT INTO ${table}_${se}_${new} SELECT * FROM ${table}_${se}_${old};"
            mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_${new};" >> /tmp/optimize_table.txt
            mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_${new} INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}.txt';"
            if [ ${se} = "TokuDB" ]; then
              mysql -e "set global tokudb_row_format=${new_row_format};"
              mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no ENGINE=TokuDB;"
              mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_no;" >> /tmp/optimize_table.txt
              mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_no INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}_alter.txt';"
            else
              mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no DROP PRIMARY KEY;"
              if [ ${table} = "t1" ]; then
                alter_comment="${new_comment_partitioned}"
              else
                alter_comment="${new_comment}"
              fi
              mysql -Dcomp_test -e "ALTER TABLE ${table}_${se}_no ADD PRIMARY KEY(a1) ${alter_comment};"
              mysql -Dcomp_test -e "OPTIMIZE TABLE ${table}_${se}_no;" >> /tmp/optimize_table.txt
              mysql -Dcomp_test -e "SELECT * FROM ${table}_${se}_no INTO OUTFILE '${secure_file_priv}/${table}_${se}_${new}_alter.txt';"
            fi
          done
        fi

      fi # end for comp_lib
    fi # end for se
  done
done

mysql -e "SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;"

# check if SST files contain proper compression libraries used
for file in /var/lib/mysql/.rocksdb/*.sst; do
  sst_cf=$(sst_dump --show_properties --file=${file} | grep "column family name:" | sed 's/  column family name: //')
  sst_clib=$(sst_dump --show_properties --file=${file} | grep "SST file compression algo:" | sed 's/  SST file compression algo: //')
  if [[ "${sst_cf}" = "__system__" && "${sst_clib}" != "LZ4" ]] || [[ "${sst_cf}" = "default" && "${sst_clib}" != "LZ4" ]] || [[ "${sst_cf}" = "cf1" && "${sst_clib}" != "Zlib" ]] || [[ "${sst_cf}" = "cf2" && "${sst_clib}" != "LZ4" ]] || [[ "${sst_cf}" = "cf3" && "${sst_clib}" != "ZSTDNotFinal" ]] || [[ "${sst_cf}" = "cf4" && "${sst_clib}" != "NoCompression" ]]; then
    echo "SST file ${file} has column family ${sst_cf} and compression library ${sst_clib} which seems incorrect!"
    exit 1
  fi
done

# check if TokuDB files contain proper compression libraries used
if [ $1 != "ps80" -o $1 != "ps81"]; then
  for file in /var/lib/mysql/comp_test/*TokuDB*_main_*.tokudb;
  do
    filename_comp=$(echo "${file}" | sed "s:/.*/::" | sed "s:.*TokuDB_::" | sed "s:_main_.*::" | sed "s:_P_.*::")
    file_comp=$(tokuftdump --header ${file}|grep "compression_method"|sed 's/ compression_method=//';)
    if [ ${filename_comp} != "no"  ]; then
      if [[ "${filename_comp}" = "quicklz" && "${file_comp}" -ne "9" ]] || [[ "${filename_comp}" = "zlib" && "${file_comp}" -ne "11" ]] || [[ "${filename_comp}" = "lzma" && "${file_comp}" -ne "10" ]] || [[ "${filename_comp}" = "snappy" && "${file_comp}" -ne "7" ]] || [[ "${filename_comp}" = "default" && "${file_comp}" -ne "9" ]]; then
        echo "TokuDB file ${file} has compression algorithm ${file_comp} and it should be ${filename_comp} which seems incorrect!"
        exit 1
      fi
    fi
  done
else 
  echo "Tokudb is deprecated in PS8.0 and PS 8.1"
fi  

md5sum ${secure_file_priv}/*.txt > /tmp/comp_test_md5.sum

#remove the rocksdb options so the server is able to start once the SE is removed
sed -i '/^rocksdb/d' ${MYCNF}

nr1=$(grep -c "e7821682046d961fb2b5ff5d11894491" /tmp/comp_test_md5.sum)
nr2=$(grep -c "3284a0c3a1f439892f6e07f75408b2c2" /tmp/comp_test_md5.sum)
nr3=$(grep -c "72f7e51a16c2f0af31e39586b571b902" /tmp/comp_test_md5.sum)
if [ $1 != "ps80" -a $1 != "ps81" ]; then
  if [ ${nr1} -ne 24 -o ${nr2} -ne 24 -o ${nr3} -ne 24 ]; then
    echo "md5sums of test files do not match. check files in ${secure_file_priv}"
    exit 1
  else
    echo "md5sums of test files match"
    exit 0
  fi
elif [ ${nr1} -ne 11 -o ${nr2} -ne 11 -o ${nr3} -ne 11 ]; then 
  echo "md5sums of test files do not match. check files in ${secure_file_priv}"
  exit 1
else
  echo "md5sums of test files match"
  exit 0	
fi
