# PyCamps configurations loader

import os

# the root location of all camps

CAMPS_ROOT = os.environ['HOME']

# the dir where the camp will be stored within the 
# user's home directory camp will be turned into 
# /home/user/camp4 for the 4th camp.

CAMPS_BASENAME = 'camp'

# the path to the PyCamps sqlite db.  Used for tracking pertinent info like camp#, description, etc.
CAMPS_DB = '/home/clints/Projects/PyCamps/pycamps.db'

# the path to the git repo to clone, must have an ending /

GIT_ROOT = '/home/clints/Projects/GitPyCamps/'

# MYSQL INFO

DB_USER = 'test'
DB_PASS = 'test'
DB_HOST = 'localhost'
BASE_DB_PORT = 3300
# the port can be set, but if left blank, will default to auto-incrementing.
# The PyCamps config for MySQL uses individual ports to manage multiple db instances
DB_PORT = None


