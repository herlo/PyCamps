#  Installing PyCamps #

### Pre-Install Configuration ###

NOTE: Configurations for anything but Apache Web Server and MySQL Database Server are not implemented yet.  If you decide to use a different configuration, please consider contributing to PyCamps.

Before beginning, PyCamps will need the following items configured, DO NOT INSTALL A WEB SERVER OR DATABASE UNTIL THESE ITEMS ARE PREPARED: 
- A disk partition with LVM for the master databases and clones
- Determine the current database size then multiply by 1.5, then multiply by the number of camps
    - For example, if the DB size is 3G, 3Gx1.5 # 4.5G per camp. 4.5Gx10 camps # 45G minimum partition
    - NOTE: Keep growth in mind as databases almost always grow
- Make a volume group named 'db' from the above partition
- Make a logical volume named 'campmaster' 
    - NOTE: the VG and LV name can change, but will require other config changes
- Make a filesystem (recommended ext3 or ext4) on the /dev/db/campmaster LV

Manage each LV using autofs.  PyCamps will automatically clone LVs as camps are created using read-write LVM snapshots.

On a RHEL/Fedora based system, as root, run the following commands:
- Install autofs
    - 'yum install autofs'
- Copy the auto.master and auto.db from the conf/ to /etc/ directory
    - 'cp /path/to/PyCamps/conf/auto.master /path/to/PyCamps/conf/auto.db /etc'
- Start autofs
    - 'service autofs start'

NOTE: Any changes made previously could affect the autofs configuration, please adjust accordingly.

### Recommendations ###
- /home should live on its own partition, but if it doesn't or can't, make sure to allocate enough disk for the camps' docroot
    - For example, if the current docroot is 10G, 10Gx1.5 # 11.5G per camp. 11.5Gx10 camps # 115G 
- Having /home on LVM makes it easy to snapshot, grow or shrink as needed

## Install ##

Get the latest tarball from github (no tarball currently available, use source code for now)

-or-

Grab the source code using git

  $ git clone git@github.com:herlo/PyCamps.git /path/to/PyCamps  
  .. snip ..  
  $ cd /path/to/PyCamps  
  $ python setup.py install #NOTE: this does not work yet  FIXME  

Source install is complete.  

NOTE: MAKE SURE TO BACKUP YOUR OLD CONFIGURATION FILES BEFORE THE NEXT STEPS
