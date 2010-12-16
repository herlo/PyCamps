PyCamps
-------

PyCamps is inspired by the Perl DevCamps created by EndPoint. The idea is simply to make it easy for developers to have their own little environments to build web applications. This PyCamps tool is built to manage PHP/MySQL based applications, like CakePHP, Magento and Wordpress.   As with DevCamps, this tool could easily be adapted to accomodate other web development configurations, like Python, Perl with Postgresql or some other database.

PyCamps Structure
-----------------

The camp structure will look something like this:

    /home/
        clints/
            campX/
                .git/
                .gitignore
                httpd/
                    conf.d/skullcandy.conf
                    conf.d/ssl.conf
                mysql/
                    my.cnf
                docroot/
                    mobile/
                db/
                    migrations.sql
                images/

Commands
--------

All actions use the 'camp' command with specified arguments passed to perform a particular action:

    pycamp
        init --desc "mix master landing pages"  # camp_id returned on successful init
        rm --id <camp_id>  # remove camp_id
        refresh --db --web --conf --all  # refresh the database, the web root, the configs, or all (--all)
        add <file_list>  # adds the list of files ready to be sent to qa
        commit [-m <message] # creates an entry with a list of files to be sent to qa
        push # pushes all commits to qa server

Git Repository
--------------

A git repository provides functionality to enable campers to build in their own isolated environments using a snapshot of the live docroot (no more than 24 hours previous).  Each camp has its own docroot which will be stored in git. If a refresh is desired, the campX branch (a branch with the same name as the camp) will be removed and cloned from the master branch. In this way, developers can have a clean tree to work from on demand.

The layout of the git repository is simple, yet efficient.

    origin/
        master # original clone, what is currently live
        campX # branched from master for camp to use

A post-receive-hook ensures the camp doesn't exist on a qa server, then pushes camp to qa camp for testing.
