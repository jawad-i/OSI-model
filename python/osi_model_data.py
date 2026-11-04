"""
OSI 7-Layer Model Metadata, Educational Content & Header Logic.
Separates data structures, theoretical explanations, and simulation state from UI rendering.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class LayerInfo:
    number: int
    name: str
    data_unit: str
    key_protocols: str
    hardware_software: str
    color: str
    accent_color: str
    short_desc: str
    detailed_responsibility: str
    simulated_header_name: str
    educational_note: str

OSI_LAYERS: Dict[int, LayerInfo] = {
    7: LayerInfo(
        number=7,
        name="Application",
        data_unit="Data / Message",
        key_protocols="HTTP/HTTPS, DNS, FTP, SMTP, SSH",
        hardware_software="Software Applications, Web Browsers, APIs",
        color="bright_green",
        accent_color="green",
        short_desc="User interface & network services gateway",
        detailed_responsibility="Directly interacts with software applications (e.g. web browsers, email clients) to produce user messages and initiate network communication requests.",
        simulated_header_name="APP_HDR",
        educational_note="In real systems, protocols like HTTP/1.1 or HTTP/2 format requests. Here, an educational HTTP envelope wraps the user's raw message."
    ),
    6: LayerInfo(
        number=6,
        name="Presentation",
        data_unit="Formatted / Encrypted Data",
        key_protocols="SSL/TLS, ASCII, UTF-8, JPEG, JSON",
        hardware_software="Operating System Cryptographic & Serialization Libraries",
        color="bright_cyan",
        accent_color="cyan",
        short_desc="Data syntax, translation, compression & encryption",
        detailed_responsibility="Ensures data is formatted, compressed, and encrypted so that the receiving system can correctly parse and interpret the transmitted syntax.",
        simulated_header_name="PRES_HDR",
        educational_note="Simulates AES-256 encryption metadata and JSON syntax formatting before handing data down to the session manager."
    ),
    5: LayerInfo(
        number=5,
        name="Session",
        data_unit="Session Data",
        key_protocols="NetBIOS, RPC, PPTP, Sockets API",
        hardware_software="OS Session Management & IPC APIs",
        color="bright_magenta",
        accent_color="magenta",
        short_desc="Dialog control, session establishment & checkpoints",
        detailed_responsibility="Manages opening, maintaining, synchronizing checkpoints, and cleanly terminating conversations (sessions) between communicating applications.",
        simulated_header_name="SESS_HDR",
        educational_note="Simulates session identifier (0x5A1B) and synchronization tokens to ensure continuous session continuity."
    ),
    4: LayerInfo(
        number=4,
        name="Transport",
        data_unit="Segments (TCP) / Datagrams (UDP)",
        key_protocols="TCP (Transmission Control Protocol), UDP",
        hardware_software="Kernel Networking Stack (L4 Protocol Handlers)",
        color="bright_yellow",
        accent_color="yellow",
        short_desc="End-to-end delivery, port addressing, flow & error control",
        detailed_responsibility="Manages host-to-host end-to-end reliability, segment sequencing, port addressing (Src: 54321 -> Dst: 8080), flow control, and data checksums.",
        simulated_header_name="TCP_HDR",
        educational_note="Encapsulates source port 54321, destination port 8080, sequence number #1001, and 16-bit payload checksum."
    ),
    3: LayerInfo(
        number=3,
        name="Network",
        data_unit="Packets",
        key_protocols="IPv4, IPv6, ICMP, OSPF, BGP",
        hardware_software="Routers, Layer 3 Switches, Kernel IP Router",
        color="bright_blue",
        accent_color="blue",
        short_desc="Logical addressing, subnet routing & packet forwarding",
        detailed_responsibility="Handles logical IP addressing (192.168.1.100 -> 192.168.1.200), determines the optimal network routing path, and manages Time-To-Live (TTL).",
        simulated_header_name="IP_HDR",
        educational_note="Appends IPv4 version 4, TTL=64, Protocol=6 (TCP), and Source/Destination IP address tags."
    ),
    2: LayerInfo(
        number=2,
        name="Data Link",
        data_unit="Frames",
        key_protocols="Ethernet (IEEE 802.3), Wi-Fi (802.11), ARP",
        hardware_software="Network Interface Card (NIC), Network Switches, MAC Bridges",
        color="bright_red",
        accent_color="red",
        short_desc="Physical MAC addressing, framing & Frame Check Sequence (CRC)",
        detailed_responsibility="Packages packets into frames, addresses them using physical MAC addresses (00:1A:2B:3C:4D:5E -> AA:BB:CC:DD:EE:FF), and appends FCS trailer for error detection.",
        simulated_header_name="ETH_FRAME",
        educational_note="Wraps packet in an Ethernet frame with source/dest MAC, EtherType 0x0800, and a CRC32/FCS error-detection trailer."
    ),
    1: LayerInfo(
        number=1,
        name="Physical",
        data_unit="Raw Bits (0s & 1s) / Signals",
        key_protocols="1000BASE-T Ethernet, Fiber Optic, Wi-Fi PHY, Preamble",
        hardware_software="Network Transceivers, PHY Chips, Twisted-Pair Cables, Sockets",
        color="white",
        accent_color="bright_white",
        short_desc="Electrical pulses, optical signals & raw binary bitstream",
        detailed_responsibility="Converts the structured frame into raw binary bits (0s and 1s) and transmits electrical/radio signals across the physical communication medium (real socket).",
        simulated_header_name="PHYS_BITS",
        educational_note="Encodes characters into 8-bit binary ASCII stream with a 16-bit Ethernet Preamble/SFD (1010101010101011) transmitted over physical TCP socket wire."
    )
}

@dataclass
class EncapsulationState:
    layer: int
    data_envelope: str
    header_added: str
    bits: str = ""
    progress_checkpoint: Optional[int] = None
    progress_percent: int = 0
    progress_desc: str = ""

def generate_encapsulation_steps(raw_message: str) -> List[EncapsulationState]:
    """
    Generates step-by-step encapsulation data structures for Layers 7 down to 1.
    """
    l7_env = f"[APP|HTTP/1.1|DATA={raw_message}]"
    l6_env = f"[PRES|ENC=AES256|COMPR=OFF|PAYLOAD={l7_env}]"
    l5_env = f"[SESS|ID=0x5A1B|SYNC=TRUE|PAYLOAD={l6_env}]"
    l4_env = f"[TCP|SRC=54321|DST=8080|SEQ=1001|ACK=0|CSUM=0x4A2F|PAYLOAD={l5_env}]"
    l3_env = f"[IP|VER=4|SRC=192.168.1.100|DST=192.168.1.200|TTL=64|PROTO=6|PAYLOAD={l4_env}]"
    l2_env = f"[ETH|SMAC=00:1A:2B:3C:4D:5E|DMAC=AA:BB:CC:DD:EE:FF|TYPE=0x0800|FRAME={l3_env}|FCS=0x8C3B]"
    
    # Binary bitstream
    bitstream = "1010101010101011" + "".join(format(ord(c), '08b') for c in l2_env)

    return [
        EncapsulationState(
            layer=7,
            data_envelope=l7_env,
            header_added="[APP|HTTP/1.1]"
        ),
        EncapsulationState(
            layer=6,
            data_envelope=l6_env,
            header_added="[PRES|AES256]",
            progress_checkpoint=1,
            progress_percent=28,
            progress_desc="Stage 1/4 (28%): Layers 7 & 6 Completed (Application & Presentation)"
        ),
        EncapsulationState(
            layer=5,
            data_envelope=l5_env,
            header_added="[SESS|ID=0x5A1B]"
        ),
        EncapsulationState(
            layer=4,
            data_envelope=l4_env,
            header_added="[TCP|SPORT=54321|DPORT=8080]",
            progress_checkpoint=2,
            progress_percent=57,
            progress_desc="Stage 2/4 (57%): Layers 5 & 4 Completed (Session & Transport)"
        ),
        EncapsulationState(
            layer=3,
            data_envelope=l3_env,
            header_added="[IP|192.168.1.100->192.168.1.200]"
        ),
        EncapsulationState(
            layer=2,
            data_envelope=l2_env,
            header_added="[ETH|MAC=00:1A..|FCS=0x8C3B]",
            progress_checkpoint=3,
            progress_percent=85,
            progress_desc="Stage 3/4 (85%): Layers 3 & 2 Completed (Network & Data Link)"
        ),
        EncapsulationState(
            layer=1,
            data_envelope=bitstream[:80] + "... [TOTAL: " + str(len(bitstream)) + " BITS]",
            header_added="[PREAMBLE: 1010101010101011]",
            bits=bitstream,
            progress_checkpoint=4,
            progress_percent=100,
            progress_desc="Stage 4/4 (100%): Layer 1 Completed (Physical Bitstream Ready for Socket Wire)"
        )
    ]

@dataclass
class DecapsulationState:
    layer: int
    header_removed: str
    remaining_envelope: str
    progress_checkpoint: Optional[int] = None
    progress_percent: int = 0
    progress_desc: str = ""

def generate_decapsulation_steps(raw_message: str) -> List[DecapsulationState]:
    """
    Generates step-by-step decapsulation data structures for Layers 1 up to 7.
    """
    l7_env = f"[APP|HTTP/1.1|DATA={raw_message}]"
    l6_env = f"[PRES|ENC=AES256|COMPR=OFF|PAYLOAD={l7_env}]"
    l5_env = f"[SESS|ID=0x5A1B|SYNC=TRUE|PAYLOAD={l6_env}]"
    l4_env = f"[TCP|SRC=54321|DST=8080|SEQ=1001|ACK=0|CSUM=0x4A2F|PAYLOAD={l5_env}]"
    l3_env = f"[IP|VER=4|SRC=192.168.1.100|DST=192.168.1.200|TTL=64|PROTO=6|PAYLOAD={l4_env}]"
    l2_env = f"[ETH|SMAC=00:1A:2B:3C:4D:5E|DMAC=AA:BB:CC:DD:EE:FF|TYPE=0x0800|FRAME={l3_env}|FCS=0x8C3B]"

    return [
        DecapsulationState(
            layer=1,
            header_removed="Preamble / SFD (16 bits) stripped",
            remaining_envelope=l2_env
        ),
        DecapsulationState(
            layer=2,
            header_removed="Ethernet MAC Header & FCS CRC Trailer stripped",
            remaining_envelope=l3_env,
            progress_checkpoint=1,
            progress_percent=28,
            progress_desc="Stage 1/4 (28%): Layers 1 & 2 Completed (Physical Reconstructed & Data Link Verified)"
        ),
        DecapsulationState(
            layer=3,
            header_removed="IPv4 Header (192.168.1.100 -> 192.168.1.200) stripped",
            remaining_envelope=l4_env
        ),
        DecapsulationState(
            layer=4,
            header_removed="TCP Header (Port 8080 Checksum Verified) stripped",
            remaining_envelope=l5_env,
            progress_checkpoint=2,
            progress_percent=57,
            progress_desc="Stage 2/4 (57%): Layers 3 & 4 Completed (Network Routed & Transport Verified)"
        ),
        DecapsulationState(
            layer=5,
            header_removed="Session Dialog Token (0x5A1B) closed",
            remaining_envelope=l6_env
        ),
        DecapsulationState(
            layer=6,
            header_removed="AES-256 Decrypted & Syntax Transformation reversed",
            remaining_envelope=l7_env,
            progress_checkpoint=3,
            progress_percent=85,
            progress_desc="Stage 3/4 (85%): Layers 5 & 6 Completed (Session Cleaned & Data Decrypted)"
        ),
        DecapsulationState(
            layer=7,
            header_removed="HTTP/1.1 Envelope extracted -> User Data Delivered",
            remaining_envelope=f'"{raw_message}"',
            progress_checkpoint=4,
            progress_percent=100,
            progress_desc="Stage 4/4 (100%): Layer 7 Completed (Original Application Message Recovered)"
        )
    ]
