import ipaddress
import subprocess
import socket

import mongo
import pymongo
import random
import bson

import pprint


class Target:
    def __init__(self,user=None, password=None, IP=None, port=None):
        self.description="Some desc"
        if user is None:
            self.user=None
        else:
            self.user= user

        if password is None:
            self.password=None
        else:
            self.password= password
        
        if IP is None:
            self.IP=None
        else:
            self.IP= ipaddress.ip_address(IP)
        
        if port is None:
            self.port=None
        else:
            self.port= port

    def setUser(self,user):
        self.user=user

    def setPass(self,password):
        self.password=password

    def setIP(self,IP):
        self.IP= ipaddress.ip_address(IP)

    def setPort(self,port):
        self.port= port


class Context:
    def __init__(self,target=None):
        self.self_info="Server info"
        if target is None:
            self.target=None
        else:
            self.target= target
  
    def setTarget(self,target):
        self.target= target



ctx=None
target=None


def populateContext():
    global ctx
    global target
#    ctx=Context()
    if ctx is None:
        target=Target()
        target.setIP("10.10.10.11")
        target.setUser("None")
        target.setPass("None")
        target.setPort(27017)
        ctx=Context(target)

#@app.on_event("startup")
#async def startup_event():
def startup_event():
    print("Startup")
    populateContext()
    

  
    if ctx.target:
        if ctx.target:
            if ctx.target.user:
                print(ctx.target.user)



def _getConnectionStatus():
    global ctx
    res=None
    try:
        host = socket.gethostbyname(str(ctx.target.IP))
        res=socket.create_connection((host, ctx.target.port), 2)
        return True
    except:
        print(res)
        pass
    return False

def checkConnection():
    res=_getConnectionStatus()
    if res:
        print("Connection OK")
    else:
        print("Problem in Connection ")
    return res


def getAllSubscribersInfo():
    global ctx
    if(checkConnection() ):
        myclient = pymongo.MongoClient("mongodb://" + str(ctx.target.IP) + ":" + str(ctx.target.port) + "/")
        mydb = myclient["open5gs"]
        mycol = mydb["subscribers"]
        subs_list = []
        for x in mycol.find():
            subs_list.append(x)
        
        pprint.pprint(subs_list)
    else:
        print("Get All subscribers failed")

def getAllSubscribersIMSIs():
    global ctx
    
    if(checkConnection() ):
        myclient = pymongo.MongoClient("mongodb://" + str(ctx.target.IP) + ":" + str(ctx.target.port) + "/")
        mydb = myclient["open5gs"]
        mycol = mydb["subscribers"]
        subs_list = []
        for x in mycol.find():
            subs_list.append(x["imsi"])
        
        return subs_list
    else:
        print("Get All subscribers failed")
        return None


def getSubscriberInfo(imsi:None):

    global ctx
    if(checkConnection() ):
        myclient = pymongo.MongoClient("mongodb://" + str(ctx.target.IP) + ":" + str(ctx.target.port) + "/")
        mydb = myclient["open5gs"]
        mycol = mydb["subscribers"]
        myquery = { "imsi": str(imsi)}
        #myquery = { "network_access_mode": 2}
        mydoc = mycol.find(myquery)
        
        mydoc_as_list=list(mydoc)
        num_res=len(mydoc_as_list)
        if num_res:
            print(num_res)
            for i in range(num_res):
                print(mydoc_as_list[i])
        else:
            print("IMSI not found")
    else:
        print("Get Subscriber failed")
    
    
def AddSubscriber(sub_data):
    global ctx
    if(checkConnection() ):
        myclient = pymongo.MongoClient("mongodb://" + str(ctx.target.IP) + ":" + str(ctx.target.port) + "/")

        mydb = myclient["open5gs"]
        mycol = mydb["subscribers"]
        
        x = mycol.insert_one(sub_data)
        print("Added subscriber with Inserted ID : " + str(x.inserted_id))
        return x.inserted_id
    else:
        print("Get Subscriber failed")


def UpdateSubscriber(imsi,sub_data):
    global ctx
    if(checkConnection() ):
        myclient = pymongo.MongoClient("mongodb://" + str(ctx.target.IP) + ":" + str(ctx.target.port) + "/")

        mydb = myclient["open5gs"]
        mycol = mydb["subscribers"]
        
        newvalues = { "$set": sub_data }
        myquery = { "imsi": str(imsi)}
        x = mycol.update_one(myquery, newvalues)
        print(x)
        
    else:
        print("Get Subscriber failed")


def main():
    print("Hello World!")
    startup_event()
    #dummyTest()
    '''
    getAllSubscribersInfo()
    res=getAllSubscribersIMSIs()
    if res:
        print(res)
    else:
        pprint.pprint("Oops")
    '''
    #getSubscriberInfo('001010000034729')
    #AddSubscriber(new_sub)
    new_sub["security"]["amf"]=8080
    new_sub["pdn"][0]["qos"]["qci"]=10
    UpdateSubscriber("001010000034799",new_sub)
    print(new_sub)


new_sub_pdn_qos={
			"qci": 9,
			"arp": {
				"priority_level": 8,
				"pre_emption_vulnerability": 1,
				"pre_emption_capability": 1
			}
		}

new_sub_pdn=[{
		"apn": "internet",
		"pcc_rule": [],
		"ambr": {
			"downlink": 1024000,
			"uplink": 1024000
		},
		"qos": new_sub_pdn_qos,
		"type": 2
	}]

new_sub_security={
		"k": "600A659CE19D6E862F29AEB168DE7164",
		"amf": "9001",
		"op": "None",
		"opc": "B053FADD67FE3B0B2D2D8FF31FCF81B0"
	}
new_sub={
	"imsi": "001010000034799",
	"pdn": new_sub_pdn,
	"ambr": {
		"downlink": 1024000,
		"uplink": 1024000
	},
	"subscribed_rau_tau_timer": 12,
	"network_access_mode": 2,
	"subscriber_status": 0,
	"access_restriction_data": 32,
	"security": new_sub_security,
}


if __name__ == "__main__":
    main()
