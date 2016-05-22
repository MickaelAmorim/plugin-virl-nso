import json

from ncs_cli import *
from virl_rest import *
from flask import Flask, render_template, request,make_response,current_app, redirect
import time

app = Flask(__name__)
statusdata={}

def jsonstatus_init():

    steps=['virl_conn','virl_data','ncs_conn','ncs_push','ncs_vali']
    for step in steps :
        statusdata[step]={'description':'','status':'','statmesg':''}

def jsonstatus(step,status,statmesg=0,desc=0):
    if desc :
        statusdata[step]['description']=desc
    if statmesg :
        statusdata[step]['statmesg']=statmesg
    statusdata[step]['status']=status

    return statusdata

def json_dump_outfile(filePath):
    with open(filePath, 'w') as outfile:
        json.dump(statusdata, outfile)

def virl_conn():
    jsonstatus('virl_conn','false', 'active')
    json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
    url='http://'+HOST+':19399/simengine/rest/list'
    r = requests.get(url, verify=False, auth=(USERNAME, PASSWORD))

    if r.status_code != 200:
        return False

    return True

def do_test_ncs_connection(job,host,conn):
    conn.execute("show devices device state")


def do_ncs_validation(job,host,conn):
    conn.execute("configure")
    conn.execute("set services svcvalidator complextopologyvalidator plugins l3connectivity source device csr1000v-1 interface 2 ip-address 10.0.0.5")
    conn.execute("set services svcvalidator complextopologyvalidator plugins l3connectivity destination device csr1000v-5 interface 2 ip-address 10.0.0.18")
    conn.execute("commit")



@app.route('/.api/ncs/validation', methods=['GET'])
def hello():

    #nso = request.form['NSO']
    #sim = request.form['simulation']
    #reset = request.form['reset-ncs']

    reset=raw_input("Reset NCS database ? [y/n default n] : ")
    try:
        if reset == 'y' :
            clear()
    except:
      pass


    jsonstatus_init()

    sim=select_sim_name()
    #test virl connection

    if virl_conn() == True :
        jsonstatus('virl_conn','true', 'active')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
        time.sleep(5)
    else :
        if virl_conn() == False :
            jsonstatus('virl_conn','true', 'visited', 'cannot connect to VIRL')
            json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
            time.sleep(5)

    jsonstatus('virl_conn','true', 'visited')
    json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")



    #sim="hackitvi-yangsters@complextopologyv2-gmD7p7"
    #sim="My_Topologies@topology-GSE4xE"
    # test build virl data
    try :
        jsonstatus('virl_data','true','active')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
        time.sleep(5)
        data=build_data(sim)
        jsonstatus('virl_data','true','visited')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
    except Exception as e :
        print "*"*60
        print e
        print "*"*60
        time.sleep(5)
        jsonstatus('virl_data','true', 'visited', 'problem to recup virl values')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")

    #test ncs connection
    try:
        jsonstatus('ncs_conn','true','active')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
        time.sleep(5)
        result=start(account, host, bind(do_test_ncs_connection))

        jsonstatus('ncs_conn','true', 'visited')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")

    except Exception as e :
        jsonstatus('ncs_conn','true', 'visited', 'cannot connect to NCS')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")

    #test push and to ncs
    try :
        jsonstatus('ncs_push','true','active')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
        upload(json.loads(convert(build_data(sim))),get_node_location(sim))
        jsonstatus('ncs_push','true','visited')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
    except Exception as e :
        jsonstatus('ncs_push','true', 'visited', 'error to push data')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")


    # ncs validation
    try :
        jsonstatus('ncs_vali','true' ,'active')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
        time.sleep(5)
        result=start(account, host, bind(do_ncs_validation))

        jsonstatus('ncs_vali','true', 'visited','ok')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
    except Exception as e :

        jsonstatus('ncs_vali','false', 'visited', 'ok')
        json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")

    print (statusdata)
    time.sleep(5)
    jsonstatus_init()
    json_dump_outfile("/var/www/ncs/startbootstrap-shop-item/data/data.json")
    # #Reset demo

    #
    # sim=virl.select_sim_name()
    # ncs.upload(json.loads(virl.convert(virl.build_data(sim))),virl.get_node_location(sim))


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8001)