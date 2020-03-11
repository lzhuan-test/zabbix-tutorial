import requests
import json
import re

def atoi(text):
    print text
    match = re.search('\d+', text)
    if match:
        return int(match.group())
    else:
        return 0

def get_auth():
	headers = {
		"Content-Type": "application/json"
	}
	payload = {
		"jsonrpc" : "2.0",
		"method" : "user.login",
		"params": {
			'user': 'Admin',
			'password':'zabbix',
		},
		"auth" : None,
		"id" : 0
	}
	res = requests.post(url, data=json.dumps(payload), headers=headers)
	res = res.json()	
	return res['result']

def get_hostgroupid(name):
	headers = {
		"Content-Type": "application/json"
	}
	payload = {
		"jsonrpc" : "2.0",
		"method" : "hostgroup.get",
		"params": {
			"output": "groupid",
			"filter": {
				"name": name
			}
		},
		"auth" : auth,
		"id" : 0
	}
	res = requests.post(url, data=json.dumps(payload), headers=headers)
	res = res.json()
	return res['result'][0]['groupid']

def get_hostids(hostgroupid):
    ret = []
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc" : "2.0",
        "method" : "host.get",
        "params": {
            "output": ["name", "hostid"],
            "groupids": hostgroupid,
            "selectInterfaces": [
                "interfaceid",
                "ip"
            ]
        },
        "auth" : auth,
        "id" : 0
    }
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    res = res.json()['result']
    res.sort(key=lambda x:atoi(x['name']))
    for ele in res:
        ret.append(ele['hostid'])
    return ret

def get_itemid(hostid, key):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc" : "2.0",
        "method":"item.get",
        "params":{
            "output": "itemid",
            "hostids": hostid,
            "search": {
                "key_": key
            }
        },
        "auth" : auth,
        "id" : 0
    }
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    res = res.json()
    return res['result'][0]['itemid']

def create_graph(name, items):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc" : "2.0",
        "method": "graph.create",
        "params": {
            "name": name,
            "width": 900,
            "height": 200,
            "gitems": items
        },
        "auth" : auth,
        "id" : 0
    }
    requests.post(url, data=json.dumps(payload), headers=headers)

def create_custom_graph(hostgroupname, key):
    colors = ["1A7C11", "F63100", "2774A4", "A54F10", "FC6EA3", "6C59DC", 
        "AC8C14", "611F27", "F230E0", "5CCD18", "BB2A02", "5A2B57", 
        "89ABF8", "7EC25C", "274482", "2B5429", "8048B4", "FD5434", 
        "790E1F", "87AC4D", "E89DF4", "1A7C11", "F63100", "2774A4", 
        "A54F10", "FC6EA3", "6C59DC", "AC8C14", "611F27", "F230E0"]
    hostgroupid = get_hostgroupid(hostgroupname)
    hostids = get_hostids(hostgroupid)
    i = 0
    items = []
    for hostid in hostids:
        itemid = get_itemid(hostid, key)
        color = colors[i]
        item = Item(itemid, color, i)
        items.append(item.__dict__)
        i = i + 1
    create_graph(hostgroupname + " " + key, items)

class Item:
    def __init__(self, itemid, color, sortorder):
        self.itemid = itemid
        self.color = color
        self.sortorder = sortorder

url = "http://10.211.55.42/zabbix/api_jsonrpc.php"
auth = get_auth()
create_custom_graph("CentOS", "system.cpu.util[,idle]")

