#!/usr/bin/env python3
"""
OSI 7-Layer Network Model Simulation & Zig-Zag Flow Visualizer
Demonstrates full 7-layer encapsulation and decapsulation with
real-time progress tracking after every two OSI layers.
"""

import sys
import os
import time
import argparse
import subprocess
import socket

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Terminal Colors & Styling
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright Foreground
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_MAGENTA = "\033[45m"
    BG_DARK = "\033[40m"

# Enable VT100 colors in Windows command prompt if needed
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

LAYER_METADATA = {
    7: {"name": "Application", "color": Style.GREEN, "unit": "Data / Message", "protocol": "HTTP/HTTPS, DNS, FTP"},
    6: {"name": "Presentation", "color": Style.CYAN, "unit": "Formatted Data", "protocol": "SSL/TLS, AES-256, ASCII"},
    5: {"name": "Session", "color": Style.MAGENTA, "unit": "Session Dialogue", "protocol": "NetBIOS, RPC, Sockets"},
    4: {"name": "Transport", "color": Style.YELLOW, "unit": "Segments", "protocol": "TCP, UDP (Ports & Seq)"},
    3: {"name": "Network", "color": Style.BLUE, "unit": "Packets", "protocol": "IPv4, IPv6, ICMP, Routing"},
    2: {"name": "Data Link", "color": Style.RED, "unit": "Frames", "protocol": "Ethernet (MAC, FCS, LLC)"},
    1: {"name": "Physical", "color": Style.WHITE, "unit": "Raw Bits / Signal", "protocol": "Ethernet PHY, 1000BASE-T"}
}

def print_banner():
    banner = f"""
{Style.BOLD}{Style.BRIGHT_CYAN}╔════════════════════════════════════════════════════════════════════════════════╗
║                   OSI 7-LAYER NETWORK MODEL SIMULATION                         ║
║         Full Encapsulation, Socket Transmission & Decapsulation                ║
║                 Progress Checkpoints Every Two OSI Layers                      ║
╚════════════════════════════════════════════════════════════════════════════════╝{Style.RESET}
"""
    print(banner)

def render_zigzag_diagram(active_side="sender", active_layer=7):
    """
    Renders an ASCII visualization of the classic OSI Zig-Zag / U-shaped data flow.
    """
    print(f"\n{Style.BOLD}--- CURRENT OSI ZIG-ZAG ARCHITECTURE STATUS ---{Style.RESET}")
    print(f"{Style.DIM}  [Client / Sender Stack]          [Physical Medium]          [Server / Receiver Stack]{Style.RESET}")
    print(f"┌───────────────────────────────┐                  ┌───────────────────────────────┐")
    
    for l in range(7, 0, -1):
        meta = LAYER_METADATA[l]
        c = meta["color"]
        name = meta["name"]
        
        # Sender marker
        if active_side == "sender" and active_layer == l:
            s_marker = f"{Style.BOLD}{Style.BRIGHT_GREEN}▶ [L{l}] {name:<12}{Style.RESET}"
            s_flow = f"{Style.BRIGHT_GREEN}  ↓↓  {Style.RESET}"
        elif active_side == "sender" and active_layer < l:
            s_marker = f"{Style.DIM}✓ [L{l}] {name:<12}{Style.RESET}"
            s_flow = f"{Style.DIM}  ││  {Style.RESET}"
        else:
            s_marker = f"{c}  [L{l}] {name:<12}{Style.RESET}"
            s_flow = "  ││  "
            
        # Receiver marker
        if active_side == "receiver" and active_layer == l:
            r_marker = f"{Style.BOLD}{Style.BRIGHT_CYAN}◀ [L{l}] {name:<12}{Style.RESET}"
            r_flow = f"{Style.BRIGHT_CYAN}  ↑↑  {Style.RESET}"
        elif active_side == "receiver" and active_layer > l:
            r_marker = f"{Style.DIM}✓ [L{l}] {name:<12}{Style.RESET}"
            r_flow = f"{Style.DIM}  ││  {Style.RESET}"
        else:
            r_marker = f"{c}  [L{l}] {name:<12}{Style.RESET}"
            r_flow = "  ││  "
            
        middle = "                  "
        if l == 1:
            if active_side == "medium":
                middle = f"{Style.BOLD}{Style.BRIGHT_YELLOW}═════ [WIRE] ════>{Style.RESET}"
            else:
                middle = f"{Style.DIM}───── [WIRE] ────>{Style.RESET}"
                
        print(f"│ {s_marker} {s_flow}│{middle}│{r_flow} {r_marker} │")
        
    print(f"└───────────────────────────────┘                  └───────────────────────────────┘\n")

def print_progress_checkpoint(stage, total_stages, layers_desc, is_encapsulation=True):
    percent = int((stage / total_stages) * 100)
    bar_width = 24
    filled = int(bar_width * (stage / total_stages))
    bar = "█" * filled + "░" * (bar_width - filled)
    flow_type = "ENCAPSULATION (DOWNWARD)" if is_encapsulation else "DECAPSULATION (UPWARD)"
    
    print(f"{Style.BOLD}{Style.BG_BLUE}{Style.WHITE} >>> LINUX STACK PROGRESS: {flow_type} | STAGE {stage}/{total_stages} [{percent}%] {Style.RESET}")
    print(f"  {Style.BOLD}Progress:{Style.RESET} [{Style.BRIGHT_GREEN}{bar}{Style.RESET}]")
    print(f"  {Style.BOLD}Layers Processed:{Style.RESET} {Style.BRIGHT_YELLOW}{layers_desc}{Style.RESET}")
    print(f"{Style.DIM}  -------------------------------------------------------------------------{Style.RESET}\n")

def simulate_layer_step(layer, side, data_in, delay=0.3):
    meta = LAYER_METADATA[layer]
    c = meta["color"]
    direction = "Encapsulating into" if side == "sender" else "Decapsulating from"
    print(f"  {c}[Layer {layer}: {meta['name']:<12}]{Style.RESET} {direction} {meta['unit']} ({meta['protocol']})")
    print(f"    {Style.DIM}Envelope:{Style.RESET} {c}{data_in[:90]}{'...' if len(data_in) > 90 else ''}{Style.RESET}")
    time.sleep(delay)

def run_simulation(message="Hello OSI Model! Real Networking Simulation", speed=0.3):
    print_banner()
    print(f"{Style.BOLD}Source Message:{Style.RESET} \"{Style.BRIGHT_YELLOW}{message}{Style.RESET}\"")
    print(f"{Style.BOLD}Data Flow Concept:{Style.RESET} Sender (L7->L1) -> Wire Socket -> Receiver (L1->L7)\n")
    
    # ---------------- ENCAPSULATION ----------------
    print(f"\n{Style.BOLD}{Style.BRIGHT_GREEN}========================================================================{Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_GREEN}        PHASE 1: SENDER STACK ENCAPSULATION (LAYERS 7 DOWN TO 1)        {Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_GREEN}========================================================================{Style.RESET}\n")
    
    render_zigzag_diagram("sender", 7)
    
    # Layer 7 & 6
    l7_data = f"[APP|HTTP/1.1|DATA={message}]"
    simulate_layer_step(7, "sender", l7_data, speed)
    
    l6_data = f"[PRES|ENC=AES256|COMPR=OFF|PAYLOAD={l7_data}]"
    simulate_layer_step(6, "sender", l6_data, speed)
    
    # Checkpoint 1 after every 2 layers (7 & 6)
    print_progress_checkpoint(1, 4, "Layer 7 (Application) & Layer 6 (Presentation)", is_encapsulation=True)
    render_zigzag_diagram("sender", 5)
    
    # Layer 5 & 4
    l5_data = f"[SESS|ID=0x5A1B|SYNC=TRUE|PAYLOAD={l6_data}]"
    simulate_layer_step(5, "sender", l5_data, speed)
    
    l4_data = f"[TCP|SRC_PORT=54321|DST_PORT=8080|SEQ=1001|ACK=0|CSUM=0x4A2F|PAYLOAD={l5_data}]"
    simulate_layer_step(4, "sender", l4_data, speed)
    
    # Checkpoint 2 after every 2 layers (5 & 4)
    print_progress_checkpoint(2, 4, "Layer 5 (Session) & Layer 4 (Transport)", is_encapsulation=True)
    render_zigzag_diagram("sender", 3)
    
    # Layer 3 & 2
    l3_data = f"[IP|VER=4|SRC_IP=192.168.1.100|DST_IP=192.168.1.200|TTL=64|PROTO=6|PAYLOAD={l4_data}]"
    simulate_layer_step(3, "sender", l3_data, speed)
    
    l2_data = f"[ETH|SMAC=00:1A:2B:3C:4D:5E|DMAC=AA:BB:CC:DD:EE:FF|TYPE=0x0800|FRAME={l3_data}|FCS=0x8C3B]"
    simulate_layer_step(2, "sender", l2_data, speed)
    
    # Checkpoint 3 after every 2 layers (3 & 2)
    print_progress_checkpoint(3, 4, "Layer 3 (Network) & Layer 2 (Data Link)", is_encapsulation=True)
    render_zigzag_diagram("sender", 1)
    
    # Layer 1
    # Generate bitstream
    bits = "1010101010101011" + "".join(format(ord(c), '08b') for c in l2_data)
    simulate_layer_step(1, "sender", bits, speed)
    
    # Checkpoint 4 after Layer 1 (Physical)
    print_progress_checkpoint(4, 4, "Layer 1 (Physical Bitstream Ready for Medium)", is_encapsulation=True)
    
    # ---------------- MEDIUM TRANSMISSION ----------------
    print(f"\n{Style.BOLD}{Style.BRIGHT_YELLOW}========================================================================{Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_YELLOW}        PHASE 2: PHYSICAL TRANSMISSION ACROSS NETWORK WIRE SOCKET       {Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_YELLOW}========================================================================{Style.RESET}\n")
    render_zigzag_diagram("medium", 1)
    
    print(f"  {Style.BOLD}Channel:{Style.RESET} TCP/IP Socket (127.0.0.1:8080)")
    print(f"  {Style.BOLD}Bitstream Length:{Style.RESET} {len(bits)} bits")
    print(f"  {Style.BOLD}Physical Signal:{Style.RESET} {Style.CYAN}{bits[:64]}...{bits[-32:]}{Style.RESET}")
    
    # Pulse animation
    for i in range(3):
        sys.stdout.write(f"\r  {Style.BRIGHT_YELLOW}Transmitting bits over wire [{'=' * (i * 8 + 8)}>]{Style.RESET}")
        sys.stdout.flush()
        time.sleep(speed * 0.8)
    print(f"\n  {Style.BRIGHT_GREEN}✓ Signal received at destination Network Interface Card (NIC)!{Style.RESET}\n")
    time.sleep(speed)
    
    # ---------------- DECAPSULATION ----------------
    print(f"\n{Style.BOLD}{Style.BRIGHT_CYAN}========================================================================{Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_CYAN}       PHASE 3: RECEIVER STACK DECAPSULATION (LAYERS 1 UP TO 7)         {Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_CYAN}========================================================================{Style.RESET}\n")
    
    render_zigzag_diagram("receiver", 1)
    
    # Layer 1 & 2
    simulate_layer_step(1, "receiver", "Decoded bits to Ethernet Frame", speed)
    simulate_layer_step(2, "receiver", "Validated FCS checksum & MAC destination", speed)
    print_progress_checkpoint(1, 4, "Layer 1 (Physical) & Layer 2 (Data Link Frame Validated)", is_encapsulation=False)
    render_zigzag_diagram("receiver", 3)
    
    # Layer 3 & 4
    simulate_layer_step(3, "receiver", "Parsed IPv4 packet header & validated TTL", speed)
    simulate_layer_step(4, "receiver", "Verified TCP destination port 8080 & segment checksum", speed)
    print_progress_checkpoint(2, 4, "Layer 3 (Network) & Layer 4 (Transport)", is_encapsulation=False)
    render_zigzag_diagram("receiver", 5)
    
    # Layer 5 & 6
    simulate_layer_step(5, "receiver", "Synchronized session token 0x5A1B", speed)
    simulate_layer_step(6, "receiver", "Decrypted AES-256 payload & decoded data formatting", speed)
    print_progress_checkpoint(3, 4, "Layer 5 (Session) & Layer 6 (Presentation)", is_encapsulation=False)
    render_zigzag_diagram("receiver", 7)
    
    # Layer 7
    simulate_layer_step(7, "receiver", f"Delivered application payload to User Space", speed)
    print_progress_checkpoint(4, 4, "Layer 7 (Application Payload Consumed by End-User)", is_encapsulation=False)
    
    print(f"\n{Style.BOLD}{Style.BRIGHT_GREEN}════════════════════════════════════════════════════════════════════════{Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_GREEN}     SUCCESS: END-TO-END OSI 7-LAYER SIMULATION COMPLETED!            {Style.RESET}")
    print(f"{Style.BOLD}     Delivered Payload: \"{Style.BRIGHT_YELLOW}{message}{Style.RESET}{Style.BOLD}\"{Style.RESET}")
    print(f"{Style.BOLD}{Style.BRIGHT_GREEN}════════════════════════════════════════════════════════════════════════{Style.RESET}\n")

def run_live_socket_workflow(message="Live socket test across all 7 layers", port=8080):
    """
    Launches the compiled C server and C client binaries to perform
    real socket communication, and monitors their output.
    """
    exe_ext = ".exe" if os.name == 'nt' else ""
    server_bin = os.path.join("bin", f"osi_server{exe_ext}")
    client_bin = os.path.join("bin", f"osi_client{exe_ext}")
    
    if not os.path.exists(server_bin) or not os.path.exists(client_bin):
        print(f"{Style.RED}[ERROR] C binaries not found in bin/. Please compile using 'make' or gcc first.{Style.RESET}")
        return
        
    print_banner()
    print(f"{Style.BOLD}{Style.BRIGHT_CYAN}[ORCHESTRATOR] Launching compiled C Server on port {port}...{Style.RESET}")
    srv_proc = subprocess.Popen([server_bin, str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.5)
    
    print(f"{Style.BOLD}{Style.BRIGHT_GREEN}[ORCHESTRATOR] Launching compiled C Client with message: \"{message}\"...{Style.RESET}\n")
    cli_proc = subprocess.run([client_bin, message, "127.0.0.1", str(port)], capture_output=True, text=True)
    
    print(f"{Style.BOLD}=== CLIENT LOGS ==={Style.RESET}")
    print(cli_proc.stdout)
    if cli_proc.stderr:
        print(f"{Style.RED}{cli_proc.stderr}{Style.RESET}")
        
    srv_out, srv_err = srv_proc.communicate(timeout=5)
    print(f"{Style.BOLD}=== SERVER LOGS ==={Style.RESET}")
    print(srv_out)
    if srv_err:
        print(f"{Style.RED}{srv_err}{Style.RESET}")

def main():
    parser = argparse.ArgumentParser(description="OSI 7-Layer Model Zig-Zag Flow Visualizer")
    parser.add_argument("-m", "--message", default="Hello OSI Model! Real Networking Simulation",
                        help="Application message to transmit")
    parser.add_argument("-s", "--speed", type=float, default=0.25,
                        help="Animation delay per layer in seconds")
    parser.add_argument("--live", action="store_true",
                        help="Execute real compiled C client and server binaries over socket")
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="Socket port number")
    
    args = parser.parse_args()
    
    if args.live:
        run_live_socket_workflow(args.message, args.port)
    else:
        run_simulation(args.message, args.speed)

if __name__ == "__main__":
    main()
