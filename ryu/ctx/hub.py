from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls


class Hub(app_manager.RyuApp):
    # openflow version
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self,*args,**kwargs):
        super(Hub,self).__init__(*args,**kwargs)

    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures,CONFIG_DISPATCHER)
    def switch_features_handler(self,ev):
        '''
        handle openvswitch connection
        CONFIG_DISPATCHER : Version negotiated and sent features-request message
        '''
        datapath = ev.msg.datapath      # get data layer
        ofproto = datapath.ofproto      # get openflow proto
        ofp_parser = datapath.ofproto_parser        # parse the proto

        match = ofp_parser.OFPMatch()       # match field
        # send the packet, OFPP_CONTROLLER: receive port, OFPCML_NO_BUFFER: because we send message to controller, so no buffer.
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]

        # default flow entry, set the lowest privilege
        self.add_flow(datapath,0,match,actions,"default flow entry")

    def add_flow(self,datapath,priority,match,actions,remind_content):
        '''
        datapath: send flow entry to which node
        priority: the privilege
        match,actions:match field and the action
        '''

        # datapath attributes
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # the instructions defined in the openflow v1.3
        # construct a flow msg and send it
        inst = [ofp_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]

        mod = ofp_parser.OFPFlowMod(datapath=datapath,priority=priority,match=match,instructions=inst);
        print("install to datapath,"+remind_content)
        
        # send out
        datapath.send_msg(mod);


    @set_ev_cls(ofp_event.EventOFPPacketIn,MAIN_DISPATCHER)
    def packet_in_handler(self,ev):
        '''
        1.recevive from OpenVSwitch
        2.flood the packets to other ports
        '''

        # parse msg construct
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # get the source port
        in_port = msg.match['in_port']

        print("get packet in, install flow entry,and lookback parket to datapath")
        
        # null means all match
        match = ofp_parser.OFPMatch();
        # flood is the reversed port
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

        # send the flow, the privilege is high than default flow entry
        self.add_flow(datapath,1,match,actions,"hub flow entry")

        # send the packet to datapath, and handle according to the flow entry
        out = ofp_parser.OFPPacketOut(datapath=datapath,buffer_id=msg.buffer_id,
                                            in_port=in_port,actions=actions)    

        datapath.send_msg(out);