import boto3
import fnmatch
import json
import os
from awsh.exit_statuses import EXIT_FAILURE


class AWSHConnector:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            print("Please set your aws credentials with awsh --configure")
            exit(EXIT_FAILURE)

        with open(config_file) as file:
            aws_credentials = json.load(file)

        self.session = boto3.session.Session(**aws_credentials)

        self.ec2_resource = self.session.resource(service_name="ec2")
        self.ec2_client = self.session.client(service_name="ec2")

        self._generate_name_mappings()

    def _generate_name_mappings(self):
        instances = self.ec2_client.describe_instances()

        reservations = instances['Reservations']

        instance_map = []
        idx = 0
        for res in reservations:
            instances = res['Instances']
            for inst in instances:
                data = {}
                if 'PublicIpAddress' not in inst:
                    continue
                data['ip'] = inst['PublicIpAddress']
                tags = inst['Tags']
                inst_name: str = None
                for tag in tags:
                    if tag['Key'] == 'Name':
                        inst_name = tag['Value']

                if inst_name is None or len(inst_name) == 0:
                    inst_name = inst['InstanceId']

                data['name'] = inst_name
                data['idx'] = idx
                data['type'] = inst['InstanceType']
                data['inst_id'] = inst['InstanceId']

                instance_map.append(data)
                idx += 1

        self.instance_map = instance_map

    def get_ip_from_name(self, name):
        instance_ips = [inst['ip'] for inst in self.instance_map if fnmatch.fnmatch(inst['name'], name)]

        return instance_ips

    def get_ip_from_index(self, idx):
        return [self.instance_map[idx]['ip']]

    def get_ip(self, instance: str):
        if instance.isnumeric():
            return self.get_ip_from_index(int(instance))
        else:
            return self.get_ip_from_name(instance)

    def instances_string(self):
        widest_name = max([len(inst['name']) for inst in self.instance_map])
        widest_ip = max([len(inst['ip']) for inst in self.instance_map])

        strings = []
        strings.append(f"| {{:<3}} | {{:<{widest_name}}} | {{:<{widest_ip}}} |".format('idx', 'Name', 'ip'))
        strings.append(f"| {{:<3}} | {{:<{widest_name}}} | {{:<{widest_ip}}} |".format('', '', ''))
        for inst in self.instance_map:
            strings.append(f"| {{:<3}} | {{:<{widest_name}}} | {{:<{widest_ip}}} |".format(inst['idx'], inst['name'], inst['ip']))

        return '\n'.join(strings)
