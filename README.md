Overview
========

Repository for automated deployment/configuration of computing nodes associated with networkplanner.

To deploy to a network planner node use:

    # setup baseline packages on machine
    ssh <host> 'bash -s' < bootstrap.sh
    # setup network planner specific packages, create np user and directories
    fab -H <host> provision:system_type=<system>,branch=<np_devops_branch>
    # deploy network planner as the np user (note that host_np_user should login as np user)
    fab -H <host_np_user> deploy:system_type=<system>,branch=<np_branch>,config_env=<my_config_env.yaml>

Where `<system>` is one of:
* `ss` - Single Server Mode
* `cs` - Cluster Server that "manages" clusters
* `cp` - A cluster processor computing node

For cluster processors, you can pass multiple comma delim'd hosts to fab and the -P option to provision or deploy in parallel.  

Also includes automated backup utils.  

Main Components
===============

* `fabfile.py` - fabfile which orchestrates deployment
* `chef-repo` - the chef configuration for setting up nodes
* `<server-type>.json` - files defining chef components of each server type
* `backup.sh` - script defining backup process

Caveat Emptor
=============

* You should have a reasonable understanding of Network Planner and it's architecture before using this (see:  github.com/SEL-Columbia/networkplanner)

* Running the deploy task requires a yaml file (see sample.yaml) that contains important configuration information.  See fabfile.py for default file names.  It can be overridden by a config_env command line parameter.  

* See fabfile.py for details
