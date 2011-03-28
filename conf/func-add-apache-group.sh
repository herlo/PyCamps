#!/bin/bash

setfacl -d -R -m 'g:apache:rX' /etc/pki/certmaster/
setfacl -R -m 'g:apache:rX' /etc/pki/certmaster/
setfacl -d -R -m 'g:apache:rX' /var/lib/certmaster
setfacl -R -m 'g:apache:rX' /var/lib/certmaster
setfacl -d -R -m 'g:apache:rX' /var/lib/certmaster/certmaster
setfacl -R -m 'g:apache:rX' /var/lib/certmaster/certmaster
setfacl -d -R -m 'g:apache:rX' /var/lib/certmaster/certmaster/certs
setfacl -R -m 'g:apache:rX' /var/lib/certmaster/certmaster/certs
setfacl -d -R -m 'g:apache:rX' /var/lib/certmaster/peers
setfacl -R -m 'g:apache:rX' /var/lib/certmaster/peers
setfacl -d -R -m 'g:apache:rwX' /var/lib/func
setfacl -R -m 'g:apache:rwX' /var/lib/func
setfacl -d -R -m 'g:apache:rwX' /var/log/func/
setfacl -R -m 'g:apache:rwX' /var/log/func/
