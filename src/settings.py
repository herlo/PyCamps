# PyCamps configurations loader

import os

# the root location of all camps

CAMPS_ROOT = os.environ['HOME']

# the dir where the camp will be stored within the 
# user's home directory camp will be turned into 
# /home/user/camp4 for the 4th camp.

CAMPS_BASENAME = 'camp'

# the path to the PyCamps sqlite db.  Used for tracking pertinent info like camp#, description, etc.
CAMPS_DB = '/home/clints/Projects/PyCamps/camps.db'

# the path to the git repo to clone, must have an ending /

GIT_ROOT = '/home/clints/Projects/GitPyCamps/'

# CHOOSE DB TYPE / Only MySQL is available atm

DB = 'MySQL'

# DB INFO
DB_USER = 'test'
DB_PASS = 'test'
DB_HOST = 'x201.egavas.org'
DB_BASE_PORT = 3300

# this is a python heredoc to generate the
# mysql config entries for each db
DB_CONFIG = """[mysqld%(camp_id)d]
datadir = /var/lib/mysql/camp%(camp_id)d
socket = /var/lib/mysql/camp%(camp_id)d/mysql.sock
pid-file = /var/run/mysqld/camp%(camp_id)d.pid
user = mysql
port = %(port)d
log = /var/log/mysqld-%(camp_id)d.log"""

# the port can be set, but if left blank, will default to auto-incrementing.
# The PyCamps config for MySQL uses individual ports to manage multiple db instances
DB_PORT = None
# location within where db master and clones will live
DB_ROOT = '/var/lib/mysql'

# How do we clone the dbs?
DB_CLONE_METHOD='LVM-SNAP'  # alternate method could be DB_CLONE_METHOD=RSYNC

# if using LVM-SNAP method, these configs are needed
CAMPS_VG='db'
CAMPS_LV='campsmaster'

# if using RSYNC method, these configs are needed


