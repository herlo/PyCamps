# PyCamps #

PyCamps is inspired by the Perl DevCamps created by EndPoint. The idea is simply to make it easy for developers to have their own little environments to build web applications. This PyCamps tool is built to manage PHP/MySQL based applications, like CakePHP, Magento and Wordpress.   As with DevCamps, this tool could easily be adapted to accomodate other web development configurations, like Python, Perl with Postgresql or some other database.

## PyCamps Installation ##

To install PyCamps, read the INSTALL.markdown document in this directory.

## PyCamps Structure ##

The camp file structure will look similar to this:

    /home/
        clints/
            campX/
                httpd/
                    conf.d/site.conf
                    conf.d/ssl.conf
                docroot/
                    project-root/
				logs/
					campX-access_log
					campX-error_log

- 'httpd' holds the configurations for the apache virtual host.  It is possible to use other web servers, like nginx, lighttpd, etc. if desired.
- 'docroot' holds your web code.  This could be any type of code, php, perl, python, etc. Administrators will need to setup any dependencies. The content of docroot will likely come from the project's master code repository.
- 'logs' holds web server and database logs :).  These should be available to you to help troubleshoot and debug issues with the code.

## Commands Quickstart ##

The script that controls all of PyCamps is 'pc'.  The two main things pc can do is manage projects or camps. 

    $ pc -h
    usage: pc [-h] {project,camp} ...
    
    Dispatches commands to manage development project data
    
    positional arguments:
      {project,camp}
        camp          camp management
        project       project management
	.. snip ..

Most of the project commands are commands that will be run by an administrator, but some are useful to developers:

    $ pc project list
    == Project List ==
    Project: abd 'short description' (owner: clints) ACTIVE
    Project: rma 'short description' (owner: clints) ACTIVE

This, then leads into the ability to create a camp based upon one of these projects:

    $ pc camp init rma -d 'new refund feature'
    == Creating camp71 ==
    camp71 database snapshot complete
    camp71 database configured
    camp71 database started
    camp71 directory created
    camp71 repo cloned from project 'rma' repo
    camp71 repo cloned and pushed to camp71 remote
    camp71 web vhost config created
    camp71 web log directory created
    camp71 web server restarted
    -- camp71 has been setup at /home/clints/camps/camp71 --

Head on over to the proper camp directory shown above and start working on your code!!

For a more complete rundown of many of the functions in 'pc', please read the USAGE.markdown document.

## Git Repository ##

A git repository provides functionality to enable campers to build in their own isolated environments using a snapshot of the live docroot (no more than 24 hours previous).  Each camp has its own docroot which will be stored in git. If a refresh is desired, the campX branch (a branch with the same name as the camp) will be removed and cloned from the master branch. In this way, developers can have a clean tree to work from on demand.

The layout of the git repository is simple, yet efficient.

    origin/
        master # original clone, what is currently live
        campX # branched from master for camp to use

A post-receive-hook ensures the camp doesn't exist on a qa server, then pushes camp to qa camp for testing.
