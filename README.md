基于ansible api去自动扫描本地 or 远程主机的[GPU, CPU, DISK, MEMORY]信息并根据相关参数进行入CMDB库或本地保存

#### (warning) 
ansible version >= 2.4, process = 24;

#### 参数说明
````

-f 指定主机列表的文件, 一行一个ip地址:
									
-h 指定单台主机

--action (gpu, cpu, memory, disk)

#required 
--type (remote, local)

--uri api接口地址
````

#### 参数约定
```
--type 必须存在这个参数， 当为remote时，需要跟随 --uri api地址， 如果是local则会保存当前目录的一个txt文件

-f 和 -h 互斥 如果同时存在以 -f为准

--action 不写默认为采集所有
```

#### command:
```
1、 export LANG='en'

2、 ./main --help 
```


#### 单个主机及文件方式准备工作
```
1、如果你有一批主机需要做一些处理, 那么你应该在'list.txt'中进行增加, 格式以里面内容为准
2、然后将增加的那些机器单独生成一个文件，然后在你运行main.py的时候 --file指定那个文件，那么就ok了
3、当你有一台主机的时候 --host， 那么你需要将这个单台的主机和步骤1一样的操作，然后在指定--host ip
```


#### 参数详细说明
```
--file 可指定文件需要批量采集主机的一个列表文件，格式为每一行一个ip地址，ps: 如果list.txt文件中没有那个ip地址，那么需要在list.txt中加入

--host 可指定单台主机进行数据采集，如果--file和--host参数同时存在，--file优先级最大

--type(local|remote) 数据采集后的动作，可基于
                       本地模式(默认会保存当前目录命名为{gpu|cpu|disk|memory}.txt的文件，格式为json格式，用于cmdb api地址识别，
                       远程模式(当为远程模式时，conf.py配置文件中必须要有REQUEST_URL的api地址，或指定--uri的参数进行地址指定，会将采集后的结果发送到CMDBapi上)

--action(gpu|cpu|disk|memory) 指定需要采集的数据，当不指定action时，默认采集所有的数据

--parallel 当指定--file时生效，并行执行主机的数量，默认不指定时为每一次1台主机是采集

--load 指定保存到本地后生成的.txt的json数据，进行api 接口发送
```
