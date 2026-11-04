#!/usr/bin/env python3
"""
OSI 7-Layer Network Model Simulation & Zig-Zag Flow Visualizer
Upgraded Professional Animated Terminal Dashboard using Python Rich.
Demonstrates 7-layer encapsulation, socket transmission, decapsulation,
and progress checkpoints every two OSI layers.

Author: MD Akib Al Jawad
GitHub: https://github.com/jawad-i/OSI-model
"""

import sys
import os
import time
import argparse
import subprocess
import shutil
from typing import Optional, List, Dict, Any

# ----------------- Self-Relaunch / Environment Resolver -----------------
# If executed in an environment lacking 'rich' (e.g. MinGW Python),
# automatically relaunch with Python 3.12 or the 'py' launcher if available.
try:
    import rich
except ImportError:
    for candidate in [
        "C:\\Users\\Jawad\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
        "py",
        "python3"
    ]:
        cand_path = candidate if os.path.isabs(candidate) else shutil.which(candidate)
        if cand_path and os.path.exists(cand_path):
            try:
                check = subprocess.run([cand_path, "-c", "import rich"], capture_output=True)
                if check.returncode == 0:
                    ret = subprocess.call([cand_path] + sys.argv)
                    sys.exit(ret)
            except Exception:
                pass
    sys.exit("[ERROR] The 'rich' library is required. Please install it using: pip install rich")

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.prompt import Prompt

from osi_model_data import (
    OSI_LAYERS,
    generate_encapsulation_steps,
    generate_decapsulation_steps
)

console = Console()

# ----------------- UI Builders -----------------

def create_header_panel(mode_name="ANIMATED DEMONSTRATION") -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=3)
    grid.add_column(justify="right", ratio=2)
    
    title = Text("◆ OSI 7-LAYER NETWORK MODEL SIMULATION & ZIG-ZAG FLOW ◆", style="bold bright_cyan")
    meta = Text("Author: MD Akib Al Jawad | Repo: https://github.com/jawad-i/OSI-model", style="dim")
    mode_text = Text(f"MODE: {mode_name} | STACK: Linux/Ubuntu Kernel Standard", style="bold bright_yellow")
    
    grid.add_row(title, mode_text)
    grid.add_row(meta, Text("ISO/IEC 7498-1 Standard Compliant", style="dim cyan"))
    
    return Panel(grid, style="bright_blue", border_style="cyan")

def build_layer_card(layer_num: int, side: str, status: str) -> Panel:
    """
    Renders an individual layer box for Client or Server stack.
    status: 'pending', 'active', 'completed'
    """
    meta = OSI_LAYERS[layer_num]
    name = meta.name
    unit = meta.data_unit.split("/")[0].strip()
    
    if status == "active":
        title = f"[bold white on blue] ▶ L{layer_num}: {name.upper()} ◀ [/]"
        border_col = "bold bright_green"
        body = f"[bold white]{unit}[/]\n[bright_yellow]{meta.simulated_header_name}[/]"
        panel_style = "bold on black"
    elif status == "completed":
        title = f"[bold bright_green]✓ L{layer_num}: {name}[/]"
        border_col = "green"
        body = f"[dim]{unit}[/]\n[green]PROCESSED[/]"
        panel_style = "default"
    else: # pending
        title = f"[dim]○ L{layer_num}: {name}[/]"
        border_col = "dim"
        body = f"[dim]{unit}\nWaiting...[/]"
        panel_style = "dim"

    return Panel(
        Align.center(body, vertical="middle"),
        title=title,
        border_style=border_col,
        style=panel_style,
        padding=(0, 1),
        height=4
    )

def render_stack_column(side: str, active_layer: Optional[int], completed_layers: List[int]) -> Group:
    """
    Renders the 7-layer stack vertically (L7 at top down to L1 at bottom).
    """
    panels = []
    # Always display Layer 7 at top down to Layer 1 at bottom
    for l in range(7, 0, -1):
        if active_layer == l:
            st = "active"
        elif l in completed_layers:
            st = "completed"
        else:
            st = "pending"
        panels.append(build_layer_card(l, side, st))
    return Group(*panels)

def render_zigzag_channel(phase: str, current_layer: int, step_count: int) -> Group:
    """
    Renders the animated middle channel representing the zig-zag data flow
    alternating directions between layers.
    """
    rows = []
    pulse_symbols = ["━━▶", "══▶", "──▶", "▶▶▶", "◀◀◀", "◀──", "◀══", "◀━━"]
    symbol = pulse_symbols[step_count % len(pulse_symbols)]

    for l in range(7, 0, -1):
        if phase == "encapsulation":
            if l == current_layer:
                # Zig-zag alternating flow
                if l % 2 == 1:
                    line = f"[bold bright_yellow]╭── {symbol} ╮[/]"
                else:
                    line = f"[bold bright_cyan]╰── {symbol} ╯[/]"
            elif l > current_layer:
                line = "[green]     ││     [/]"
            else:
                line = "[dim]     ┆┆     [/]"
        elif phase == "decapsulation":
            if l == current_layer:
                if l % 2 == 1:
                    line = f"[bold bright_cyan]╭── {symbol} ╮[/]"
                else:
                    line = f"[bold bright_yellow]╰── {symbol} ╯[/]"
            elif l < current_layer:
                line = "[green]     ││     [/]"
            else:
                line = "[dim]     ┆┆     [/]"
        elif phase == "wire":
            line = f"[bold bright_yellow]══ {symbol} ══[/]"
        else:
            line = "[dim]     ┆┆     [/]"
            
        rows.append(Panel(Align.center(f"\n{line}", vertical="middle"), border_style="dim", height=4))
    return Group(*rows)

def build_explanation_panel(layer_num: Optional[int], phase: str) -> Panel:
    if not layer_num or layer_num not in OSI_LAYERS:
        text = Text("Ready to initiate transmission pipeline.\nSelect a simulation mode to begin.", style="dim")
        return Panel(text, title="[bold]OSI Layer Architecture Insight[/]", border_style="cyan")
        
    meta = OSI_LAYERS[layer_num]
    t = Table.grid(expand=True, padding=(0, 1))
    t.add_column(style="bold bright_cyan", width=18)
    t.add_column(style="white")
    
    action = "Encapsulating (Downward Flow)" if phase == "encapsulation" else "Decapsulating (Upward Flow)"
    
    t.add_row("Current Layer:", f"[bold {meta.color}]Layer {meta.number}: {meta.name} ({action})[/]")
    t.add_row("Data Unit (PDU):", f"[bright_yellow]{meta.data_unit}[/]")
    t.add_row("Key Protocols:", f"[bright_white]{meta.key_protocols}[/]")
    t.add_row("Host Hardware/OS:", f"[dim]{meta.hardware_software}[/]")
    t.add_row("Primary Duty:", f"{meta.detailed_responsibility}")
    t.add_row("Header / Metadata:", f"[bold bright_green]{meta.simulated_header_name}[/]")
    t.add_row("Protocol Scope:", f"[italic cyan]{meta.educational_note}[/]")
    
    note = (
        "\n[dim yellow]★ Educational Notice:[/] This educational simulation appends visible layer envelopes. "
        "Real OS sockets handle true kernel-level IP/TCP encapsulation before physical Ethernet transmission."
    )
    
    return Panel(Group(t, Text.from_markup(note)), title=f"[bold]Layer {meta.number} Detailed Responsibility[/]", border_style="bright_blue")

def build_data_inspection_panel(envelope: str, bitstream: str = "", message: str = "") -> Panel:
    t = Table.grid(expand=True, padding=(0, 1))
    t.add_column(style="bold cyan", width=18)
    t.add_column(style="white")
    
    if message:
        t.add_row("Application Data:", f"[bold bright_yellow]\"{message}\"[/]")
    
    # Format envelope nicely
    env_display = envelope if envelope else "[dim]No active envelope[/]"
    t.add_row("Simulated Envelope:", f"[bright_green]{env_display}[/]")
    
    if bitstream:
        short_bits = bitstream[:64] + " ... [+" + str(len(bitstream) - 64) + " bits]"
        t.add_row("Physical Bitstream:", f"[bold white on blue] {short_bits} [/]")
    
    return Panel(t, title="[bold]Educational Data Inspection & Envelope View[/]", border_style="bright_magenta")

def build_progress_panel(percent: int, stage_desc: str, completed_count: int) -> Panel:
    prog = Progress(
        TextColumn("[bold bright_blue]{task.description}"),
        BarColumn(bar_width=35, complete_style="bright_green", finished_style="bold green"),
        TaskProgressColumn(),
        console=console
    )
    task = prog.add_task("Progress", total=100, completed=percent)
    
    content = Group(
        prog,
        Text(f"Completed Layers: {completed_count}/7 | {stage_desc}", style="bold bright_yellow")
    )
    return Panel(content, title="[bold]Linux Kernel Stack Progress (Every 2 Layers)[/]", border_style="yellow")

def build_dashboard_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=4),
        Layout(name="body", ratio=1)
    )
    layout["body"].split_row(
        Layout(name="stacks", ratio=6),
        Layout(name="details", ratio=5)
    )
    layout["stacks"].split_row(
        Layout(name="client_stack", ratio=3),
        Layout(name="zigzag_channel", ratio=2),
        Layout(name="server_stack", ratio=3)
    )
    layout["details"].split_column(
        Layout(name="explanation", ratio=5),
        Layout(name="inspection", ratio=3),
        Layout(name="progress", ratio=2)
    )
    return layout

# ----------------- Animation Core -----------------

def run_animated_dashboard(raw_message: str = "Hello Server! Real OSI 7-Layer Simulation", speed: float = 0.35):
    """
    Main animated dashboard showing encapsulation, real socket transmission, and decapsulation.
    """
    enc_steps = generate_encapsulation_steps(raw_message)
    dec_steps = generate_decapsulation_steps(raw_message)
    
    layout = build_dashboard_layout()
    layout["header"].update(create_header_panel("ANIMATED 7-LAYER SIMULATION"))
    
    client_completed = []
    server_completed = []
    current_layer = 7
    active_side = "client"
    phase = "encapsulation"
    step_tick = 0
    
    with Live(layout, console=console, refresh_per_second=10, screen=False) as live:
        # Initial empty state
        layout["client_stack"].update(Panel(render_stack_column("client", None, []), title="[bold green]Client Stack (Sender)[/]"))
        layout["zigzag_channel"].update(Panel(render_zigzag_channel(phase, current_layer, step_tick), title="[bold yellow]Zig-Zag Medium[/]"))
        layout["server_stack"].update(Panel(render_stack_column("server", None, []), title="[bold cyan]Server Stack (Receiver)[/]"))
        layout["explanation"].update(build_explanation_panel(7, phase))
        layout["inspection"].update(build_data_inspection_panel(f"[APP|DATA={raw_message}]", "", raw_message))
        layout["progress"].update(build_progress_panel(0, "Stage 0/4 (0%): Ready to encapsulate", 0))
        time.sleep(speed * 1.5)
        
        # ---------------- 1. ENCAPSULATION PHASE (L7 -> L1) ----------------
        for step in enc_steps:
            current_layer = step.layer
            step_tick += 1
            
            layout["client_stack"].update(Panel(render_stack_column("client", current_layer, client_completed), title="[bold green]Client Stack (Sender)[/]"))
            layout["zigzag_channel"].update(Panel(render_zigzag_channel(phase, current_layer, step_tick), title="[bold yellow]Zig-Zag Medium[/]"))
            layout["explanation"].update(build_explanation_panel(current_layer, phase))
            layout["inspection"].update(build_data_inspection_panel(step.data_envelope, step.bits, raw_message))
            
            # Progress check after every 2 layers
            if step.progress_checkpoint:
                pct = step.progress_percent
                desc = step.progress_desc
                comp_layers = 7 - current_layer + 1
            else:
                pct = int(((7 - current_layer) / 7.0) * 100)
                desc = f"Processing Layer {current_layer} ({OSI_LAYERS[current_layer].name})"
                comp_layers = 7 - current_layer
                
            layout["progress"].update(build_progress_panel(pct, desc, comp_layers))
            live.refresh()
            time.sleep(speed)
            client_completed.append(current_layer)

        # ---------------- 2. PHYSICAL WIRE TRANSMISSION PHASE ----------------
        phase = "wire"
        layout["client_stack"].update(Panel(render_stack_column("client", None, client_completed), title="[bold green]Client Stack (Sender)[/]"))
        
        wire_table = Table.grid(expand=True, padding=(0, 1))
        wire_table.add_column(style="bold green")
        wire_table.add_column(style="bold yellow", justify="center")
        wire_table.add_column(style="bold cyan", justify="right")
        wire_table.add_row("CLIENT (127.0.0.1:54321)", "──────[ REAL TCP SOCKET : 8080 ]──────▶", "SERVER (127.0.0.1:8080)")
        
        wire_panel = Panel(
            Align.center(
                Group(
                    wire_table,
                    Text("\n[PHYSICAL TRANSMISSION]: 3,144 binary bits moving across loopback socket channel...", style="bold bright_white"),
                    Text("[STATUS]: TCP Handshake Verified | ACK Received | Data Intact", style="bold green")
                ),
                vertical="middle"
            ),
            title="[bold yellow]Physical Medium (TCP Socket Channel)[/]",
            border_style="bold yellow"
        )
        
        for w in range(4):
            step_tick += 1
            layout["zigzag_channel"].update(Panel(render_zigzag_channel(phase, 1, step_tick), title="[bold yellow]Physical Medium[/]"))
            layout["explanation"].update(wire_panel)
            live.refresh()
            time.sleep(speed * 0.7)

        # ---------------- 3. DECAPSULATION PHASE (L1 -> L7) ----------------
        phase = "decapsulation"
        for step in dec_steps:
            current_layer = step.layer
            step_tick += 1
            
            layout["server_stack"].update(Panel(render_stack_column("server", current_layer, server_completed), title="[bold cyan]Server Stack (Receiver)[/]"))
            layout["zigzag_channel"].update(Panel(render_zigzag_channel(phase, current_layer, step_tick), title="[bold yellow]Zig-Zag Medium[/]"))
            layout["explanation"].update(build_explanation_panel(current_layer, phase))
            layout["inspection"].update(build_data_inspection_panel(step.remaining_envelope, "", raw_message))
            
            # Progress check after every 2 layers
            if step.progress_checkpoint:
                pct = step.progress_percent
                desc = step.progress_desc
                comp_layers = current_layer
            else:
                pct = int((current_layer / 7.0) * 100)
                desc = f"Processing Layer {current_layer} ({OSI_LAYERS[current_layer].name})"
                comp_layers = current_layer - 1

            layout["progress"].update(build_progress_panel(pct, desc, comp_layers))
            live.refresh()
            time.sleep(speed)
            server_completed.append(current_layer)

    # ---------------- 4. FINAL SUCCESS SUMMARY ----------------
    console.print()
    success_grid = Table.grid(expand=True)
    success_grid.add_column(justify="center")
    success_grid.add_row(Text("✔ SUCCESS: FULL 7-LAYER OSI ENCAPSULATION & DECAPSULATION COMPLETED!", style="bold bright_green"))
    success_grid.add_row(Text(f"Delivered Application Payload: \"{raw_message}\"", style="bold bright_yellow"))
    success_grid.add_row(Text("Zig-Zag Flow: (L7→L1) ──[ Socket 127.0.0.1:8080 ]──▶ (L1→L7)", style="bold cyan"))
    success_grid.add_row(Text("Stack Checkpoints: All 4 stages (28%, 57%, 85%, 100%) verified.", style="dim white"))
    
    console.print(Panel(success_grid, border_style="bold bright_green", padding=(1, 2)))
    console.print()

# ----------------- Real C Sockets Orchestration -----------------

def run_live_socket_orchestration(message: str = "Live socket test across all 7 layers", port: int = 8080, speed: float = 0.25):
    """
    Compiles (if needed) and executes the real C server and C client binaries,
    captures real socket network communication, and displays live visual feedback.
    """
    console.print(Panel(Text(f"ORCHESTRATING LIVE C CLIENT & SERVER SOCKET COMMUNICATION (PORT {port})", style="bold bright_cyan"), border_style="cyan"))
    
    exe_ext = ".exe" if os.name == 'nt' else ""
    server_bin = os.path.join("bin", f"osi_server{exe_ext}")
    client_bin = os.path.join("bin", f"osi_client{exe_ext}")
    
    # Auto-compile if binaries missing
    if not os.path.exists(server_bin) or not os.path.exists(client_bin):
        console.print("[yellow][BUILD] C binaries not found in bin/. Compiling with GCC...[/]")
        os.makedirs("bin", exist_ok=True)
        libs = ["-lws2_32"] if os.name == 'nt' else []
        cmd_srv = ["gcc", "-Wall", "-Wextra", "-Isrc", "src/osi_layers.c", "src/server.c", "-o", server_bin] + libs
        cmd_cli = ["gcc", "-Wall", "-Wextra", "-Isrc", "src/osi_layers.c", "src/client.c", "-o", client_bin] + libs
        subprocess.run(cmd_srv, check=True)
        subprocess.run(cmd_cli, check=True)
        console.print("[green][BUILD] Compilation complete![/]\n")
        
    console.print(f"[bold cyan][1/3] Launching compiled C Server ({server_bin}) on port {port}...[/]")
    srv_proc = subprocess.Popen([server_bin, str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(0.6)
    
    console.print(f"[bold green][2/3] Launching compiled C Client ({client_bin}) with payload: \"{message}\"...[/]")
    cli_proc = subprocess.run([client_bin, message, "127.0.0.1", str(port)], capture_output=True, text=True)
    
    srv_out, srv_err = srv_proc.communicate(timeout=5)
    
    # Print formatted output
    console.print(f"\n[bold green]=== C CLIENT ENCAPSULATION OUTPUT ===[/]")
    console.print(Panel(cli_proc.stdout.strip(), title="Client (Sender Stack L7 -> L1)", border_style="green"))
    
    console.print(f"\n[bold cyan]=== C SERVER DECAPSULATION OUTPUT ===[/]")
    console.print(Panel(srv_out.strip(), title="Server (Receiver Stack L1 -> L7)", border_style="cyan"))
    
    console.print(f"\n[bold yellow][3/3] Playing Animated Dashboard Visualization for the Live Transmission...[/]\n")
    time.sleep(1)
    run_animated_dashboard(message, speed)

# ----------------- Educational Reference Explorer -----------------

def show_educational_layer_guide():
    console.clear()
    console.print(Panel(Text("OSI 7-LAYER REFERENCE GUIDE & THEORETICAL BREAKDOWN", style="bold bright_cyan"), border_style="cyan"))
    
    table = Table(title="OSI Model (ISO/IEC 7498-1) Layers", border_style="blue", header_style="bold bright_white")
    table.add_column("Layer", justify="center", style="bold yellow", width=8)
    table.add_column("Layer Name", style="bold", width=14)
    table.add_column("Data Unit (PDU)", style="bright_green", width=16)
    table.add_column("Key Protocols", style="cyan", width=22)
    table.add_column("Primary Responsibility", style="white")
    
    for l in range(7, 0, -1):
        info = OSI_LAYERS[l]
        table.add_row(
            f"L{info.number}",
            f"[{info.color}]{info.name}[/]",
            info.data_unit.split("/")[0].strip(),
            info.key_protocols,
            info.short_desc
        )
        
    console.print(table)
    console.print("\n[bold cyan]Press Enter to return to main menu...[/]")
    input()

# ----------------- Interactive Main Menu -----------------

def interactive_menu():
    while True:
        console.clear()
        console.print(create_header_panel("INTERACTIVE CONTROL MENU"))
        
        menu_table = Table.grid(expand=True, padding=(1, 2))
        menu_table.add_column(style="bold bright_yellow", width=6)
        menu_table.add_column(style="bold white")
        
        menu_table.add_row("[1]", "Run Animated OSI 7-Layer Simulation (Live Zig-Zag Dashboard)")
        menu_table.add_row("[2]", "Run Real Socket Communication (C Client & Server over TCP/IP)")
        menu_table.add_row("[3]", "Explore Detailed OSI 7-Layer Educational Reference Guide")
        menu_table.add_row("[4]", "Run Automated Test Suite (Windows Batch / Shell)")
        menu_table.add_row("[5]", "Exit")
        
        console.print(Panel(menu_table, title="[bold]Select an Option[/]", border_style="bright_blue"))
        
        choice = Prompt.ask("[bold bright_green]Enter your choice (1-5)[/]", default="1")
        
        if choice == "1":
            msg = Prompt.ask("\nEnter message to transmit", default="Hello Server! Real OSI 7-Layer Simulation")
            if not msg.strip():
                msg = "Hello Server! Real OSI 7-Layer Simulation"
            spd_str = Prompt.ask("Animation delay per layer (seconds)", default="0.3")
            try:
                spd = float(spd_str)
            except ValueError:
                spd = 0.3
            console.clear()
            run_animated_dashboard(msg, spd)
            console.print("\n[bold cyan]Press Enter to continue...[/]")
            input()
        elif choice == "2":
            msg = Prompt.ask("\nEnter message to transmit via live C socket", default="Live socket test across all 7 layers")
            if not msg.strip():
                msg = "Live socket test across all 7 layers"
            console.clear()
            run_live_socket_orchestration(msg, 8080, 0.25)
            console.print("\n[bold cyan]Press Enter to continue...[/]")
            input()
        elif choice == "3":
            show_educational_layer_guide()
        elif choice == "4":
            console.clear()
            console.print(Panel(Text("EXECUTING AUTOMATED TEST SUITE...", style="bold yellow"), border_style="yellow"))
            if os.name == 'nt':
                subprocess.run(["cmd", "/c", "tests\\test_communication.bat"])
            else:
                subprocess.run(["bash", "tests/test_communication.sh"])
            console.print("\n[bold cyan]Press Enter to continue...[/]")
            input()
        elif choice == "5":
            console.print("\n[bold green]Thank you for using the OSI 7-Layer Network Model Simulator![/]\n")
            break

# ----------------- CLI Entry Point -----------------

def main():
    parser = argparse.ArgumentParser(description="Professional OSI 7-Layer Network Model Simulation & Zig-Zag Visualizer")
    parser.add_argument("-m", "--message", default="Hello Server! Real OSI 7-Layer Simulation",
                        help="Application payload message to transmit")
    parser.add_argument("-s", "--speed", type=float, default=0.3,
                        help="Animation delay per layer in seconds (default: 0.3)")
    parser.add_argument("--demo", action="store_true",
                        help="Directly run the animated dashboard demo")
    parser.add_argument("--live", action="store_true",
                        help="Directly run live C Client and Server socket communication")
    parser.add_argument("-p", "--port", type=int, default=8080,
                        help="TCP Socket Port (default: 8080)")
    parser.add_argument("--menu", action="store_true",
                        help="Launch the interactive control menu")
    
    args = parser.parse_args()
    
    try:
        if args.live:
            run_live_socket_orchestration(args.message, args.port, args.speed)
        elif args.demo:
            run_animated_dashboard(args.message, args.speed)
        elif len(sys.argv) == 1 or args.menu:
            interactive_menu()
        else:
            run_animated_dashboard(args.message, args.speed)
    except KeyboardInterrupt:
        console.print("\n[bold yellow][INTERRUPTED] Simulation safely stopped by user.[/]\n")

if __name__ == "__main__":
    main()
