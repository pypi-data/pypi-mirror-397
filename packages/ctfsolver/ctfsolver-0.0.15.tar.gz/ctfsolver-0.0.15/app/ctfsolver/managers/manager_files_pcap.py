"""
manager_files_pcap.py

This module provides the ManagerFilePcap class for handling and analyzing PCAP files using Scapy.
It offers methods to open PCAP files, filter ICMP packets, extract TTL values, and search for specific text within packet payloads.

Classes:
    ManagerFilePcap: Manages PCAP file operations and packet analysis.

Typical usage example:
    manager = ManagerFilePcap()
    packets = manager.pcap_open(file=path_to_pcap)
    icmp_packets = manager.get_packets_icmp(packets)
    ttl_values = manager.get_packet_ttl(icmp_packets)
    found_text = manager.searching_text_in_packets("flag", packets)
"""

import scapy.all as scapy


class ManagerFilePcap:
    """
    ManagerFilePcap provides methods for handling and analyzing PCAP files using Scapy.
    This class allows you to open PCAP files, filter packets by protocol (such as ICMP),
    extract specific packet attributes (like TTL), and search for text within packet payloads.
    Attributes:
        packets (list[scapy.packet.Packet]): List of packets loaded from a PCAP file.
        challenge_file (Path): Default file path for PCAP operations.
    Methods:
        initializing_all_ancestors(*args, **kwargs):
            Initializes all ancestors of the class.
        pcap_open(file=None, save=False) -> list[scapy.packet.Packet] | None:
            Opens a PCAP file and loads packets using Scapy.
        get_packets_icmp(packets=None) -> list:
            Retrieves all ICMP packets from the loaded packets.
        get_packet_ttl(packets=None) -> list:
            Extracts the TTL values from the provided packets.
        searching_text_in_packets(text, packets=None, display=False) -> str:
            Searches for a specific text in packet payloads and optionally displays matching packets.
    """

    def __init__(self, *args, **kwargs):
        pass

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class
            Placeholder for overwrite

        """
        pass

    def pcap_open(self, file=None, save=False) -> list[scapy.packet.Packet] | None:
        """
        Description:
            Open the pcap file with scapy and saves it in self.packets

        Args:
            file (Path, optional): File to open. Defaults to None.
            save (bool, optional): Save the output. Defaults to False.
        """

        if file is None:
            file = self.challenge_file

        self.packets = scapy.rdpcap(file.as_posix())

        # In later versions this should be changed
        if save:
            return self.packets

    def get_packets_icmp(self, packets=None):
        """
        Description:
        Get all the ICMP packets from the packets

        Args:
            packets (list, optional): List of packets to search in. Defaults to None.

        Returns:
            list: List of ICMP packets
        """

        if packets is None:
            packets = self.packets

        icmp_packets = [packet for packet in packets if packet.haslayer("ICMP")]

        return icmp_packets

    def get_packet_ttl(self, packets=None):
        """
        Description:
        Get the TTL of all the ICMP packets

        Args:
            packets (list, optional): List of packets to search in. Defaults to None.

        Returns:
            list: List of TTL of the ICMP packets
        """
        if packets is None:
            packets = self.packets

        icmp_ttl = [packet.ttl for packet in packets]

        return icmp_ttl

    def searching_text_in_packets(self, text, packets=None, display=False):
        """
        Description:
        Search for a text in the packets that have been opened with scapy

        Args:
            text (str): Text to search in the packets
            packets (list, optional): List of packets to search in. Defaults to None.
            display (bool, optional): Display the packet if the text is found. Defaults to False.

        Returns:
            str: Text found in the packet if found
        """

        if packets is None:
            packets = self.packets

        for i, packet in enumerate(packets):
            if packet.haslayer("Raw"):
                if text.encode() in packet["Raw"].load:
                    if display:
                        print(f"Found {text} in packet {i}")
                        print(packet.show())
                        print(packet.summary())
                    return packet["Raw"].load.decode("utf-8")
