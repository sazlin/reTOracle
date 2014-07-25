from __future__ import print_function
from fabric.api import run
from fabric.api import env
from fabric.api import execute
from fabric.api import prompt
from fabric.api import sudo
from fabric.contrib.project import upload_project

import boto.ec2
import time
import os

env.aws_region = 'us-west-2'


def deploy_to_production_full():
    # TBD: implement deploy to production
    #_deploy(os.environ.get('R_HOST_INSTANCE_ID'), 'Prod', True)
    raise NotImplementedError()


def stage_for_testing():
    _deploy(os.environ.get('R_TEST_HOST_INSTANCE_ID'), 'Test', True)


def _deploy(instance_id, r_config, full_deploy):
    conn = _get_ec2_connection()
    instance = conn.get_only_instances(instance_ids=[instance_id])[0]
    if instance:
        print("Deployment Started for Instance {}:".format(instance.id))

        #Update apt-get
        run_command_on_server(_update_apt_get, instance)

        #Install pip
        run_command_on_server(_setup_pip, instance)

        #Install requirements
        run_command_on_server(_auto_install_req, instance)

        #Remove existing project files
        run_command_on_server(_remove_existing_project_files, instance)

        #Upload new project files
        run_command_on_server(_upload_project_files, instance)

        #Install, configure, and start nginx
        # run_command_on_server(_install_nginx, instance)
        setup_nginx(r_config, instance)

        #Install, configure, and start supervisor
        if r_config == 'Test':
            run_command_on_server(_setup_supervisor_test, instance)
        elif r_config == 'Prod':
            run_command_on_server(_setup_supervisor_prod, instance)
        else:
            raise Exception('Invalid r_config.')

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


def _upload_project_files():
    print("Uploading Project files from {}".format(os.getcwd()))
    upload_project(remote_dir='./', use_sudo=True)
    print("Upload complete")


def _remove_existing_project_files():
    print("Removing existing project files...")
    sudo('rm -rf ./*')
    print("Old files removed.")


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


def setup_nginx(r_config, instance):
    if r_config == 'Prod':
        print("Setting up nginx [PROD]...")
        run_command_on_server(_install_nginx_prod, instance)
    elif r_config == 'Test':
        print("Setting up nginx [TEST]...")
        run_command_on_server(_install_nginx_test, instance)
    print("nginx installed and started.")


def _install_nginx_prod():
    print("Setting up nginx...")
    sudo('apt-get install nginx')
    sudo('mv /etc/nginx/sites-available/default /etc/nginx/sites-available/default.orig')
    sudo('mv ./rheTOracle/nginx_config_prod /etc/nginx/sites-available/default')
    sudo('/etc/init.d/nginx start')
    print("nginx installed and started.")


def _install_nginx_test():
    print("Setting up nginx...")
    sudo('apt-get install nginx')
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
