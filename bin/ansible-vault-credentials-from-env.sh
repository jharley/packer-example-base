#!/bin/bash
# This is to allow an Ansible Vault's credentials to be stored in an environment variable making
# use of ansible-playbook's "--vault-password-file" option or "ANSIBLE_VAULT_PASSWORD_FILE"
# environment variable.
#
# e.g. ANSIBLE_VAULT_PASSWORD_FILE=ansible-vault-credentials-from-env.sh ansible-playbook myplay.yml

echo $ANSIBLE_VAULT_PASSWORD
