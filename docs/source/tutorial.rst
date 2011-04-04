PyCamps Tutorial
================

Let's start with the most common scenario for PyCamps. These will be the most common ways to use the system. Other common tools and commands can be found in the :doc:`usage guide </usage_guide>`.

Setting up Projects
-------------------
PyCamps makes heavy use of some of the core pieces of Gitolite. While Gitolite isn't *technically* required, it is highly recommended. Keep in mind, however, that the concepts of sharing/cloning camps may not work properly, see 'Camp Sharing' in :doc:`admin_config_guide` for more information.   

If this is the first time installing gitolite, please read the very `excellent documentation <https://github.com/sitaramc/gitolite#start>`_. 

Gitolite can be setup with very basic components, but it does need to have wildcard repos enabled. Once gitolite is installed, please follow these conventions for each project.

The gitolite-admin.conf should have a section for admins. These admins should match the :data:`ADMINS` section in the :mod:`config.settings` module. In addition, two entries should be made for each project::

    @admins = clints ags

    repo    community/master
            C   =   @admins
            RW+D =  @admins
            R   =   @all
            
    repo    community/camp[0-9]+
            C   =   CREATOR
            RW+ =   CREATOR
            RW+ =   @admins
            RW  =   WRITERS
            R   =   READERS

The first repo configuration 'community/master' defines the location from which a new camp will pull its original source code. The second entry, is intended to be used to keep all camp code in one location. As stated before, the master repository is optional and could come from such places as github.com or fedorahosted.org. Unfortunately, for now, the camp repositories are required to be on gitolite for now as PyCamps uses this information internally. It is **highly** recommended to use gitolite on-site for PyCamps.

As stated in the `gitolite documentation <https://github.com/sitaramc/gitolite#start>`_, when a camp is initiated the CREATOR owns the repository and in this case will have the ability to Read / Write and Rewind the repository. In addition, the CREATOR can also grant rights to other users, allowing them to use their repository. This is one of the killer features of PyCamps called :doc:`Camp Sharing </usage_guide>`.

Once gitolite is configured, the project will need a good baseline before a camp can be cloned. When a project is already running, it's pretty simple to make a good baseline. Essentially, the source code needs to run which likely means a copy of the live environment usually works.  A couple of things to think about while building the baseline source code.

* Configuration files tend to be external to a code repository. Don't include them unless there is room for development, qa and live system. 
* Migrations work well in a camps environment, make sure to include db migrations in the source code repository. 

.. warning:: **NEVER INCLUDE LIVE USERNAMES/PASSWORDS IN CONFIGURATION FILES**. 

Clone the repository and create a 'develop' branch::

    $ git clone git@git.example.com:community/master
    Cloning into master...
    remote: Counting objects: 3, done.
    remote: Total 3 (delta 0), reused 0 (delta 0)
    Receiving objects: 100% (3/3), done.
    $ cd master/
    $ mkdir shop/
    $ echo "<?php phpinfo(); ?>" > shop/index.php
    
At each stage during the baseline creation, don't forget to document, commit code often. Keep code commits small so they are easy to rollback::

    $ git add file [file...]
    $ git commit -m "reason for committing"

After the baseline code works with a web server and database, make sure all code is committed, then push it to the project's master repository::

    $ git push origin master
    Counting objects: 5, done.
    Delta compression using up to 4 threads.
    Compressing objects: 100% (2/2), done.
    Writing objects: 100% (4/4), 356 bytes, done.
    Total 4 (delta 0), reused 0 (delta 0)
    To git@git.example.com:community/master
       c098394..9b82e49  master -> master

At this point, the project is ready to be cloned. **Lather, rinse and repeat** for every project to be used with PyCamps.
 
Managing Projects
------------------
PyCamps is used to grab code from the master code repository and allow editing into a separate camp repository. Camps can be initialized from this by creating a project.  This can *only* be done by an admin, which is set in the :attr:`ADMINS` property of :mod:`config.settings`.  

Add a Project
^^^^^^^^^^^^^
Adding a new project is generally very simple.::

    $ pc project add -h
    usage: pc project add [-h] [--owner owner] name desc rcs_url lvm_path size
    
    positional arguments:
      name           project name to add
      desc           project description
      rcs_url        url/path to master code repo
      lvm_path       logical volume location for master database
      size           logical volume snapshot size

To add the project, provide the above fields.  If the owner is not the same as the person setting up the project, this should also be set::

	$ pc project add community 'community magento website' 'gitolite@git.example.org:community/master' '/dev/db/community' '200m'
	== Adding community to project list ==
	Activating 'community'
	Project community, with remote repo: gitolite@git.example.org:community/master, failed to activate. Please ensure you can clone
	the repo and then run 'pc admin project activate community'

In some cases, something isn't quite right with the repository. Either it was specified incorrectly, in this case it should have been 'gitolite@git.example.com:community/master', or the repository does not let the user clone properly.  The ``pc project add`` checks to make sure the repository can be cloned and if it cannot, the project cannot be activated.  Fixing this problem is actually pretty simple:

Edit a Project
^^^^^^^^^^^^^^
::

    $ pc project edit community --remote 'gitolite@git.example.com:community/master'

List Projects
^^^^^^^^^^^^^
::

    $ pc project list -ln community
    == Project List ==
    Project: community 'community magento website' (owner: clints) INACTIVE
        [remote: gitolite@git.example.com:community/master, webserver: httpd, database server: mysql, master db: /dev/db/community, snap size: 200m]

Editing the project will fix the problem, and now the remote repository is correct.  Now that everything is correct, the project will need to be activated.  Again, the remote repository will be verified, and if it succeeds, the project will be activated.

Activate a Project
^^^^^^^^^^^^^^^^^^
::

    $ pc project activate community
    Activating 'community'
    Project: community with remote repo: gitolite@git.example.com:community/master, has been activated by clints

Now the project is active and ready to be cloned into a camp!


Deactivate a Project
^^^^^^^^^^^^^^^^^^^^
Once in a while, there is a need to deactivate a particular project.  This is usually because it's has come to end of life or is just too hard to maintain.  However, it might still be desired to reactivate the project later.  A camp can not be initialized from an inactive project and would have to be activated if it were desired to be used again.  To deactivate a project::

    $ pc project rm abd
    Deactivating 'abd'
    Project 'abd' deactivated

Any existing camp can continue to use its own repo, but will not be able to update from the master repo (using pc camp refresh).  

Utilizing Camps
---------------
Now that at least one project has been created and activated, camps can be initialized.  In addition, a camp has many other features, including starting, stopping and restarting the database, restarting the web server, sharing a camp, tracking and pushing files to camp repositories to later be sent to qa, then live.  Using camps is also very simple, just initialize and start working.

Initialize a Camp
^^^^^^^^^^^^^^^^^
::

    $ pc camp init community -d 'applying company theme'
    == Creating camp74 ==
    camp74 database snapshot complete
    camp74 database configured
    camp74 database started
    camp74 directory created
    camp74 repo cloned from project 'community' repo
    camp74 repo cloned and pushed to camp74 remote
    camp74 web vhost config created
    camp74 web log directory created
    camp74 web server restarted
    -- camp74 has been setup at /home/clints/camps/camp74 --

When a camp is initialized, a camp is given an id.  In this case, camp74.  Then, the database is snapshotted, configured and started, then the project's master repository is cloned and the web server is configured to be used.  The directory of the camp is provided on the last line.  One optional parameter (-d/--desc) is not required, but can be useful to remind the developer what was going on within a particular camp.  

In the initialized camp, will be a minimal set of configuration components::

    [clints@x201 camp74]$ ls -l
    total 8
    drwxrwsr-x. 3 clints apache 4096 Mar 29 15:43 httpd
    drwxrwsr-x. 2 clints apache 4096 Mar 29 15:43 logs
    -rw-rw-r--. 1 clints apache    0 Mar 29 15:43 README

Depending on the scheme set up by the administrator, the group ownership is set properly as is the SetGID bit.  This allows the httpd process be able to read and modify logs and configs.  If the group ownership isn't correct, a simple chgrp should work since the developer should be in the proper group, or camps will not work.

Commonly, the initial setup will be done for the project with a good baseline structure in the source code repository.  However, if the repository is basically blank, or doesn't have some core components, seeing results on the web browser can be challenging.  Luckily, with just a couple commands, a basic website can be setup to make sure things are working.::

    [clints@x201 camp74]$ mkdir docroot
    [clints@x201 camp74]$ echo camp74 > docroot/index.html

Open the web browser and point it at http://camp74.example.com/, and assuming the administrator has added the proper dns, the camp should show 'camp74' as content.  If a docroot already exists with proper configuration, the camp should just work(tm).

.. note:: Determining the structure of the code repository is important. An administrator should set the :data:`WEB_DOCROOT` value in the :mod:`config.settings` module to the proper value.

List Camps
^^^^^^^^^^
Another useful thing might be to see what camps are being used::

    $ pc camp list
    == Camps List ==
    camp74 'applying company theme' (project: community, owner: clints) ACTIVE
    camp76 'adding shipping details' (project: community, owner: kynalya) ACTIVE

Other useful options: *-l* (long [detail] list) and *-i* (specific camp id)::

    $ pc camp list -l -i 65
    == Camps List ==
    camp65 'no description' (project: rma, owner: kynalya) INACTIVE
   	    [path: /home/kynalya/camps/camp65, remote: None, db host: localhost, db port: 3365]

Start/Stop/Restart Camps
^^^^^^^^^^^^^^^^^^^^^^^^
Because of the way that PyCamps is configured, stopping and starting the database is very simple::

    $ pc camp stop
    Stopping database on camp77
    camp77 database stopped

A simple process query makes sure it's stopped::

    $ ps -ef | grep camp77 | grep -v grep
    (no output)

Start the camp again::

    $ pc camp start
    Starting database on camp77
    camp77 database started

Make sure it started::

    $ ps -ef | grep camp77 | grep -v grep
    mysql     7424     1  0 11:57 ?        00:00:00 /usr/libexec/mysqld --datadir=/var/lib/mysql/camp77 --socket=/var/lib/mysql/camp77/mysql.sock 
    --pid-file=/var/run/mysqld/camp77.pid --user=mysql --port=3377 --log=/var/log/mysqld-77.log --datadir=/var/lib/mysql/camp77 
    --socket=/var/lib/mysql/camp77/mysql.sock --pid-file=/var/run/mysqld/camp77.pid --user=mysql --port=3377 --log=/var/log/mysqld-77.log 
    --datadir=/var/lib/mysql/camp77 --socket=/var/lib/mysql/camp77/mysql.sock --pid-file=/var/run/mysqld/camp77.pid --user=mysql --port=3377 
    --log=/var/log/mysqld-77.log

In addition, restarting the web server can also be done very easily::

    $ pc camp restart --web
    restarting web server
    camp77 web server restarted

.. note:: The :option:`--web` option is a must for a web-only restart.  Omitting it will restart both the web and database servers.

.. note:: The web server cannot be stopped by a user. If a configuration issue caused the web server to not restart, it can just simply be restarted again once the issue has been resolved.

Refresh a Camp
^^^^^^^^^^^^^^
.. todo:: create/document refresh camp db and/or web server

Camp Sharing
^^^^^^^^^^^^
.. todo:: share - give permission to clone a camp
.. todo::    unshare             remove permission to clone a camp
.. todo::    clone               clone a shared camp

Camp Revision Control
^^^^^^^^^^^^^^^^^^^^^
.. todo::    track               tracked files/dirs
.. todo::    untrack             before commit, untrack files
.. todo::    commit              commit tracked files
.. todo::    log                 show commit log
