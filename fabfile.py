from __future__ import print_function
from fabric.api import run
from fabric.api import env
from fabric.api import execute
from fabric.api import prompt
from fabric.api import put
from fabric.api import sudo
from fabric.utils import abort
from fabric.contrib.console import confirm
from fabric.contrib.project import upload_project
from fabric.contrib.files import exists

import boto.ec2
import time
import os

env.aws_region = 'us-west-2'


def deploy(r_dest=None, r_option='Full'):
    if not r_dest:
        r_dest = raw_input("Enter deploy target (Test or Prod): ")
    instance = None
    if r_dest == 'Prod':
        if not confirm("Are you sure you want to deploy to production?", default=False):
            abort("Deployment to production aborted.")
        instance_id = os.environ.get('R_HOST_INSTANCE_ID')
    elif r_dest == 'Test':
        instance_id = os.environ.get('R_TEST_HOST_INSTANCE_ID')
    else:
        raise Exception('invalid r_dest')
    conn = _get_ec2_connection()
    print("Instance id: ", instance_id)
    instance = conn.get_only_instances(instance_ids=[instance_id])[0]
    if not instance:
        raise Exception('Could not get instance')

    print("Deployment Started for Instance {}:".format(instance.id))

    #initial setup related stuff
    if r_option == 'project':
        pass
    elif r_option == 'config':
        pass
    else:
        #Update apt-get
        run_command_on_server(_update_apt_get, instance)

        #Install pip
        run_command_on_server(_setup_pip, instance)

        #Install requirements
        run_command_on_server(_auto_install_req, instance)
        #deploy everything

    if r_option == 'config':
        #Remove config files only
        run_command_on_server(_remove_existing_config_files, instance)

        #Upload config files only
        run_command_on_server(_upload_config_files, instance)
    else:
        #Remove all existing project files
        run_command_on_server(_remove_existing_project_files, instance)

        #Upload all new project files
        run_command_on_server(_upload_project_files, instance)

    #Install, configure, and start nginx
    # run_command_on_server(_install_nginx, instance)
    setup_nginx(r_dest, instance)

    setup_supervisor(r_dest, instance)

    #Restart nginx
    run_command_on_server(_restart_nginx, instance)
    print("Deployment Complete for Instance {}.".format(instance.id))


def _update_apt_get():
    print("Updating apt-get...")
    sudo("apt-get update")
    print("Done.")


def _auto_install_req():
    f = open("requirements.txt", 'r')
    sudo("apt-get build-dep python-psycopg2")
    print("DEPENDENCIES BUILT")
    for line in f:
        index_ = line.index('==', 0, len(line))
        module = line[:index_]
        command = "pip install %s" % module
        sudo(command)


def _setup_pip():
    print("Installing pip...")
    sudo("apt-get install python-dev build-essential python-pip")
    print("Done.")


def _setup_flask():
    print("Installing Flask...")
    sudo('pip install flask')
    print("Done.")


def _rm_if_exists(path):
    if exists(path):
        sudo("rm " + path)
    else:
        print("Path does not exist:" + path)


def _remove_existing_config_files():
    print("Removing config files...")
    _rm_if_exists("./rheTOracle/supervisord-test.conf")
    _rm_if_exists("./rheTOracle/supervisord-prod.conf")
    _rm_if_exists("./rheTOracle/nginx_config_test")
    _rm_if_exists("./rheTOracle/nginx_config_prod")
    print("Config files removed")


def _upload_config_files():
    print("Uploading new config files...")
    put("./supervisord-test.conf", "./rheTOracle/supervisord-test.conf", use_sudo=True)
    put("./supervisord-prod.conf", "./rheTOracle/supervisord-prod.conf", use_sudo=True)
    put("./nginx_config_test", "./rheTOracle/nginx_config_test", use_sudo=True)
    put("./nginx_config_prod", "./rheTOracle/nginx_config_prod", use_sudo=True)
    print("New config files uploaded")


def _upload_project_files():
    print("Uploading Project files from {}".format(os.getcwd()))
    upload_project(remote_dir='./', use_sudo=True)
    print("Upload complete")


def _remove_existing_project_files():
    print("Removing existing project files...")
    sudo('rm -rf ./*')
    print("Old files removed.")


def setup_supervisor(r_dest, instance):
    if r_dest == 'Prod':
        run_command_on_server(_setup_supervisor_prod, instance)
    elif r_dest == 'Test':
        run_command_on_server(_setup_supervisor_test, instance)
    else:
        raise Exception('invalid r_dest')


def _setup_supervisor_test():
    print("Setup and run supervisor [TEST]...")
    # ret code 1 comes back if no process to kill, which is fine
    # ret code 127 comes back if supervisor hasn't been installed yet (ex. on first deployment of fresh instance)
    env.ok_ret_codes = [0, 1, 127]
    sudo('supervisorctl -c /etc/supervisor/supervisord.conf stop all')
    sudo('killall -w supervisord')
    env.ok_ret_codes = [0]
    sudo('apt-get install supervisor')
    sudo('mv ./rheTOracle/supervisord-test.conf /etc/supervisor/conf.d/supervisord.conf')
    sudo('/etc/init.d/supervisor start')
    print("Supervisor running")


def _setup_supervisor_prod():
    print("Setup and run supervisor [PROD}...")
    # ret code 1 comes back if no process to kill, which is fine
    # ret code 127 comes back if supervisor hasn't been installed yet (ex. on first deployment of fresh instance)
    env.ok_ret_codes = [0, 1, 127]
    sudo('supervisorctl -c /etc/supervisor/supervisord.conf stop all')
    sudo('killall -w supervisord')
    env.ok_ret_codes = [0]
    sudo('apt-get install supervisor')
    sudo('mv ./rheTOracle/supervisord-prod.conf /etc/supervisord.conf')
    sudo('/etc/init.d/supervisor start')
    print("Supervisor running")


def setup_nginx(r_dest, instance):
    if r_dest == 'Prod':
        print("Setting up nginx [PROD]...")
        run_command_on_server(_install_nginx_prod, instance)
    elif r_dest == 'Test':
        print("Setting up nginx [TEST]...")
        run_command_on_server(_install_nginx_test, instance)
    print("nginx installed and started.")


def _install_nginx_prod():
    print("Setting up nginx...")
    sudo('apt-get install nginx')
    if exists("/etc/nginx/sites-available/default"):
        sudo('mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig')
    sudo('mv ./rheTOracle/nginx_config_prod /etc/nginx/sites-available/default')
    sudo('/etc/init.d/nginx start')
    print("nginx installed and started.")


def _install_nginx_test():
    print("Setting up nginx...")
    sudo('apt-get install nginx')
    if exists("/etc/nginx/sites-available/default"):
        sudo('mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig')
    sudo('mv ./rheTOracle/nginx_config_test /etc/nginx/sites-available/default')
    sudo('/etc/init.d/nginx start')
    print("nginx installed and started.")


def _restart_nginx():
    print("Restarting Nginx...")
    sudo('/etc/init.d/nginx restart')
    print("Nginx Restarted.")


def _get_ec2_connection():
    if 'ec2' not in env:
        conn = boto.ec2.connect_to_region(env.aws_region)
        if conn is not None:
            env.ec2 = conn
            print("Connected to EC2 region {}".format(env.aws_region))
        else:
            msg = "Unable to connect to EC2 region %s"
            raise IOError(msg % env.aws_region)
    return env.ec2


def provision_instance(wait_for_running=False, timeout=60, interval='2'):
    """This will create a new instance for whomever runs this"""
    wait_val = int(interval)
    timeout_val = int(timeout)
    conn = _get_ec2_connection()
    instance_type = 't1.micro'
    key_name = 'kp1'
    security_group = 'ssh-access'
    image_id = 'ami-bf582a8f'

    reservations = conn.run_instances(
        image_id,
        instance_type=instance_type,
        key_name=key_name,
        security_groups=[security_group, ]
    )
    new_instances = [i for i in reservations.instances if i.state == 'pending']
    running_instance = []
    if wait_for_running:
        waited = 0
        while new_instances and (waited < timeout_val):
            time.sleep(wait_val)
            waited += int(wait_val)
            for instance in new_instances:
                state = instance.state
                print("Instance {} is {}".format(instance.id, state))
                if state == "running":
                    running_instance.append(
                        new_instances.pop(new_instances.index(i))
                    )
                instance.update()


def list_reservations():
    _get_ec2_connection()
    print(env.ec2.get_all_reservations())


def list_aws_instances(verbose=False, state=''):
    conn = _get_ec2_connection()

    reservations = conn.get_all_reservations()
    instances = []
    for res in reservations:
        for instance in res.instances:
            if state == 'all' or instance.state == state:
                instance = {
                    'id': instance.id,
                    'type': instance.instance_type,
                    'image': instance.image_id,
                    'state': instance.state,
                    'instance': instance,
                }
                instances.append(instance)
    env.instances = instances
    if verbose:
        import pprint
        pprint.pprint(env.instances)


def select_instance(state='running'):
    if hasattr(env, 'active_instance'):
        return

    list_aws_instances(state=state)

    prompt_text = "Please select from the following instances:\n"
    instance_template = " %(ct)d: %(state)s instance %(id)s\n"
    for idx, instance in enumerate(env.instances):
        ct = idx + 1
        args = {'ct': ct}
        args.update(instance)
        prompt_text += instance_template % args
    prompt_text += "Choose an instance: "

    def validation(input):
        choice = int(input)
        if not choice in range(1, len(env.instances) + 1):
            raise ValueError("%d is not a valid instance" % choice)
        return choice

    choice = prompt(prompt_text, validate=validation)
    env['active_instance'] = env.instances[choice - 1]['instance']


def run_command_on_server(command, instance=None):
    if instance is None:
        select_instance(state='running')
        instance = env.active_instance
    selected_hosts = [
        'ubuntu@' + instance.public_dns_name
    ]
    execute(command, hosts=selected_hosts)


def host_type():
    run('uname -s')


def select_and_stop_instance(force=False):
    select_instance(state='running')
    instance = env.active_instance
    if instance is None:
        print("No active instance selected.")
        return

    choice = prompt(
        "Are you sure you want to stop instance {}? (y/n)".format(instance))
    confirm = ('y' in choice) and (len(choice) == 1)

    if confirm:
        print("Stopping instance: {}".format(instance))
        instance.stop()
    else:
        print("Aborting.")


def select_and_terminate_instance():
    select_instance(state='stopped')
    instance = env.active_instance
    if instance is None:
        print("No active instance selected.")
        return

    choice = prompt(
        "Are you sure you want to terminate instance {} (y/n)".format(instance))
    confirm = ('y' in choice) and (len(choice) == 1)

    if confirm:
        print("Terminating instance: {}".format(instance))
        instance.terminate()
    else:
        print("Aborting.")
