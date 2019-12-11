#!/usr/bin/env bash
rm -f get_download_link.sh && wget -q https://raw.githubusercontent.com/Percona-QA/percona-qa/master/get_download_link.sh && chmod +x get_download_link.sh
rm -f vault_test_setup.sh && wget -q https://raw.githubusercontent.com/Percona-QA/percona-qa/master/vault_test_setup.sh && chmod +x vault_test_setup.sh
./vault_test_setup.sh --use-ssl --workdir=${PWD}/vault-server
grep VAULT_ADDR ${PWD}/vault-server/set_env.sh|cut -d'=' -f2 > ${PWD}/vault-server/VAULT_URL
grep VAULT_TOKEN ${PWD}/vault-server/set_env.sh|cut -d'=' -f2 > ${PWD}/vault-server/VAULT_TOKEN
echo "${PWD}/vault-server/certificates/root.cer" > ${PWD}/vault-server/VAULT_CERT
