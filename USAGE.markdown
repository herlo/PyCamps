# PyCamps Overview #

As noted in the README.markdown section 'Commands Quickstart', the 'pc' command controls interactions with the camps environment.  PyCamps has two basic components, projects and camps.  The 'pc' command clones code from a single project to work on a new feature or bugfix.  However, it is possible to do many things with camps beyond just cloning code.  In this document we'll explain and show some common ways to use PyCamps.

The relationship between projects and camps is important.  Each camp must refer to an existing, active project when initialized.  When a camp is run through the qa process, or pushed live, the code in the camp is reintegrated back into the project's master repository.  This process allows new camps to keep the latest code from the live servers available.  In addition, each project can and likely will, have a database which can be cloned.  This allows easy access to data as close to live without actually giving the developer access to the live database.  A developer can also dig right into the problem on a problem quickly and easily, rather than waiting for an admin to give them access to a shared database.

Finally, PyCamps is not the end all, be all of code integration and management.  It's intended to be a development/integration environment for a lot of projects, but at some point it may not scale.  The devs can live on one box and the database another, but at some point, another box would have to be created or expanded.  If the database becomes very large, syncronization could be an issue.  Many of these items could be dealt with from the administrators end as well.  I would love feedback on how you use PyCamps and how you scaled it to solve issues. 

# PyCamps Usage #

Let's start with a few common scenarios for PyCamps.  These will be the most common ways to use the system.

## Setting up a Project ##
The scenario here is that we have a git repo somewhere we want to use as the master code repository.  For camps to be initialized from this, a project needs to be setup.  This can only be done by an admin, which is setup in config/settings.py ADMINS section.  Create a new project:
 
### Add a Project ###

    $ pc project add -h
    usage: pc project add [-h] [--owner owner] name desc rcs_url lvm_path size
    
    positional arguments:
      name           project name to add
      desc           project description
      rcs_url        url/path to master code repo
      lvm_path       logical volume location for master database
      size           logical volume snapshot size

To add the project, provide the above fields.  If the owner is not the same as the person setting up the project, this should also be set:


	$ pc project add community 'community magento website' 'gitolite@git.example.org:community/master' '/dev/db/campmaster' '200m'
	== Adding community to project list ==
	Activating 'community'
	Project community, with remote repo: gitolite@git.example.org:community/master, failed to activate. Please ensure you can clone
	the repo and then run 'pc admin project activate community'

In some cases, something isn't quite right with the repository.  Either it was specified incorrectly, in this case it should have been 'gitolite@git.example.com:community/master', or the repository does not let the user clone properly.  The 'pc project add' checks to make sure the repository can be cloned and if it cannot, the project cannot be activated.  Fixing this problem is actually pretty simple:

### Edit a Project ###

	$ pc project edit community --remote 'gitolite@git.example.com:community/master'

### List Projects ###

	$ pc project list -ln community
	== Project List ==
	Project: community 'community magento website' (owner: clints) INACTIVE
	  [remote: gitolite@git.example.com:community/master, webserver: httpd, database server: mysql, master db: /dev/db/campmaster, snap size: 200m]

Editing the project will fix the problem, and now the remote repository is correct.  Now that everything is correct, the project will need to be activated.  Again, the remote repository will be verified, and if it succeeds, the project will be activated.

### Activate a Project ###

	$ pc project activate community
	Activating 'community'
	Project: community with remote repo: gitolite@git.example.com:community/master, has been activated by clints

Now the project is active and ready to be cloned into a camp!

Once in a while, there is a need to deactivate a particular project.  This is usually because it's has come to end of life or is just too hard to maintain.  However, it might still be desired to reactivate the project later.  A camp can not be initialized from an inactive project and would have to be activated if it were desired to be used again.  To deactivate a project

### Deactivate a Project ###

	$ pc project rm abd
	Deactivating 'abd'
	Project 'abd' deactivated

Any existing camp can continue to use its own repo, but will not be able to update from the master repo (using pc camp refresh).  

## Using Camp Tools ##
Now that at least one project has been created and activated, camps can be initialized.  In addition, a camp has many other features, including starting, stoping and restarting the database, restarting the web server, sharing a camp, tracking and pushing files to camp repositories to later be sent to qa, then live.  Using camps is also very simple, just initialize and start working:

## Initialize a Camp ##

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

In the initialized camp, will be a minimal set of configuration components:

	[clints@x201 camp74]$ ls -l
	total 8
	drwxrwsr-x. 3 clints apache 4096 Mar 29 15:43 httpd
	drwxrwsr-x. 2 clints apache 4096 Mar 29 15:43 logs
	-rw-rw-r--. 1 clints apache    0 Mar 29 15:43 README

Depending on the scheme set up by the administrator, the group ownership is set properly as is the SetGID bit.  This allows the httpd process be able to read and modify logs and configs.  If the group ownership isn't correct, a simple chgrp should work since the developer should be in the proper group, or camps will not work.

Commonly, the initial setup will be done for the project with a good baseline structure in the source code repository.  However, if the repository is basically blank, or doesn't have some core components, seeing results on the web browser can be challenging.  Luckily, with just a couple commands, a basic website can be setup to make sure things are working.

[clints@x201 camp74]$ mkdir docroot
[clints@x201 camp74]$ echo camp74 > docroot/index.html

Open your web browser and point it at http://camp74.yourdomain.com/, and assuming the administrator has added the proper dns, the camp should show 'camp74' as content.  

If a docroot already exists with proper configuration, the camp should just work(tm).

Another useful thing might be to see what camps are being used.

### List Camps ###

	$ pc camp list
	== Camps List ==
	camp74 'applying company theme' (project: community, owner: clints) ACTIVE
	camp76 'adding shipping details' (project: community, owner: kynalya) ACTIVE

Other useful options are -l (long [detail] list) and -i (specific camp id)

	$ pc camp list -l -i 65
	== Camps List ==
	camp65 'no description' (project: rma, owner: kynalya) INACTIVE
		[path: /home/kynalya/camps/camp65, remote: None, db host: localhost, db port: 3365]




