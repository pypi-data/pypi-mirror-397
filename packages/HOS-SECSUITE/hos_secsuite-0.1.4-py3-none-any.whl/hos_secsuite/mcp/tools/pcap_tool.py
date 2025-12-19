"""PCAP tool integration for MCP Service"""

import asyncio
import subprocess
import os
from typing import Dict, Any, Optional, List

from scapy.all import sniff, wrpcap, rdpcap, IP, TCP, UDP, ICMP
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import Ether

from hos_secsuite.core.base_module import BaseModule


class PcapTool(BaseModule):
    """PCAP tool integration module"""
    
    name = "scan.pcap"
    description = "PCAP - Packet capture and analysis tool"
    category = "scan"
    subcategory = "network"
    
    options = {
        "interface": {
            "required": False,
            "default": "",
            "description": "Network interface to capture from (e.g., 'eth0', 'wlan0')"
        },
        "filter": {
            "required": False,
            "default": "",
            "description": "BPF filter for packet capture (e.g., 'tcp port 80' or 'udp port 53')"
        },
        "count": {
            "required": False,
            "default": 100,
            "description": "Number of packets to capture"
        },
        "timeout": {
            "required": False,
            "default": 30,
            "description": "Capture timeout in seconds"
        },
        "output_file": {
            "required": False,
            "default": "",
            "description": "Output PCAP file path"
        },
        "input_file": {
            "required": False,
            "default": "",
            "description": "Input PCAP file path for analysis"
        },
        "analysis_type": {
            "required": False,
            "default": "basic",
            "description": "Analysis type (basic, detailed, protocol_stats)"
        }
    }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run PCAP capture or analysis
        
        Returns:
            Dict[str, Any]: PCAP result
        """
        interface = self.current_options["interface"]
        filter_expr = self.current_options["filter"]
        count = self.current_options["count"]
        timeout = self.current_options["timeout"]
        output_file = self.current_options["output_file"]
        input_file = self.current_options["input_file"]
        analysis_type = self.current_options["analysis_type"]
        
        # Check if we're analyzing an existing file or capturing new packets
        if input_file and os.path.exists(input_file):
            # Analyze existing PCAP file
            return await self._analyze_pcap(input_file, analysis_type)
        else:
            # Capture new packets
            return await self._capture_packets(interface, filter_expr, count, timeout, output_file)
    
    async def _capture_packets(
        self, 
        interface: str, 
        filter_expr: str, 
        count: int, 
        timeout: int, 
        output_file: str
    ) -> Dict[str, Any]:
        """Capture packets from network interface
        
        Args:
            interface: Network interface
            filter_expr: BPF filter expression
            count: Number of packets to capture
            timeout: Capture timeout
            output_file: Output PCAP file path
            
        Returns:
            Dict[str, Any]: Capture result
        """
        try:
            # Capture packets using scapy
            packets = sniff(
                iface=interface if interface else None,
                filter=filter_expr,
                count=count,
                timeout=timeout
            )
            
            # Save to file if output file is provided
            if output_file:
                wrpcap(output_file, packets)
            
            # Basic packet statistics
            stats = self._get_packet_stats(packets)
            
            return {
                "status": "success",
                "action": "capture",
                "interface": interface,
                "filter": filter_expr,
                "packet_count": len(packets),
                "output_file": output_file,
                "stats": stats,
                "packets": [self._packet_to_dict(pkt) for pkt in packets[:10]]  # Return first 10 packets
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to capture packets: {str(e)}",
                "action": "capture"
            }
    
    async def _analyze_pcap(self, input_file: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze existing PCAP file
        
        Args:
            input_file: Input PCAP file path
            analysis_type: Analysis type
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        try:
            # Read PCAP file
            packets = rdpcap(input_file)
            
            # Get basic statistics
            stats = self._get_packet_stats(packets)
            
            result = {
                "status": "success",
                "action": "analysis",
                "input_file": input_file,
                "analysis_type": analysis_type,
                "packet_count": len(packets),
                "stats": stats
            }
            
            # Add detailed analysis if requested
            if analysis_type == "detailed" or analysis_type == "protocol_stats":
                result["detailed_analysis"] = self._get_detailed_analysis(packets, analysis_type)
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze PCAP file: {str(e)}",
                "action": "analysis"
            }
    
    def _get_packet_stats(self, packets: List) -> Dict[str, Any]:
        """Get basic packet statistics
        
        Args:
            packets: List of packets
            
        Returns:
            Dict[str, Any]: Packet statistics
        """
        stats = {
            "total_packets": len(packets),
            "ip_packets": 0,
            "tcp_packets": 0,
            "udp_packets": 0,
            "icmp_packets": 0,
            "other_packets": 0,
            "src_ips": set(),
            "dst_ips": set(),
            "src_ports": set(),
            "dst_ports": set()
        }
        
        for pkt in packets:
            if IP in pkt:
                stats["ip_packets"] += 1
                stats["src_ips"].add(pkt[IP].src)
                stats["dst_ips"].add(pkt[IP].dst)
                
                if TCP in pkt:
                    stats["tcp_packets"] += 1
                    stats["src_ports"].add(pkt[TCP].sport)
                    stats["dst_ports"].add(pkt[TCP].dport)
                elif UDP in pkt:
                    stats["udp_packets"] += 1
                    stats["src_ports"].add(pkt[UDP].sport)
                    stats["dst_ports"].add(pkt[UDP].dport)
                elif ICMP in pkt:
                    stats["icmp_packets"] += 1
                else:
                    stats["other_packets"] += 1
            else:
                stats["other_packets"] += 1
        
        # Convert sets to lists for JSON serialization
        stats["src_ips"] = list(stats["src_ips"])
        stats["dst_ips"] = list(stats["dst_ips"])
        stats["src_ports"] = list(stats["src_ports"])
        stats["dst_ports"] = list(stats["dst_ports"])
        
        return stats
    
    def _get_detailed_analysis(self, packets: List, analysis_type: str) -> Dict[str, Any]:
        """Get detailed packet analysis
        
        Args:
            packets: List of packets
            analysis_type: Analysis type
            
        Returns:
            Dict[str, Any]: Detailed analysis
        """
        analysis = {
            "protocol_distribution": {},
            "port_distribution": {},
            "ip_distribution": {}
        }
        
        # Protocol distribution
        protocol_counts = {}
        for pkt in packets:
            if TCP in pkt:
                proto = "TCP"
            elif UDP in pkt:
                proto = "UDP"
            elif ICMP in pkt:
                proto = "ICMP"
            elif IP in pkt:
                proto = f"IP_{pkt[IP].proto}"
            else:
                proto = "OTHER"
            
            protocol_counts[proto] = protocol_counts.get(proto, 0) + 1
        
        analysis["protocol_distribution"] = protocol_counts
        
        # Port distribution (for TCP/UDP)
        if analysis_type == "detailed":
            port_counts = {}
            for pkt in packets:
                if TCP in pkt:
                    port = pkt[TCP].dport
                    port_counts[port] = port_counts.get(port, 0) + 1
                elif UDP in pkt:
                    port = pkt[UDP].dport
                    port_counts[port] = port_counts.get(port, 0) + 1
            
            analysis["port_distribution"] = port_counts
        
        return analysis
    
    def _packet_to_dict(self, packet) -> Dict[str, Any]:
        """Convert scapy packet to dictionary
        
        Args:
            packet: Scapy packet object
            
        Returns:
            Dict[str, Any]: Packet as dictionary
        """
        pkt_dict = {
            "timestamp": packet.time,
            "length": len(packet)
        }
        
        # Add Ethernet layer info if present
        if Ether in packet:
            pkt_dict["ethernet"] = {
                "src": packet[Ether].src,
                "dst": packet[Ether].dst,
                "type": packet[Ether].type
            }
        
        # Add IP layer info if present
        if IP in packet:
            pkt_dict["ip"] = {
                "version": packet[IP].version,
                "src": packet[IP].src,
                "dst": packet[IP].dst,
                "proto": packet[IP].proto,
                "ttl": packet[IP].ttl
            }
        
        # Add TCP layer info if present
        if TCP in packet:
            pkt_dict["tcp"] = {
                "sport": packet[TCP].sport,
                "dport": packet[TCP].dport,
                "flags": str(packet[TCP].flags),
                "seq": packet[TCP].seq,
                "ack": packet[TCP].ack,
                "window": packet[TCP].window
            }
        
        # Add UDP layer info if present
        if UDP in packet:
            pkt_dict["udp"] = {
                "sport": packet[UDP].sport,
                "dport": packet[UDP].dport,
                "length": packet[UDP].len
            }
        
        # Add ICMP layer info if present
        if ICMP in packet:
            pkt_dict["icmp"] = {
                "type": packet[ICMP].type,
                "code": packet[ICMP].code
            }
        
        return pkt_dict
    
    async def analyze_file(self, file_path: str, analysis_type: str = "basic") -> Dict[str, Any]:
        """Analyze PCAP file
        
        Args:
            file_path: PCAP file path
            analysis_type: Analysis type
            
        Returns:
            Dict[str, Any]: Analysis result
        """
        self.set_option("input_file", file_path)
        self.set_option("analysis_type", analysis_type)
        return await self.run()
    
    async def capture(self, interface: str = "", filter_expr: str = "", count: int = 100, timeout: int = 30, output_file: str = "") -> Dict[str, Any]:
        """Capture packets
        
        Args:
            interface: Network interface
            filter_expr: BPF filter
            count: Number of packets
            timeout: Capture timeout
            output_file: Output file
            
        Returns:
            Dict[str, Any]: Capture result
        """
        self.set_option("interface", interface)
        self.set_option("filter", filter_expr)
        self.set_option("count", count)
        self.set_option("timeout", timeout)
        self.set_option("output_file", output_file)
        return await self.run()
