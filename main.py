#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
import json
import requests
import time
import argparse
import re
import sys
from api import AnsibleBase
import logging
import conf

logger = logging.getLogger('ansible')

logger.setLevel(logging.INFO)

debugfile = logging.FileHandler('debug.log')

formatter = logging.Formatter('%(asctime)s - %(name)s  - %(message)s')

debugfile.setFormatter(formatter)

logger.addHandler(debugfile)


class AutoCollection(object):

    def __init__(self, run_type="remote", files=None, host=None, uri=None, action=None, parallel=None, required=True):

        self.__action = (
            ("gpu", self.get_gpu, "nvidia-smi  -a  | grep  -E 'GPU (.*?):(.*?):.(.*?)' -A 70", "0"),
            ("cpu", self.get_cpu, 'lscpu', "1"),
            ("disk", self.get_disk, "lsblk -P -d -o FSTYPE,VENDOR,MODEL,SERIAL,SIZE,ROTA  | sed $'s/\"//g'", "2"),
            ("memory", self.get_memory, 'dmidecode -t 17', "3")
        )

        self.run_action = action
        self.files = files
        self.type = run_type
        self.api_uri = conf.PUSH_API if conf.PUSH_API else uri
        self.host_list = []
        self.count = 0
        self.parallel = int(parallel) if parallel else 1

        self.host = self.file_parse() if files else [host]
        if required:
            self.argument_form_valid()
        self.ansible = AnsibleBase()

    @staticmethod
    def auth():

        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            "username": conf.AUTH_USER,
            "password": conf.AUTH_PASS
        }
        try:
            token = json.loads(requests.post(conf.AUTH_API, data=json.dumps(data), headers=headers).text)
        except Exception as e:
            print('get token error')
            sys.exit(1)

        headers["Authorization"] =  token['token']

        return headers

    def load_request(self, files):
        with open(files, "r") as f:
            for i in f.readlines():
                self.remote_request(json.loads(i.strip('\n')))

    def argument_form_valid(self):

        if self.type not in ("remote", 'local'):
            raise ValueError("Please enter valid parameters (remote or local)")

        elif self.type == 'remote' and self.api_uri is None:
            raise TypeError("If you choose remote, then you must have remote API interface argument!")

        elif self.files is None and self.host is None:
            raise TypeError("Please enter a valid IP address or host list file name")


    def formst_sysout(self, ip, msg, state, method, color, command=None):

        background = {
            0: 32,
            1: 33,
            2: 31
         }

        status = {
            "ip": ip if ip else None,
            "msg": msg,
            "state": state,
            "method": method,
        }

        print("\033[1;%sm%s\033[0m" % (background[color], json.dumps(status, indent=4)))

    def custom_format(self, response,  msg, state,color):
        task_id = response['task_id'] if isinstance(response, dict)  else response[0]['task_id']
        ip = response['ip']  if isinstance(response, dict) else response[0]['ip']

        method = ''
        for i in self.__action:
            if task_id in i:
                method = i[0]
                break

        self.formst_sysout(ip=ip, msg=msg, state=state, method=method, color=color)

    def ansible_format(self, response):

        errir_list = [response['failed'], response['unreachable']]
        single = False 
        for failed_list in errir_list:
            if failed_list:
                for i in failed_list:
                    self.formst_sysout(i, failed_list[i]['msg'], False, 'ansible', 2)

        
        if not response['success']:
            self.formst_sysout(ip=None, msg="command not found", state=False, method='ansible', color=1)


    def run(self):
        return self.run_complete()

    def remote_request(self, data):
        headers = self.auth()
        try:
            html = json.loads(requests.post(url=self.api_uri, data=json.dumps(data), headers=headers, timeout=conf.REQUEST_TIMEOUT).text)
        except Exception as e:
            logger.error("push to api address error: %s" % e)
            print(e)
            self.custom_format(data, "push to api error", False, 2)
        else:
            self.custom_format(data, "push to api success", True, 0)

    def iterable_data(self, data, method, task_id, name=None):
        for i in data['success']:
            try:
                result = data['success'][i]['stdout_lines']
            except Exception as e:
                logger.error("get command result error:%s" % e)
                continue

            arrays = [{"task_id": task_id , "ip": i}]
            success_filter_data = method(result, arrays)

            if self.type == 'local':
                self.local_save(name=name, data=success_filter_data)
            else:
                self.remote_request(data=success_filter_data)

    def local_save(self, name, data):
        with open('%s.txt' % name, 'a+') as f:
            f.write(json.dumps(data) + '\n')
        self.custom_format(data, color=0, msg="success save to %s.txt" % name, state=True)

    def run_complete(self):
        for name, method, command, task_id in self.__action:
            if self.run_action and self.run_action != name:
                if self.count >= 1:
                    break
                continue
            else:
                self.count += 1

            self.set_single(method.__name__)
            self.all_action(command, method, task_id, name)

    def all_action(self, command, method, task_id, name):
        for i in self.host:
            print("\033[1;32m run => %s\033[0m" % i )
            response = self.ad_hoc(hosts=i, module="shell", command=command)
            self.iterable_data(response, method, task_id=task_id, name=name)

    def file_parse(self):
        hosts = []
        with open(self.files, 'r') as files:
            for i in files.readlines():
                if len(hosts) == self.parallel:
                    self.host_list.append(hosts)
                    hosts = []
                ip = i.strip('\n').strip()
                if ip:
                    hosts.append(ip)
        if hosts:
            self.host_list.append(hosts)

        #return list(set(self.host_list))
        return self.host_list

    def ad_hoc(self, hosts, module, command, *args, **kwargs):
        response = self.ansible.run(host_list=hosts, moduls=module, _args=command)

        self.ansible_format(response)
        return response

    def play_book(self, yml, **kwargs):
        return self.ansible.playbook(yml=yml)

    def set_single(self, name):
        setattr(self, "%s_list" % name, [])

    def get_cpu(self, result, data):
        data = data[0]
        numa_node_format = ''
        count = 0
        for i in result:
            key, value = i.strip().split(':')
            for k, v in conf.CPU_FIELDS.items():
                if key.strip() == k:
                    data[v.strip()] = value.strip()
                    break
            if key.strip().startswith('NUMA') and key.strip().endswith('CPU(s)'):
                numa_node_format += '%s:%s ' %  (str(count),value.strip())
                count += 1

        data['sockets'] = int(data['sockets'])
        data['numa_node_cpus'] = numa_node_format
        return data

    def get_memory(self, result, data):
        temp = {}
        for i in result:
            value = i.strip().split(':')
            if len(value) != 2:
                continue
            for k, v in conf.MEMORY_FIELDS.items():
                if value[0] == k:
                    temp[v] = value[1].strip()
                    break
            if len(temp) == 5:
                data.append(temp)
                temp = {}
        return data

    def get_gpu(self, result, data):
        temp = {}
        for i in result:
            if re.search('GPU [0-9]', i.strip()):
                temp['pci'] = i.strip()
            value = i.strip().split(':')
            if len(value) != 2:
                continue
            for k,v in conf.GPU_FIELDS.items():
                if value[0].strip() == k:
                    temp[v] = value[1].strip()
                    break
            if len(temp) == 6:
                data.append(temp)
                temp = {}
        return data

    def get_disk(self, result, data):
        temp = {}
        for i in result:
            split = i.split()
            count = 3
            while True:
                y = split[3]
                if 'SERIAL' not in y:
                    split[2] += ' ' +  split.pop(count)
                else:
                    break
            for s in split:
                t = s.split('=')
                for k, v in conf.DISK_FIELDS.items():
                    if t[0] == k:
                        temp[v] = t[1].strip() or None
                        break
                if len(temp) == 6:
                    data.append(temp)
                    temp = {}
        return data


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(usage='-h --help get help')
        parser.add_argument( '-f', '--file',  help = 'Specify the file in the host list, one IP per line')
        parser.add_argument( '--host',help = 'When specifying host ip, --host and --file exist simultaneously, file priority is higher.')
        parser.add_argument( '--type',help = 'Execution action (local, remote), local will save a local file, remote must exist --uri', choices=['local', 'remote'])
        parser.add_argument( '--action',help = 'Get the host information type (gpu, cpu, memory, disk), and collect all by default when action is not specified', choices=['gpu', 'cpu', 'disk' ,'memory'])
        parser.add_argument( '--uri',help = '--type must exist when it is remote, specifying which API interface to send to')
        parser.add_argument( '--parallel',help = 'This parameter is valid when -- file is specified,How many host colleagues to execute commands, the default is one')
        parser.add_argument( '--load',help = 'Send requests to API addresses based on locally saved files')
        args = parser.parse_args()

        if len(sys.argv) == 1:
            print('usage: -h --help get help')
            sys.exit(1)

    except Exception as e:
        print('error',e)

    if args.load:
        complete = AutoCollection(required=False)
        complete.load_request(args.load)
    else:
        transfer = AutoCollection(action=args.action, run_type=args.type,files=args.file, host=args.host, uri=args.uri, parallel=args.parallel)
        transfer.run()
