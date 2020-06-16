from awsh.aws_connector import AWSHConnector
import click
import subprocess
import time
import os
from pathlib import Path
import json

user_home = str(Path.home())
config_file = os.path.join(user_home, '.awshell')


def which_ssh():
    global_path = os.environ['PATH']

    if os.name == 'nt':
        ssh_name = 'ssh.exe'
        split_char = ';'
    else:
        ssh_name = 'ssh'
        split_char = ':'

    for path in global_path.split(split_char):
        fpath = os.path.join(path, ssh_name)
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return fpath

    return False


def enter_ssh(ip, key):
    ssh_loc = which_ssh()

    if ssh_loc is False:
        print("ssh doesn't appear to be installed on your machine. Check your path?")
        exit(1)

    if os.name == 'nt':
        sts = os.spawnv(os.P_WAIT, ssh_loc, ['ssh', '-i', key, f'ubuntu@{ip}'])
        exit(sts)
    else:
        os.execle(ssh_loc, 'ssh', '-i', key, f"ubuntu@{ip}", os.environ)


def exec_script(instance_ips, key, file):
    print("executing files")

    file = os.path.basename(file)

    for ip in instance_ips:
        cmd = ['ssh', '-o', 'StrictHostKeyChecking no', '-i', key, f'ubuntu@{ip}', f'sed -i -e "s/\\r$//" ./{file}; sudo chmod +x ./{file}; sudo ./{file}; exit']

        p = subprocess.Popen(cmd)

        while p.poll() is None:
            time.sleep(0.1)

    print("execution complete")


def copy_file(instance_ips, key, file):
    processes = []

    outfile = os.path.basename(file)

    print(f"copying file {file}")

    for ip in instance_ips:
        p = subprocess.Popen(['scp', '-o', 'StrictHostKeyChecking no', '-i', key, file, f'ubuntu@{ip}:/home/ubuntu/{outfile}'])

        processes.append(p)

    while len(processes) > 0:
        processes = [proc for proc in processes if proc.poll() is None]
        time.sleep(.1)

    print("files copied")


@click.command()
@click.option("--configure", required=False, is_flag=True)
@click.option("-i", '--key', required=False)
@click.option("--ls", required=False, is_flag=True, default=False)
@click.argument('instance', required=False)
@click.option('-c', '--copy', default=False, is_flag=True)
@click.argument('files', nargs=-1)
def main(configure, key, ls, instance: str, copy, files):
    if configure:
        aws_credentials = {}
        aws_credentials['region_name'] = input("Enter region_name: ")
        aws_credentials['aws_access_key_id'] = input("Enter aws_access_key_id: ")
        aws_credentials['aws_secret_access_key'] = input("Enter aws_secret_access_key: ")

        with open(config_file, 'w') as file:
            json.dump(aws_credentials, file)

        exit(0)

    aws = AWSHConnector(config_file)

    if ls:
        print(aws.instances_string())
        exit(1)

    if instance is None:
        print("Error: Missing argument 'INSTANCE'.")
        exit(1)

    if key is None:
        if "AWSH_KEY" in os.environ:
            key = os.environ["AWSH_KEY"]
        else:
            print("ssh key not provided, please set AWSH_KEY environment variable or supply -i parameter.")
            exit(1)

    ips = aws.get_ip(instance)

    if len(ips) == 0:
        print(f"{instance} does not exist!")
        print(aws.instances_string())
        exit(1)

    if len(files) == 0:
        if len(ips) > 1:
            print("Error: cannot ssh with multiple ips. Please specify your instance.")
            exit(1)
        else:
            enter_ssh(ips[0], key)

    for file in files:
        copy_file(ips, key, file)

    if not copy:
        exec_script(ips, key, files[0])


if __name__ == '__main__':
    main()
