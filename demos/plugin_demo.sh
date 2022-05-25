#!/bin/bash

########################
# include the magic
########################
. demo-magic.sh

# hide the evidence
clear

# Put your stuff here

pe "koji download-build gnupg-1.4.5-18.el5_10.1"
pe "ls *.rpm"
pe "koji list-signed --build gnupg-1.4.5-18.el5_10.1"
pe "rpmsign --addsign --rpmv3 gnupg-1.4.5-18.el5_10.1.ia64.rpm"
pe "rpm -Kv gnupg-1.4.5-18.el5_10.1.ia64.rpm"
pe "koji import-sig gnupg-1.4.5-18.el5_10.1.ia64.rpm"
pe "cat /mnt/koji/rekor_logs/gnupg/1.4.5/18.el5_10.1/ia64/gnupg-1.4.5-18.el5_10.1.ia64.json"
pe "rekor-cli search --artifact gnupg-1.4.5-18.el5_10.1.ia64.rpm"

cmd
 
