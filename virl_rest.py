import requests
import collections
import json
import xml.dom.minidom
import xml.etree.ElementTree
from bs4 import BeautifulSoup


USERNAME="Unetwork"
PASSWORD="cisco"
HOST="10.60.21.23"

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

def get_sim_name():

    url='http://'+HOST+':19399/simengine/rest/list'
    #print '++++++++ REQUEST GET ++++++++'
    #print url
    #print '------------------------------'

    r = requests.get(url, verify=False, auth=(USERNAME, PASSWORD))
    #print r.status_code

    #print '++++++++ RESPONSE GET ++++++++'
    #pprint (convert(r.json()))
    #print '-------------------------------'
    #print convert(r.json())
    return json.dumps(convert(r.json()))

def select_sim_name():
    i=1
    data=get_sim_name()
    json_data=json.loads(data)
    tab=[]

    print "-"*40
    print "   Yangters' software validation"
    print "-"*40
    for simul in json_data['simulations']:
        tab.append(simul)
        print str(i)+" - "+simul
        i=i+1
    print"""

select your simulation
    """
    sel=int(input())

    return tab[sel-1]

def get_drafts_data(sim):

    url='http://'+HOST+':19399/simengine/rest/interfaces/'+sim
    print '++++++++ REQUEST GET ++++++++'
    print url
    print '------------------------------'

    r = requests.get(url, verify=False, auth=(USERNAME, PASSWORD))
    print r.status_code

    #print '++++++++ RESPONSE GET ++++++++'
    #pprint (convert(r.json()))
    #print '-------------------------------'

    return convert(r.json())

def get_args_sim_data() :

    url='http://'+HOST+':19399/roster/rest/'
    print '++++++++ REQUEST GET ++++++++'
    print url
    print '------------------------------'

    r = requests.get(url, verify=False, auth=(USERNAME, PASSWORD))
    print r.status_code

    #print '++++++++ RESPONSE GET ++++++++'
    #pprint (convert(r.json()))
    #print '-------------------------------'
    return convert(r.json())

def get_node_location(sim):

    tab=[]
    url='http://'+HOST+':19399/simengine/rest/export/'+sim+'?updated=1'
    print '++++++++ REQUEST GET ++++++++'
    print url
    print '------------------------------'

    r = requests.get(url, verify=False, auth=(USERNAME, PASSWORD))
    result = xml.dom.minidom.parseString(r.text)
    print r.status_code

    xml_d=convert((result.toprettyxml()))
    cmp=xml_d.count("node ")
    xml_data=BeautifulSoup(xml_d)


    for i in range(0, cmp):
        loc=xml_data.topology.findAll("node")[i]["location"].split(",", 2)
        tab.append([xml_data.topology.findAll("node")[i]["name"], loc[0],loc[1]]
        )

    value_max=max(tab)


    for j in range(0, len(tab)):
        #tab[j][2]=float(tab[j][2])/(float(value_max[1])+1)
        tab[j][2]=float(tab[j][2])/(float(400))
        before_dec, after_dec = str(tab[j][2]).split('.')
        tab[j][2]=float('.'.join((before_dec, after_dec[0:2])))

        tab[j][1]=float(tab[j][1])/(float(950))
        #tab[j][1]=float(tab[j][1])/(float(value_max[1])+1)
        before_dec, after_dec = str(tab[j][1]).split('.')
        tab[j][1]=float('.'.join((before_dec, after_dec[0:2])))

    return tab

def build_data(sim):

    data = []
    Interfaces = []
    NEC = {}


    node=get_args_sim_data()
    drafts=get_drafts_data(sim)

    for ob in node:
        if ob.find(sim) != -1 :
            if ob.find('~') == -1 and ob.count(".") < 4 :
                NodeName=node[ob]['NodeName']
                managementIP=node[ob]['managementIP']
                PortConsole=node[ob]['PortConsole']
                managementProtocol=node[ob]['managementProtocol']
                NodeSubtype=node[ob]['NodeSubtype']

                tav=drafts[sim]
                for dr in tav:
                    if dr == NodeName :
                        NEC =drafts[sim][NodeName]
                        for int in NEC :
                            sta=drafts[sim][NodeName][int]
                            name=sta['name']
                            network=sta['network']
                            link_state=str(sta['link-state'])
                            ip_address=str(sta['ip-address'])

                            Interfaces.append({'name': name, 'network': network,'link-state' : link_state, 'ip-address' : ip_address })
                            if int[0] == "m" :
                                break

                data.append({'NodeSubtype': NodeSubtype,'NodeName': NodeName, 'managementIP': managementIP, 'PortConsole': PortConsole, 'managementProtocol': managementProtocol, 'Interface': Interfaces})
                Interfaces=[]
    json_data = json.dumps(data)

    return json_data
