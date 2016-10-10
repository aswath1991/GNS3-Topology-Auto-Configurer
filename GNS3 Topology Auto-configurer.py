import pip
import pexpect
import importlib
import sys
import csv, sqlite3
import os
import collections
from collections import defaultdict
from netmiko import *
import Tkinter as tk
from Tkinter import *
import time
import threading

deviceIPMap = {}
deviceIntMap = {}
deviceHostMap = {}
deviceUserMap = {}
devicePassMap = {}
deviceSecretMap = {}
deviceDomainMap = {}
deviceHostReverseMap = {}
interfaceChangeTable = defaultdict(list)
interfaceIPtable= defaultdict(list)

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        self.master.geometry(self._geom)
        self._geom=geom
        
def parseConfigs():
    global deviceIPMap
    global deviceIntMap
    global deviceHostMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceDomainMap
    global deviceHostReverseMap
    global interfaceChangeTable
    global interfaceIPtable
    
    if(os.path.isfile("Master.csv")):
        try:
            tableData = csv.DictReader(open('Master.csv','r'))
            for i in tableData:
                deviceIPMap[i['Default Device Name']] = i['IP address']
                deviceIntMap[i['Default Device Name']] = i['Management Interface']
                deviceHostMap[i['Default Device Name']] = i['Hostname']
                deviceUserMap[i['Default Device Name']] = i['Username']
                devicePassMap[i['Default Device Name']] = i['Password']
                deviceSecretMap[i['Default Device Name']] = i['Secret']
                deviceDomainMap[i['Default Device Name']] = i['Domain name']
                deviceHostReverseMap[i['Hostname']] = i['Default Device Name']
            if(os.path.isfile("Slave.csv")):
                intChangeData = csv.DictReader(open('Slave.csv','r'))
                for i in intChangeData:
                    if i['Hostname'] in deviceHostReverseMap.keys():
                        interfaceChangeTable[i['Hostname']].append({ str("interface " + i['Interface']) : str("ip address " + i['IP'] + " " + i['Subnet']) })
            else:
                print ("Slave.csv does NOT EXIST")
                return False
        except:
            return False

    else:
        print ("Master.csv does NOT EXIST")
        return False
    return True

def setupSSH():
    '''
    global deviceIPMap
    bigBuff = ''
    for k,v in deviceIPMap.items():
        # Telnet configuration for SSH
        child = winspawn('telnet ' + v)
        child.expect ('Username: ')
        child.sendline (deviceUserMap[k])
        child.expect ('Password: ')
        child.sendline (devicePassMap[k])
        child.expect (k + '>')
        bigBuff += (k + " : SSH Configuration Started; Please wait")
        text_box.config(text=bigBuff)
        child.sendline ('enable')
        child.expect ('Password: ')
        child.sendline (deviceSecretMap[k])
        child.expect (k + '#')
        child.sendline ('configure terminal')
        child.expect (k + '(config)#')
        child.sendline ('ip domain-name ' + deviceDomainMap[k])
        child.expect (k + '(config)#')
        child.sendline ('crypto key generate rsa')
        child.expect ('How many bits in the modulus [512]: ')
        child.sendline ('1024')
        child.expect (k + '(config)#')
        child.sendline ('exit')
        child.expect (k + '#')
        child.sendline ('exit')
        bigBuff += (k + " : SSH Configuration Completed;")
        text_box.config(text=bigBuff)

    return bigBuff
    '''
    
def testSSH():
    global deviceIPMap
    global deviceIntMap
    global deviceHostMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceDomainMap
    global deviceHostReverseMap
    global interfaceChangeTable
    global interfaceIPtable
    global text_box

    bigBuff = ''
    text_box.delete(0,END)
    text_box.insert(tk.END, "Testing if all the devices are reachable and if SSH is enabled on them (Please wait)")
    text_box.insert(tk.END, "\n")
    
    for k,v in deviceIPMap.items():
        try:
            t = threading.currentThread()
            if getattr(t, "do_run", True):
                cisco_asa = {
                    'device_type': 'cisco_asa',
                    'ip': v,
                    'username': deviceUserMap[k],
                    'password': devicePassMap[k],
                    'secret': deviceSecretMap[k],
                    'verbose': False,
                    }
                net_connect = ConnectHandler(**cisco_asa)
                out = net_connect.find_prompt()
                if getattr(t, "do_run", True):
                    smallBuff = str(out + " : Test passed. Device is reachable and SSH is enabled")
                    text_box.insert(tk.END,smallBuff)
                    text_box.insert(tk.END, "\n")
        except:
            text_box.insert(tk.END, "Test failed on Device: " + str(deviceHostMap[k]) + "; Please check if this device is reachable and if SSH is enabled in it.")
            text_box.insert(tk.END, "\n")
    if getattr(t, "do_run", True):
        text_box.insert(tk.END, "--- Event has completed ---")
        text_box.insert(tk.END, "\n")
            
            
def configureInterfaces():
    global deviceIPMap
    global deviceIntMap
    global deviceHostMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceDomainMap
    global deviceHostReverseMap
    global interfaceChangeTable
    global interfaceIPtable
    global text_box

    bigBuff = ''
    text_box.delete(0,END)
    text_box.insert(tk.END, "Configuring all the interfaces on all routers: (Please wait)")
    text_box.insert(tk.END, "\n")
    
    for k,v in deviceIPMap.items():
        try:
            if(deviceHostMap[k] in interfaceChangeTable.keys()):
                t = threading.currentThread()
                if getattr(t, "do_run", True):
                    cisco_asa = {
                        'device_type': 'cisco_asa',
                        'ip': v,
                        'username': deviceUserMap[k],
                        'password': devicePassMap[k],
                        'secret': deviceSecretMap[k],
                        'verbose': False,
                        }
                    net_connect = ConnectHandler(**cisco_asa)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : Interface Configuration Started; Please wait\n")
                        text_box.insert(tk.END,smallBuff)
     
                    commands_to_execute=[]
                    commands_to_execute.append("hostname " + deviceHostMap[k])

                    for innerItems in interfaceChangeTable[deviceHostMap[k]]:
                        for interfaceName,newIPaddr in innerItems.items():
                            commands_to_execute.append(interfaceName) #Goes into interface specific config command
                            commands_to_execute.append("no ip address") #To reset any previous configuration
                            commands_to_execute.append(newIPaddr) #Changes the IP
                            commands_to_execute.append("no shutdown")
                            commands_to_execute.append("exit")

                    commands_to_execute.append("router ospf 1")
                    commands_to_execute.append("network 0.0.0.0 0.0.0.0 area 0") #To reset any previous configuration
                    commands_to_execute.append("exit")
                    
                    out = net_connect.send_config_set( commands_to_execute,exit_config_mode=True)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : Interface Configuration Completed")
                        text_box.insert(tk.END,smallBuff)
                        text_box.insert(tk.END, "\n")
 
        except:
            text_box.insert(tk.END, "Configuration failed on Device: " + str(deviceHostMap[k]) + "; Please check if the router is reachable and SSH is working")
            text_box.insert(tk.END, "\n")
    if getattr(t, "do_run", True):
        text_box.insert(tk.END, "--- Event has completed ---")
        text_box.insert(tk.END, "\n")
 
def configureOspf():
    global deviceIPMap
    global deviceIntMap
    global deviceHostMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceDomainMap
    global deviceHostReverseMap
    global interfaceChangeTable
    global interfaceIPtable
    global text_box

    bigBuff = ''
    text_box.delete(0,END)
    text_box.insert(tk.END, "Configuring OSPF routing protcol on all routers: (Please wait)")
    text_box.insert(tk.END, "\n")
    
    for k,v in deviceIPMap.items():
        try:
            if(deviceHostMap[k] in interfaceChangeTable.keys()):
                t = threading.currentThread()
                if getattr(t, "do_run", True):
                    cisco_asa = {
                        'device_type': 'cisco_asa',
                        'ip': v,
                        'username': deviceUserMap[k],
                        'password': devicePassMap[k],
                        'secret': deviceSecretMap[k],
                        'verbose': False,
                        }
                    net_connect = ConnectHandler(**cisco_asa)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : OSPF Protocol Configuration Started; Please wait\n")
                        text_box.insert(tk.END,smallBuff)
     
                    commands_to_execute=[]
                    commands_to_execute.append("router ospf 1")
                    commands_to_execute.append("network 0.0.0.0 0.0.0.0 area 0") #To reset any previous configuration
                    commands_to_execute.append("exit")
                            
                    out = net_connect.send_config_set( commands_to_execute,exit_config_mode=True)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : OSPF Protocol Configuration Completed")
                        text_box.insert(tk.END,smallBuff)
                        text_box.insert(tk.END, "\n")
 
        except:
            text_box.insert(tk.END, "Configuration failed on Device: " + str(deviceHostMap[k]) + "; Please check if the router is reachable and SSH is working")
            text_box.insert(tk.END, "\n")
    if getattr(t, "do_run", True):
        text_box.insert(tk.END, "--- Event has completed ---")
        text_box.insert(tk.END, "\n")


def showCommand(event,hostname):
    global deviceIPMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceHostReverseMap
    global deviceHostMap
    global text_box
    
    text_box.delete(0,END)
    if (event == 1):
        text_box.insert(tk.END, "Displaying show ip interface brief command output in all routers: (Please wait)")
    elif (event == 2):
        text_box.insert(tk.END, "Displaying show cdp neighbors command output in all routers: (Please wait)")
    elif (event == 3):
        text_box.insert(tk.END, "Displaying show ip route command output in all routers: (Please wait)")
    text_box.insert(tk.END, "\n")
    bigBuff = ''
    for k,v in deviceIPMap.items():
        try:
            t = threading.currentThread()
            if getattr(t, "do_run", True):
                if(hostname == "ALL" or hostname == deviceHostMap[k]):
                    cisco_asa = {
                        'device_type': 'cisco_asa',
                        'ip': v,
                        'username': deviceUserMap[k],
                        'password': devicePassMap[k],
                        'secret': deviceSecretMap[k],
                        'verbose': False,
                        }
                    net_connect = ConnectHandler(**cisco_asa)
                    if (event == 1):
                        smallBuff = showIpIntBrief(net_connect)
                    elif (event == 2):
                        smallBuff = showCdpNeighbors(net_connect)
                    elif (event == 3):
                        smallBuff = showIpRoute(net_connect)
                    bigBuff += smallBuff
                    bigBuff += '##################################################################\n'
                    if getattr(t, "do_run", True):
                        list_of_details_per_user=smallBuff.split("\n")
                        for each_detail in  list_of_details_per_user:
                            text_box.insert(tk.END, each_detail)
                        text_box.insert(tk.END, "\n")
        except:
            text_box.insert(tk.END, "Show command failed on Device: " + str(deviceHostMap[k]) + "; Please check if the router is reachable and SSH is working")
            text_box.insert(tk.END, "\n")
    if getattr(t, "do_run", True):
        text_box.insert(tk.END, "--- Event has completed ---")
        text_box.insert(tk.END, "\n")
            
def showIpIntBrief(net_connect):
    devName = net_connect.find_prompt() 
    output = (devName + " show ip interface brief\n")
    output += net_connect.send_command("show ip int brief")
    return output

def showCdpNeighbors(net_connect):
    devName = net_connect.find_prompt() 
    output = (devName + " show cdp neighbors\n")
    output += net_connect.send_command("show cdp neighbors")
    return output

def showIpRoute(net_connect):
    devName = net_connect.find_prompt() 
    output = (devName + " show ip route\n")
    output += net_connect.send_command("show ip route")
    return output
   
def resetInterfaces():
    global deviceIPMap
    global deviceIntMap
    global deviceHostMap
    global deviceUserMap
    global devicePassMap
    global deviceSecretMap
    global deviceDomainMap
    global deviceHostReverseMap
    global interfaceChangeTable
    global interfaceIPtable
    global text_box

    bigBuff = ''
    text_box.delete(0,END)
    text_box.insert(tk.END, "Resetting all the interfaces on all routers: (Please wait)")
    text_box.insert(tk.END, "\n")
     
    for k,v in deviceIPMap.items():
        try:
            if(deviceHostMap[k] in interfaceChangeTable.keys()):
                t = threading.currentThread()
                if getattr(t, "do_run", True):
                    cisco_asa = {
                        'device_type': 'cisco_asa',
                        'ip': v,
                        'username': deviceUserMap[k],
                        'password': devicePassMap[k],
                        'secret': deviceSecretMap[k],
                        'verbose': False,
                        }
                    net_connect = ConnectHandler(**cisco_asa)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : Interface Resetting Started; Please wait\n")
                        text_box.insert(tk.END,smallBuff)
                    commands_to_execute = []
                    for innerItems in interfaceChangeTable[deviceHostMap[k]]:
                        for interfaceName,newIPaddr in innerItems.items():
                            commands_to_execute.append(interfaceName) #Goes into interface specific config command
                            commands_to_execute.append("no ip address") #To reset any previous configuration
                            commands_to_execute.append("shutdown")
                            commands_to_execute.append("exit")

                    out = net_connect.send_config_set( commands_to_execute,exit_config_mode=True)
                    out = net_connect.find_prompt()
                    if getattr(t, "do_run", True):
                        smallBuff = (out + " : Interface Resetting Completed")
                        text_box.insert(tk.END,smallBuff)
                        text_box.insert(tk.END, "\n")
 
        except:
            text_box.insert(tk.END, "Interface reset failed on Device: " + str(deviceHostMap[k]) + "; Please check if the router is reachable and SSH is working")
            text_box.insert(tk.END, "\n")
    if getattr(t, "do_run", True):        
        text_box.insert(tk.END, "--- Event has completed ---")
        text_box.insert(tk.END, "\n")
                     
def eventHandler(number):
            global thr
            thr.do_run = False
            if (number ==1):
                text_box.delete(0,END)
                text_box.insert(tk.END, "Enter the command: \"crypto key generate rsa\" on all the routers and ensure that your domain is set for configuring SSH\n")
                #bigBuffOp = setupSSH()
                
            elif (number==2):
                thr = threading.Thread(target=configureInterfaces, args=(), kwargs={})
                thr.do_run = True
                thr.start()              
            
            elif (number==3):
                thr = threading.Thread(target=resetInterfaces, args=(), kwargs={})
                thr.do_run = True
                thr.start()  
                
            elif (number==4):
                text_box.delete(0,END)
                text_box.insert(tk.END, "This feature will be implemented in the future.")
                            
            elif (number==5):
                text_box.delete(0,END)
                text_box.insert(tk.END, "This feature will be implemented in the future.")
                
            elif (number==6):
                #configure OSPF
                thr = threading.Thread(target=configureOspf, args=(), kwargs={})
                thr.do_run = True
                thr.start()
                
            elif (number==7):
                text_box.delete(0,END)
                text_box.insert(tk.END, "This feature will be implemented in the future.")
                
            elif (number==8):
                #Show ip int brief
                thr = threading.Thread(target=showCommand, args=(1,"ALL"), kwargs={})
                thr.do_run = True
                thr.start() 
                           
            elif (number==9):
                #Show cdp neighbors
                thr = threading.Thread(target=showCommand, args=(2,"ALL"), kwargs={})
                thr.do_run = True
                thr.start() 
                                
            elif (number==10):
                #Show ip route
                thr = threading.Thread(target=showCommand, args=(3,"ALL"), kwargs={})
                thr.do_run = True
                thr.start()

            elif (number==11):
                #Check for SSH
                thr = threading.Thread(target=testSSH, args=(), kwargs={})
                thr.do_run = True
                thr.start() 

def update_txt(event = None):
    text_box.update_idletasks()
    
if(parseConfigs() == False):
    print("Configs are wrong. Please correct them.")
    sys.exit(1)
    
#initialize root
thr = threading.Thread(target=update_txt, args=(), kwargs={})
root1=tk.Tk()
app=FullScreenApp(root1)

#initialize Label
label = tk.Label(root1, text='Welcome to auto config GUI', font=("Verdana", 15), anchor='center')


#Button Objects
B_setup_ssh = tk.Button(root1, text ="Setup SSH on All Routers",command=lambda: eventHandler(1),font=('Fixed', 15))
B_test_ssh = tk.Button(root1, text ="Test if SSH is working on All Routers",command=lambda: eventHandler(11),font=('Fixed', 15))
B_config_interface = tk.Button(root1, text ="Configure Interfaces",command=lambda: eventHandler(2),font=('Fixed', 15))
B_reset_config = tk.Button(root1, text ="Reset Interfaces & Configuration",command=lambda: eventHandler(3),font=('Fixed', 15))
B_show_ip_int = tk.Button(root1, text ="Show IP Interface Brief",command=lambda: eventHandler(8),font=('Fixed', 15))
B_show_cdp_neigh = tk.Button(root1, text ="Show CDP Neighbours",command=lambda: eventHandler(9),font=('Fixed', 15))
B_show_ip_route = tk.Button(root1, text ="Show IP Route",command=lambda: eventHandler(10),font=('Fixed', 15))
B_config_rip = tk.Button(root1, text ="Configure RIP",command=lambda: eventHandler(4),font=('Fixed', 15))
B_clear_rip = tk.Button(root1, text ="Clear RIP",command=lambda: eventHandler(5),font=('Fixed', 15))
B_config_ospf = tk.Button(root1, text ="Configure OSPF",command=lambda: eventHandler(6),font=('Fixed', 15))
B_clear_ospf = tk.Button(root1, text ="Clear OSPF",command=lambda: eventHandler(7),font=('Fixed', 15))

text_box = tk.Listbox(root1, width=75, height=100, font=('Verdana', 18))

text_box.pack(side=RIGHT)
yscroll = tk.Scrollbar(command=text_box.yview, orient=tk.VERTICAL)
yscroll.pack(side=RIGHT,fill=BOTH,expand=1)
text_box.configure(yscrollcommand=yscroll.set)


#Layout Control
B_setup_ssh.pack(pady=10,ipadx=20 )
B_test_ssh.pack(pady=10,ipadx=20 )
B_config_interface.pack(pady=10,ipadx=32)
B_reset_config.pack(pady=10)
B_show_ip_int.pack(pady=10,ipadx=29)
B_show_cdp_neigh.pack(pady=10, ipadx=30)
B_show_ip_route.pack(pady=10,ipadx=50)
B_config_rip.pack(pady=10, ipadx=49)
B_clear_rip.pack(pady=10,ipadx=63)
B_config_ospf.pack(pady=10,ipadx=45)
B_clear_ospf.pack(pady=10,ipadx=58)
text_box.pack()

root1.after(1000,update_txt)
root1.mainloop()
