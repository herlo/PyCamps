Installing PyCamps
==================
The installation of PyCamps is a bit arduous and time-consuming.  The hope is to automate some of the steps needed to setup and configure the PyCamps environment.  For now, this guide does a pretty good job of walking you through the initial setup and configuration required to make PyCamps work.  And luckily, the configurations only need to be done once.

.. warning:: Some of the concepts listed here require understanding of concepts elsewhere in this documentation. Please read the entire documention before beginning installation.

Get the Source Code
-------------------
Get the latest tarball from github::

    $ wget https://github.com/downloads/herlo/PyCamps/PyCamps-0.2.0.tar.gz
    $ tar xvf PyCamps-0.2.0.tar.gz -C /path/to/PyCamps

\- or -

Grab the source code using git::

    $ git clone git@github.com:herlo/PyCamps.git

PyCamps Install
---------------
::

    $ cd /path/to/PyCamps  
    $ python setup.py install
    .. snip ..

Source install is complete. 

Post-Install Configuration
-------------------------

.. note:: Configurations for anything but Apache Web Server (httpd) and MySQL Database Server (mysqld) are not implemented yet. If you decide to use a different configuration, please consider contributing to PyCamps.

.. warning:: **DO NOT INSTALL A WEB SERVER OR DATABASE UNTIL ALL OF THE ITEMS BELOW ARE COMPLETED.**

Before beginning, PyCamps will need the following items configured. For each project managed with PyCamps, a master database must be created as well as a central gitolite repository. 

Dependencies
------------

* Gitolite >= 1.5.3 (https://github.com/sitaramc/gitolite)
* Autofs >= 5.0.1 (http://www.autofs.org/)
* LVM2 (for database snapshots)
* Apache Web Server >= 2.2 (http://httpd.apache.org)
* MySQL Database Server >= 5.1.52 (http://mysql.com)
* git-python 0.2x (http://gitorious.org/projects/git-python/)
* sqlite 3.0 (http://www.sqlite.org/)
* python-sqlite2 2.3.3 (http://www.sqlite.org/)

Assumptions
-----------
First thing, this install guide can refer to outside material often. Please take the time to read and understand at least the basics of each application used in PyCamps. It is imperative to a successful installation.

As described in the :doc:`intro` document. PyCamps has both projects and camps. The goal of this installation guide is to setup and configure first, the Project(s) for which the camps will be using, and second, the environment in which the camps will reside. Simplicity is attempted at every turn, though sometimes, it is impossible. 

In this documentation, the Project will be called '**community**'. Its source code repository will reside at '**git\@git.example.com:community/master**'. The community project will have a Logical Volume (LV) defined as '**/dev/db/community**'. These conventions will be used throughout this document. 

Camps are named by ID and customarily called 'camp1', 'camp2', etc. Each camp corresponds to one and only one project, but also has its own source code repository. In this document, 'camp1' source code will reside in /home/clints/camps/camp1 and its corresponding source code repository will reside at 'git\@git.example.com:community/camp1'. If camp2 were created, its source code would reside in /home/clints/camps/camp1 and source code repository will reside at 'git\@git.example.com:community/camp2'. Hopefully, it's clear enough from these examples what camp3, camp4, etc. would look like.  The :doc:`tutorial </tutorial>` discusses more about how camps and projects relate.

Setting up the PyCamps Server(s)
--------------------------------
The PyCamps server can be set up to use either one or two machines. The key parts are the web and database components, determining which way to run PyCamps is very important as it cannot be changed once in place. The recommendation is to put everything on one beefy server making it easier to configure database connections for hosts. Notes will be made along the way where a dual server setup differs from a single server configuration.

Func-ify the Server(s)
^^^^^^^^^^^^^^^^^^^^^^
Func is used to help manage services that either are on another machine, like the database server, or elevate privileges for non-admin users in a controlled manner. PyCamps uses func heavily to create/remove/refresh the database LVM snapshots, start and stop the database and web servers and create configurations for the web and database servers.  There are likely other features func will enable in PyCamps in the future.

.. note:: If the database is on a separate server, func must be enabled on both machines. Luckily, the commands will be the same on both.

Installing func is simple and straightforward::

    # yum install func

\- or - ::

    # easy_install func

.. note:: On any other distribution of Unix/Linux, installation can be done 

To configure func further, please read `the func installation guide <https://fedorahosted.org/func/wiki/InstallAndSetupGuide>`_.

Once funcd and certmaster are setup, verify the configuration works by running the following as root::

    # func "x201.egavas.org" call command run "hostname"
    ('camps.example.com', [0, 'camps.example.com\n', ''])

A return value similar to the one above means func is configured properly.  

PyCamps requires one extra step to use func properly. Each user must be added to two central groups, apache (or www-dev) and a group to allow use of func. Once the group is determined, the func components will need to be altered to accommodate all system users.  In this example, the '*func*' group has been created for this purpose.

Once the group is created, func needs to be configured to allow that group to use its functionality::

    # setfacl -d -R -m 'g:func:rX' /etc/pki/certmaster/
    # setfacl -R -m 'g:func:rX' /etc/pki/certmaster/
    # setfacl -d -R -m 'g:func:rX' /var/lib/certmaster
    # setfacl -R -m 'g:func:rX' /var/lib/certmaster
    # setfacl -d -R -m 'g:func:rX' /var/lib/certmaster/certmaster
    # setfacl -R -m 'g:func:rX' /var/lib/certmaster/certmaster
    # setfacl -d -R -m 'g:func:rX' /var/lib/certmaster/certmaster/certs
    # setfacl -R -m 'g:func:rX' /var/lib/certmaster/certmaster/certs
    # setfacl -d -R -m 'g:func:rX' /var/lib/certmaster/peers
    # setfacl -R -m 'g:func:rX' /var/lib/certmaster/peers
    # setfacl -d -R -m 'g:func:rwX' /var/lib/func
    # setfacl -R -m 'g:func:rwX' /var/lib/func
    # setfacl -d -R -m 'g:func:rwX' /var/log/func/
    # setfacl -R -m 'g:func:rwX' /var/log/func/

A convenience script '*func-add-func-group.sh*' has been provided in the conf/ directory of the PyCamps package.

Database Requirements
^^^^^^^^^^^^^^^^^^^^^
PyCamps makes use of Logical Volume Manager (LVM2) for quick cloning of databases.  Each database will have a master database stored in a logical volume (LV).  A camp will create an LVM snapshot when it is being created or refreshed.  When an update occurs on the live database from code in a camp, the project's master database should be updated.  This could also happen on a nightly basis, if desired.  Determining the size of the master database is crucial, and while a new database can be recreated, a camp should have ample space to grow.

In most instances, it is also a good idea for the database dump script to scrub the data before using with PyCamps.  It is suggested to have the dump script do at least the following:

* Change the database passwords.
* Clean out any unneeded logs or superfluous data, such as product images, session data, etc.

Once the database has been dumped to a reasonable size, snapshots can be made.  Generally speaking, a snapshot can be much smaller than the original.  This is due to the fact that unless the master or camp database data changes, the LVM on which it sits, doesn't need to change.  Thus, making a camp database of 1/3 the size of the original is completely possible. 

.. note:: Snapshot sizes vary, some research can make the proper size much easier to determine.

* A disk partition with LVM for the master databases and clones
* Determine the master database size then divide by 1.75, then multiply by the number of camps

For example, if the master database size is 3G, 3G/1.75 = 2G per camp. 2Gx10 camps # 20G Logical Volume to start. This will likely need to be known when adding a project to PyCamps. 
      
.. note:: Keep growth in mind as databases almost always grow

Create the Master Database LV
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To create the Logical Volume, determine the size of the live database and add 25% for growth and flexibility. Manipulating Logical Volumes requires root rights. In the 'community' project, the database is currently 9G in size.  Therefore, a Logical Volume of at least 11.25G is needed.

Add that to the total size of camps, the Volume Group 'db' will be at least 31.25G in size.

.. note:: Since disk is cheap, rounding up to 50G would be a wise choice to either eke out a few more camps, or leave room to grow.

Assuming the /dev/sdb1 partition of 50G has been created with type LVM (8e), creating the LV is simple.  If desired, set the extent size larger than the standard 4M::

    # vgcreate db /dev/sdb1 [-s 128M]

From within the 'db' Volume Group, create the community Logical Volume::

    # lvcreate -L 12.5G -n community db

Verify the logical volume is reasonably close to the desired sizes::

    # vgs
    ..snip..
    # lvs
    ..snip..

Make a filesystem (recommended ext3 or ext4) on the /dev/db/community Logical Volume::

    # mkfs -t ext3 -L community_master_db /dev/db/community

Automounting Database Volumes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Another technology PyCamps takes advantage of is autofs.  Each camp database, including the master camp, is mounted using autofs.

To install and configure autofs, there are just a few steps to complete:

Install autofs::

    # yum install autofs (for RHEL/CentOS/Fedora)

\- or - ::

    # aptitude install autofs (for Ubuntu)

Copy the auto.master and auto.db from this project's conf/ to /etc/ directory.::

    # cp /path/to/PyCamps/conf/auto.master /path/to/PyCamps/conf/auto.db /etc'

.. note:: Any changes made previously could affect the autofs configuration, please adjust accordingly.

Start autofs and ensure autofs starts on boot.

Camp Requirements
^^^^^^^^^^^^^^^^^
Creating camps is likely the simplest component to configure.  Essentially, each camp will consist of configuration, logs, scripts and source code.  Depending on the size of the source code for each project, the size can range immensely.  

Camps usually live in /home, though this value is configurable.  Sharing of camps is not a simple copy as that could cause headaches and is one of the main reasons camps live in each users' home directory.  Assuming camps live in /home, here is the recommended setup.

* /home should live on its own partition, but if not possible, it is not required.
* Each camp should be owned by a valid user of the system.  

.. note:: Each user must be added to the '*func*' group for database and web server functionality to work properly.
.. note:: Each user must be added to the '*apache*' group to allow restarts of the web server.
.. note:: Each user's home directory should be o+rx to allow apache to read the docroot.

Make sure to allocate enough space in /home for the docroots in each camp.

For example, if the docroot in the project is 5G, 5Gx1.5 # 6.5G per camp. 6.5Gx10 camps # 65G 

.. note:: Having /home on LVM makes it easy to snapshot, grow or shrink as needed.

