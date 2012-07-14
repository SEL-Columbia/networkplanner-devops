#This fabfile was basically copied from the original 'restart' shell script
#There are a few slight changes to watch out for:
# - for cluster processors (cp):
#   we don't currently get the config from the "master server"
# - We ONLY remove the scenario data for cluster processors
# - We don't kill the process before the git pull
#   (shouldn't matter since paster shouldn't reload the app implicitly)

import os

from fabric.api import env, run, cd, settings, abort, sudo
import fabric
import operator
import yaml
# from fabric.decorators import hosts


DEFAULTS = {
    'home': '/var/www',
    'repo': 'git://github.com/modilabs/networkplanner.git',
    'project': 'np'
    }

def refresh_doc():
    run("python utilities/document.py")
    with cd("docs"):
        run("make html")

    docs_dir = os.path.join("np", "public", "docs")
    run("rm -Rf %s" % os.path.join(docs_dir, "*"))
    run("mkdir -p %s" % docs_dir)
    run("mv %s %s" % (os.path.join("docs", "_build", "html", "*"), docs_dir))

def deploy_cs():
    print("deploying clustered server on %(host_string)s" % env)
    run("kill `cat paster.pid`")
    run("paster setup-app %(ini_file)s" % env)
    sudo("service rabbitmq-server restart")
    run("crontab deployment/cluster-queue.crt")
    #sleep 1 so that daemon is not killed
    run("paster serve --daemon %(ini_file)s; sleep 1" % env) 
    run("kill `ps x|grep consumer.py|grep -v grep|awk '{print $1}'`")
    cronfile = os.path.join("deployment", env.cronfile)
    run("crontab %s" % cronfile)
    refresh_doc()

def deploy_ss():
    print("deploying single server on %(host_string)s" % env)
    run("kill `cat paster.pid`")
    run("paster setup-app %(ini_file)s" % env)
    #sleep 1 so that daemon is not killed
    run("paster serve --daemon %(ini_file)s; sleep 1" % env)
    cronfile = os.path.join("deployment", env.cronfile)
    run("crontab %s" % cronfile)
    refresh_doc()

def deploy_cp():
    print("deploying clustered processor on %(host_string)s" % env)
    run("rm -Rf data *.db")
    run("paster setup-app %(ini_file)s" % env)
    #sleep 1 so that daemon is not killed
    run("paster serve --daemon %(ini_file)s; sleep 1" % env)
    cronfile = os.path.join("deployment", env.cronfile)
    run("crontab %s" % cronfile)

# Define deployment system type configurations
DEPLOYMENTS = {
    'cs': {
        'description': 'cluster server',
        'cronfile':    'cluster-server.crt',
        'ini_file':    'production.ini',
        'config_env':  'production.yaml',
        'deploy_fun':  deploy_cs
        }, 
    'cp': {
        'description': 'cluster processor',
        'cronfile':    'cluster-processor.crt',
        'ini_file':    'development.ini',
        'config_env':  'development.yaml',
        'deploy_fun':  deploy_cp
        }, 
    'ss': {
        'description': 'single server',
        'cronfile':    'single-server.crt',
        'ini_file':    'production.ini',
        'config_env':  'production.yaml',
        'deploy_fun':  deploy_ss
        } 
    }

setup_called = False
def setup_env(**args):
    global setup_called
    if setup_called: return
    setup_called = True
    # use ssh config if available
    if env.ssh_config_path and os.path.isfile(os.path.expanduser(env.ssh_config_path)):
        env.use_ssh_config = True
    # ensure that args contains host_string, system_type and branch
    bools = [x in args for x in ('system_type', 'branch')]
    if not (reduce(operator.and_, bools)):
        abort("system_type and branch params are required")

    env.update(DEFAULTS)
    env.update(args)
    env.update(DEPLOYMENTS[env.system_type])
    env.project_directory = os.path.join(env.home, env.project)
    env.pip_requirements_file = os.path.join(env.project_directory, 'requirements.txt')


def upload_config():
    config_dict = yaml.load(file(env.config_env))
    fabric.contrib.files.upload_template(filename="templates/.default.cfg", 
            destination=config_dict['config-file'], 
            context=config_dict,
            mode=0600)

def deploy(**args):
    setup_env(**args)
    with cd(env.project_directory):
        pull(**args)
        sudo("pip install -r %(pip_requirements_file)s" % env)
        upload_config()
        with settings(warn_only=True):
            env.deploy_fun()


def pull(**args):
    setup_env(**args)
    with settings(warn_only=True):
        if run("test -d %s" % env.project_directory).failed:
            with cd(env.project_directory):
                run("git clone %(repo)s" %env)

    with cd(env.project_directory):
        run("git pull origin %(branch)s" % env)
        run('find . -name "*.pyc" | xargs rm -rf')
        
        
