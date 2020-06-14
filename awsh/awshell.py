from awsh.aws_connector import AWSHConnector
from awsh.exit_statuses import SSH_EXIT_OK, EXIT_FAILURE, EXIT_OK
import click
import subprocess
import time
import sys
import os
from pathlib import Path
import json

user_home = str(Path.home())
config_file = os.path.join(user_home, '.awshell')


def enter_ssh(ip, key):
    print(f"{ip}~{key}", end='')


def exec_script(instance_ips, key, file):
    print("executing files", file=sys.stderr)

    for ip in instance_ips:
        cmd = ['ssh', '-o', 'StrictHostKeyChecking no', '-i', key, f'ubuntu@{ip}', f'sed -i -e "s/\\r$//" ./{file}; sudo chmod +x ./{file}; sudo ./{file}; exit']

        p = subprocess.Popen(cmd)

        while p.poll() is None:
            time.sleep(0.1)

    print("execution complete", file=sys.stderr)


def copy_file(instance_ips, key, file):
    processes = []

    print(f"copying file {file}", file=sys.stderr)

    for ip in instance_ips:
        p = subprocess.Popen(['scp', '-o', 'StrictHostKeyChecking no', '-i', key, file, f'ubuntu@{ip}:/home/ubuntu/{file}'])

        processes.append(p)

    while len(processes) > 0:
        processes = [proc for proc in processes if proc.poll() is None]
        time.sleep(.1)

    print("files copied", file=sys.stderr)


def stderr_input(prompt):
    print(prompt, file=sys.stderr, end='')
    res = input()
    return res


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
        aws_credentials['region_name'] = stderr_input("Enter region_name: ")
        aws_credentials['aws_access_key_id'] = stderr_input("Enter aws_access_key_id: ")
        aws_credentials['aws_secret_access_key'] = stderr_input("Enter aws_secret_access_key: ")

        with open(config_file, 'w') as file:
            json.dump(aws_credentials, file)

        exit(EXIT_OK)

    aws = AWSHConnector(config_file)

    if ls:
        print(aws.instances_string(), file=sys.stderr)
        exit(EXIT_FAILURE)

    if instance is None:
        print("Error: Missing argument 'INSTANCE'.")
        exit(EXIT_FAILURE)

    if key is None:
        if "AWSH_KEY" in os.environ:
            key = os.environ["AWSH_KEY"]
        else:
            print("ssh key not provided, please set AWSH_KEY environment variable or supply -i parameter.")
            exit(EXIT_FAILURE)

    ips = aws.get_ip(instance)

    if len(ips) == 0:
        print(f"{instance} does not exist!")
        print(aws.instances_string())
        exit(EXIT_FAILURE)

    if len(files) == 0:
        if len(ips) > 1:
            print("Error: cannot ssh with multiple ips. Please specify your instance.")
            exit(EXIT_FAILURE)
        else:
            enter_ssh(ips[0], key)
            exit(SSH_EXIT_OK)

    for file in files:
        copy_file(ips, key, file)

    if not copy:
        exec_script(ips, key, files[0])
        exit(EXIT_OK)


if __name__ == '__main__':
    main()
