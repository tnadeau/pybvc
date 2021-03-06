#!/usr/bin/python

# Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0


"""

import time
import json

from pybvc.controller.controller import Controller
from pybvc.netconfdev.vrouter.vrouter5600 import VRouter5600
from pybvc.netconfdev.vrouter.vpn import Vpn
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file


def vr_demo_8():

    f = "cfg4.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit()

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']

        nodeName = d['nodeName']
        nodeIpAddr = d['nodeIpAddr']
        nodePortNum = d['nodePortNum']
        nodeUname = d['nodeUname']
        nodePswd = d['nodePswd']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    vrouter = VRouter5600(ctrl, nodeName, nodeIpAddr, nodePortNum,
                          nodeUname, nodePswd)
    print ("<<< 'Controller': %s, '%s': %s"
           % (ctrlIpAddr, nodeName, nodeIpAddr))

    print ("\n")
    time.sleep(rundelay)
    node_configured = False
    result = ctrl.check_node_config_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONFIGURED)):
        node_configured = True
        print ("<<< '%s' is configured on the Controller" % nodeName)
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        node_configured = False
    else:
        print ("\n")
        print "Failed to get configuration status for the '%s'" % nodeName
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    if node_configured is False:
        result = ctrl.add_netconf_node(vrouter)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< '%s' added to the Controller" % nodeName)
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.detailed())
            exit(0)

    print ("\n")
    time.sleep(rundelay)
    result = ctrl.check_node_conn_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONNECTED)):
        print ("<<< '%s' is connected to the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Show VPN configuration on the '%s'" % nodeName)
    result = vrouter.get_vpn_cfg()
    time.sleep(rundelay)
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No VPN configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print (">>> Create new VPN configuration on the '%s'" % (nodeName))
    description = ("Remote Access VPN Configuration Example - "
                   "L2TP/IPsec with Pre-Shared Key")
    external_ipaddr = "12.34.56.78"
    nexthop_ipaddr = "12.34.56.254"
    nat_traversal = True
    nat_allow_network = "192.168.100.0/24"
    client_ip_pool_start = "192.168.100.11"
    client_ip_pool_end = "192.168.100.210"
    ipsec_auth_mode = "pre-shared-secret"
    ipsec_auth_secret = "!secrettext!"
    l2tp_auth_mode = "local"
    uname1 = "user1"
    upswd1 = "user1_password"
    uname2 = "user2"
    upswd2 = "user2_password"
    uname3 = "user3"
    upswd3 = "user3_password"
    dns_srv1 = "192.168.100.1"
    dns_srv2 = "192.168.100.2"
    wins_srv1 = "192.168.100.3"
    wins_srv2 = "192.168.100.4"
    mtu = "16384"
    print (" VPN options to be set:\n"
           "   - Configuration description            : '%s'\n"
           "   - Server external address              : '%s'\n"
           "   - Next hop router address              : '%s'\n"
           "   - NAT_traversal                        : '%s'\n"
           "   - NAT allowed networks                 : '%s'\n"
           "   - Client addresses pool (start/end)    : '%s'/'%s'\n"
           "   - IPsec authentication (mode/secret)   : '%s'/'%s'\n"
           "   - L2TP authentication  mode            : '%s'\n"
           "   - Allowed users (name/password)        : '%s'/'%s'\n"
           "                                            '%s'/'%s'\n"
           "                                            '%s'/'%s'\n"
           "   - DNS servers (primary/secondary)      : '%s'/'%s'\n"
           "   - WINS servers (primary/secondary)     : '%s'/'%s'\n"
           "   - Maximum Transmission Unit            : '%s'\n"
           % (description, external_ipaddr, nexthop_ipaddr,
              "enabled" if nat_traversal else "disabled",
              nat_allow_network,
              client_ip_pool_start, client_ip_pool_end,
              ipsec_auth_mode, ipsec_auth_secret,
              l2tp_auth_mode,
              uname1, upswd1,
              uname2, upswd2,
              uname3, upswd3,
              dns_srv1, dns_srv2,
              wins_srv1, wins_srv2,
              mtu
              )
           )

    time.sleep(rundelay)

    # -------------------------------------------------------------------------
    # Encode VPN configuration options by using 'Vpn' object
    # -------------------------------------------------------------------------
    vpn = Vpn()

    # This VPN configuration description
    vpn.set_l2tp_remote_access_description(description)

    # Enable NAT traversal
    vpn.set_nat_traversal(nat_traversal)

    # Set the allowed subnets
    vpn.set_nat_allow_network(nat_allow_network)

    # Bind the L2TP server to the external IP address
    vpn.set_l2tp_remote_access_outside_address(external_ipaddr)

    # Set the next hop IP address for reaching the VPN clients
    vpn.set_l2tp_remote_access_outside_nexthop(nexthop_ipaddr)

    # Set up the pool of IP addresses that remote VPN connections will assume.
    # In this example we make 100 addresses available (from .11 to .210) on
    # subnet  192.168.100.0/24
    vpn.set_l2tp_remote_access_client_ip_pool(start=client_ip_pool_start,
                                              end=client_ip_pool_end)

    # Set the IPsec authentication mode to 'pre-shared-secret'
    vpn.set_l2tp_remote_access_ipsec_auth_mode(mode=ipsec_auth_mode)

    # Set the 'pre-shared-secret' value
    func = vpn.set_l2tp_remote_access_ipsec_auth_pre_shared_secret
    func(secret=ipsec_auth_secret)

    # Set the L2TP remote access user authentication mode to 'local'
    vpn.set_l2tp_remote_access_user_auth_mode(l2tp_auth_mode)

    # Set the L2TP remote access user credentials ('username'/'password')
    vpn.set_l2tp_remote_access_user(name=uname1, pswd=upswd1)
    vpn.set_l2tp_remote_access_user(name=uname2, pswd=upswd2)
    vpn.set_l2tp_remote_access_user(name=uname3, pswd=upswd3)

    # Set 'primary' and 'secondary' DNS servers
    vpn.set_l2tp_remote_access_primary_dns_server(dns_srv1)
    vpn.set_l2tp_remote_access_secondary_dns_server(dns_srv2)

    # Set 'primary' and 'secondary' WINS servers
    vpn.set_l2tp_remote_access_primary_wins_server(wins_srv1)
    vpn.set_l2tp_remote_access_secondary_wins_server(wins_srv2)

    # Set Maximum Transmission Unit (MTU <128..16384>)
    vpn.set_l2tp_remote_access_mtu(mtu)

    print "\n"
    print (">>> VPN configuration to be applied to the '%s'" % (nodeName))
    print vpn.get_payload()
    time.sleep(rundelay)
    result = vrouter.set_vpn_cfg(vpn)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< VPN configuration was successfully created")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show VPN configuration on the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.get_vpn_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
        print ("<<< VPN configuration was successfully read")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Delete VPN configuration from the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_vpn_cfg()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("VPN configuration successfully removed from '%s'" % (nodeName))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show VPN configuration on the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.get_vpn_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No VPN configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print (">>> Remove '%s' NETCONF node from the Controller" % nodeName)
    time.sleep(rundelay)
    result = ctrl.delete_netconf_node(vrouter)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("'%s' NETCONF node was successfully removed "
               "from the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")

if __name__ == "__main__":
    vr_demo_8()
