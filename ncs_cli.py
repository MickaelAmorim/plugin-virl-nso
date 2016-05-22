from Exscript.util.decorator import bind
from Exscript.util.start import start
from Exscript import Host, Account


iosmapping ={'CSR1000v':'cisco-ios','IOSv' : 'cisco-ios'}
portmapping={'telnet':'23','ssh':'22'}
account= Account('admin','admin')
host="ssh://10.60.21.192:2024"
#host="ssh://10.148.24.73:2024"

def clear():
    def clearall(job,host,conn):
        conn.execute('configure')
        conn.execute('delete webui data-stores')
        conn.execute('delete topology')
        conn.execute('delete devices device')
        conn.execute('commit')

    start(account,host,clearall)

def upload(jsondata,coorddata):
    def do_addnode(job,host,conn,node):

        conn.execute('configure')
        conn.execute('set devices authgroups group auth-cisco default-map remote-name cisco remote-password cisco remote-secondary-password cisco')
        conn.execute('commit')
        conn.execute('set devices device '+node['NodeName']+' address '+node['managementIP']+' port '+portmapping[node['managementProtocol']]+' authgroup auth-cisco device-type cli ned-id '+iosmapping[node["NodeSubtype"]]+' protocol '+node['managementProtocol'] )
        conn.execute('commit')
        conn.execute('set devices device '+node['NodeName']+' state admin-state unlocked ')
        conn.execute('commit')
        conn.execute('request devices device '+node['NodeName']+' sync-from')

    def get_int_info(device,connex):
        for node in jsondata:
            if node["NodeName"]==device :
                for int in node["Interface"]:
                        if(connex==int['network']):
                            return int['name'], int['ip-address']

    def do_addconnection(job,host,conn,node1,node2,interface):
            info1=get_int_info(node1,interface)
            info2=get_int_info(node2,interface)
            conn.execute('configure')
            try:
                if info1[1]=="None":
                    conn.execute('set topology connection '+node1+"_"+node2+' endpoint-1 device '+node1+" interface "+info1[0])
                    conn.execute('set topology connection '+node1+"_"+node2+' endpoint-2 device '+node2+" interface "+info2[0])
                else:
                    conn.execute('set topology connection '+node1+"_"+node2+' endpoint-1 device '+node1+" interface "+info1[0]+ " ip-address "+info2[1])
                    conn.execute('set topology connection '+node1+"_"+node2+' endpoint-2 device '+node2+" interface "+info2[0]+ " ip-address "+info2[1])

                conn.execute('commit')
            except Exception as e:
                print e
                print info1,info2

    def do_addicons(job,host,conn,node,coordx,coordy):
        conn.execute("configure")
        conn.execute('set webui icons device '+node['NodeName']+' disabled large icon cisco-disabled')
        conn.execute('set webui icons device '+node['NodeName']+' enabled large icon cisco-enabled')
        conn.execute('set webui data-stores static-map device '+node['NodeName']+' coord x '+str(coordx)+' y '+str(coordy)+'')
        conn.execute('commit')

    for node in jsondata :
        for i in range (0,len(coorddata)):
            if coorddata[i][0]==node['NodeName']:
                coordx=coorddata[i][1]
                coordy=coorddata[i][2]
                break

        start(account, host, bind(do_addnode,node))
        start(account, host, bind(do_addicons,node,coordx,coordy))

        for interfaces in node['Interface']:
            split=interfaces['network'].split("-to-",2)
            if len(split) ==2:
                start(account, host, bind(do_addconnection,split[0],split[1],interfaces['network']))


