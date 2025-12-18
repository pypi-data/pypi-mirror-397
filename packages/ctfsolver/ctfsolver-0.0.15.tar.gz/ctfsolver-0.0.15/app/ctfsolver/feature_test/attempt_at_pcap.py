from pyvis.network import Network
import scapy.all as scapy
from ctfsolver.managers.manager_files_pcap import ManagerFilePcap


class GraphAttempt:

    def visualize_packet_flow(self, filename="packet_graph.html", limit=None):
        """
        Visualize the interaction between IPs in the PCAP file as a graph.
        """
        edge_set = set()
        node_counts = {}

        for i, packet in enumerate(self.packets):
            if limit and i >= limit:
                break
            if packet.haslayer("IP"):
                src = packet["IP"].src
                dst = packet["IP"].dst
                proto = packet.sprintf("%IP.proto%")

                node_counts[src] = node_counts.get(src, 0) + 1
                node_counts[dst] = node_counts.get(dst, 0) + 1

                edge_key = (src, dst, proto)
                if edge_key not in edge_set:
                    self.packet_graph.add_node(src, label=src)
                    self.packet_graph.add_node(dst, label=dst)
                    self.packet_graph.add_edge(src, dst, label=proto)
                    edge_set.add(edge_key)

        # Optional: scale node sizes by count
        for node_id in node_counts:
            self.packet_graph.get_node(node_id)["value"] = node_counts[node_id]

        self.packet_graph.show_buttons(filter_=["physics"])
        self.packet_graph.show(filename)
        print(f"[+] Packet interaction graph saved to {filename}")
