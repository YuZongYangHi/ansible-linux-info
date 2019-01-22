# -*- coding: utf-8 -*- 


# Push the result to the API address, provided that token is already carried in the header header
PUSH_API = ''


# If you are remotely to the api, the authentication address you need to fill in here should return token
AUTH_API = ''

# auth user
AUTH_USER = ''

# auth password
AUTH_PASS = ''

#ansible api fork process number
ANSIBLE_FORK = 25 

#request timeout time
REQUEST_TIMEOUT = 10 

#cpu,format
CPU_FIELDS  = {
	'Architecture': 'architecture',
	'CPU op-mode(s)': 'cpu_op_mode',
	'Byte Order': 'byte_order',
	'CPU(s)': 'cpus',
	'On-line CPU(s) list': 'on_line_cpu_list',
	'Thread(s) per core': 'threads_per_core',
	'Core(s) per socket': 'cores_per_socket',
	'Socket(s)': 'sockets',
	'NUMA node(s)': 'numa_nodes',
	'Vendor ID': 'vendor_id',
	'CPU family': 'cpu_family',
	'Model': 'model',
	'Model name': 'model_name',
	'Stepping': 'stepping',
	'CPU MHz': 'cpu_mhz',
	'CPU max MHz': 'cpu_max_mhz',
	'CPU min MHz': 'cpu_min_mhz',
	'BogoMIPS': 'bogomips',
	'Virtualization': 'virtualization',
	'L1d cache': 'l1d_cache',
	'L1i cache': 'l1i_cache',
	'L2 cache': 'l2_cache',
	'L3 cache': 'l3_cache',
	'Flags': 'flags',
	'NUMA node' :'numa_node_cpus',
	'name': ''
}


GPU_FIELDS = {
	"Product Name": "product_name",
	"Product Brand": "product_brand",
	"GPU UUID": "uuid",
	"Serial Number": "sn",
	"Compute Mode": "compute_mode",
	"pci": "pci"
	}


MEMORY_FIELDS = {
	"Serial Number": "serial_id",
	"Type": "type",
	"Size": "size",
	"Manufacturer": "vendor",
	"Speed": "speed",
	}


DISK_FIELDS = {
	"FSTYPE": "fs_type",
	"VENDOR": "vendor",
	"MODEL": "model",
	"SERIAL": "sn",
	"SIZE": 'size',
	"ROTA": "type"
	}
