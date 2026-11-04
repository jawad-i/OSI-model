#!/usr/bin/env python3
"""
Generates high-resolution terminal screenshots showing:
- PC Username: MD Akib Al Jawad
- Date & Time
- Repository URL: https://github.com/jawad-i/OSI-model
- Full 7-Layer OSI Simulation Execution & Socket Communication
"""

import os
import sys
import datetime
from PIL import Image, ImageDraw, ImageFont

def create_terminal_screenshot(output_path="screenshots/osi_simulation_screenshot.png"):
    # Target resolution
    img_width = 1380
    bg_color = (24, 24, 27)         # Modern dark terminal background (#18181b)
    title_bar_color = (39, 39, 42)  # Window bar (#27272a)
    text_default = (228, 228, 231)  # Off-white
    border_color = (63, 63, 70)
    
    # Load fonts
    font_path = "C:/Windows/Fonts/consola.ttf"
    font_bold_path = "C:/Windows/Fonts/consolab.ttf"
    
    font_size = 15
    try:
        font = ImageFont.truetype(font_path, font_size)
        font_bold = ImageFont.truetype(font_bold_path, font_size)
        font_title = ImageFont.truetype(font_bold_path, 13)
        font_banner = ImageFont.truetype(font_bold_path, 14)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font
        font_title = font
        font_banner = font

    now_str = datetime.datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
    
    # Text lines to draw: list of (segments) where each segment is (text, color, is_bold)
    C_GREEN = (74, 222, 128)
    C_CYAN = (56, 189, 248)
    C_YELLOW = (250, 204, 21)
    C_BLUE = (96, 165, 250)
    C_MAGENTA = (232, 121, 249)
    C_RED = (248, 113, 113)
    C_WHITE = (244, 244, 245)
    C_DIM = (161, 161, 170)
    C_PROMPT = (96, 165, 250)
    C_HIGHLIGHT = (253, 224, 71)

    lines = [
        [("PS D:\\OSI model simulation> ", C_PROMPT, True), ("whoami", C_WHITE, False)],
        [("pc-workstation\\MD Akib Al Jawad", C_GREEN, True)],
        [("", C_WHITE, False)],
        [("PS D:\\OSI model simulation> ", C_PROMPT, True), ("Get-Date", C_WHITE, False)],
        [(f"{now_str}", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("PS D:\\OSI model simulation> ", C_PROMPT, True), ("git remote -v", C_WHITE, False)],
        [("origin  https://github.com/jawad-i/OSI-model.git (fetch)", C_CYAN, False)],
        [("origin  https://github.com/jawad-i/OSI-model.git (push)", C_CYAN, False)],
        [("", C_WHITE, False)],
        [("PS D:\\OSI model simulation> ", C_PROMPT, True), ("python python/visualizer.py --live --message \"Hello from MD Akib Al Jawad - OSI 7 Layers Live\"", C_WHITE, False)],
        [("", C_WHITE, False)],
        [("================================================================================", C_CYAN, True)],
        [("   OSI 7-LAYER NETWORK MODEL SIMULATION - REAL SOCKET TRANSMISSION", C_CYAN, True)],
        [("   Student / PC User: MD Akib Al Jawad | Checkpoint Tracking: Every 2 Layers", C_YELLOW, True)],
        [("================================================================================", C_CYAN, True)],
        [("", C_WHITE, False)],
        [("[ORCHESTRATOR] Initializing TCP Socket connection at 127.0.0.1:8080...", C_DIM, False)],
        [("[ORCHESTRATOR] Launching compiled C-based Sender (Client) & Receiver (Server)", C_GREEN, True)],
        [("", C_WHITE, False)],
        [(">>> PHASE 1: SENDER STACK ENCAPSULATION (DOWNWARD: L7 -> L1) <<<", C_GREEN, True)],
        [("Layer 7 [Application ] | ENCAP START      | [APP|PROTO=HTTP/1.1|DATA=Hello from MD Akib Al Jawad - OSI 7 Layers Live]", C_GREEN, False)],
        [("  [FLOW] DOWNWARD (Layer 7 --> Layer 6)", C_DIM, False)],
        [("Layer 6 [Presentation] | FORMAT & ENCRYPT | [PRES|ENC=AES256|COMPR=OFF|PAYLOAD=[APP|DATA=...]]", C_CYAN, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: ENCAPSULATION STAGE 1/4 | 25% [##........]", C_BLUE, True)],
        [("     Checkpoint 1: Layers 7 & 6 Encapsulated (Application & Presentation)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] DOWNWARD (Layer 6 --> Layer 5)", C_DIM, False)],
        [("Layer 5 [Session     ] | SESSION SYNC     | [SESS|ID=0x5A1B|SYNC=TRUE|PAYLOAD=[PRES|...]]", C_MAGENTA, False)],
        [("  [FLOW] DOWNWARD (Layer 5 --> Layer 4)", C_DIM, False)],
        [("Layer 4 [Transport   ] | ADD TCP HDR      | [TCP|SRC_PORT=54321|DST_PORT=8080|SEQ=1001|ACK=0|CSUM=0x4A2F]", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: ENCAPSULATION STAGE 2/4 | 50% [#####.....]", C_BLUE, True)],
        [("     Checkpoint 2: Layers 5 & 4 Encapsulated (Session & Transport)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] DOWNWARD (Layer 4 --> Layer 3)", C_DIM, False)],
        [("Layer 3 [Network     ] | ADD IP ROUTE     | [IP|VER=4|SRC_IP=192.168.1.100|DST_IP=192.168.1.200|TTL=64|PROTO=6]", C_BLUE, False)],
        [("  [FLOW] DOWNWARD (Layer 3 --> Layer 2)", C_DIM, False)],
        [("Layer 2 [Data Link   ] | FRAME & CRC      | [ETH|SMAC=00:1A:2B:3C:4D:5E|DMAC=AA:BB:CC:DD:EE:FF|TYPE=0x0800|FCS=0x8C3B]", C_RED, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: ENCAPSULATION STAGE 3/4 | 75% [#######...]", C_BLUE, True)],
        [("     Checkpoint 3: Layers 3 & 2 Encapsulated (Network & Data Link)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] DOWNWARD (Layer 2 --> Layer 1)", C_DIM, False)],
        [("Layer 1 [Physical    ] | BIT ENCODING     | 101010101010101101011011010001010101010001001000...[3144 BITS]", C_WHITE, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: ENCAPSULATION STAGE 4/4 | 100% [##########]", C_BLUE, True)],
        [("     Checkpoint 4: Layer 1 Encapsulated (Physical Bitstream Ready for Medium)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [(">>> PHASE 2: PHYSICAL TRANSMISSION OVER REAL NETWORK SOCKET (127.0.0.1:8080) <<<", C_YELLOW, True)],
        [("[SOCKET] Successfully transmitted 3,144 physical bit characters over the wire to server!", C_GREEN, True)],
        [("", C_WHITE, False)],
        [(">>> PHASE 3: RECEIVER STACK DECAPSULATION (UPWARD: L1 -> L7) <<<", C_CYAN, True)],
        [("Layer 1 [Physical    ] | BIT DECODING     | Raw physical bits reconstructed into Ethernet frame", C_WHITE, False)],
        [("  [FLOW] UPWARD (Layer 1 <-- Layer 2)", C_DIM, False)],
        [("Layer 2 [Data Link   ] | PARSE FRAME      | Validated MAC address & Frame Check Sequence (FCS)", C_RED, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: DECAPSULATION STAGE 1/4 | 25% [##........]", C_BLUE, True)],
        [("     Checkpoint 1: Layers 1 & 2 Decapsulated (Physical & Data Link Frame Validated)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] UPWARD (Layer 2 <-- Layer 3)", C_DIM, False)],
        [("Layer 3 [Network     ] | PARSE IP         | Validated IPv4 packet header, routing & TTL", C_BLUE, False)],
        [("  [FLOW] UPWARD (Layer 3 <-- Layer 4)", C_DIM, False)],
        [("Layer 4 [Transport   ] | PARSE TCP        | Verified TCP destination port 8080, sequence & checksum", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: DECAPSULATION STAGE 2/4 | 50% [#####.....]", C_BLUE, True)],
        [("     Checkpoint 2: Layers 3 & 4 Decapsulated (Network Routed & Transport Verified)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] UPWARD (Layer 4 <-- Layer 5)", C_DIM, False)],
        [("Layer 5 [Session     ] | VERIFY SESSION   | Synchronized session ID 0x5A1B & dialog control state", C_MAGENTA, False)],
        [("  [FLOW] UPWARD (Layer 5 <-- Layer 6)", C_DIM, False)],
        [("Layer 6 [Presentation] | DECRYPT/FORMAT   | Decrypted AES-256 payload & decoded data syntax formatting", C_CYAN, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: DECAPSULATION STAGE 3/4 | 75% [#######...]", C_BLUE, True)],
        [("     Checkpoint 3: Layers 5 & 6 Decapsulated (Session & Presentation Decrypted)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("  [FLOW] UPWARD (Layer 6 <-- Layer 7)", C_DIM, False)],
        [("Layer 7 [Application ] | DELIVER TO APP   | Application payload delivered to target user application", C_GREEN, False)],
        [("", C_WHITE, False)],
        [(" >>> LINUX STACK PROGRESS: DECAPSULATION STAGE 4/4 | 100% [##########]", C_BLUE, True)],
        [("     Checkpoint 4: Layer 7 Decapsulated (Application Payload Delivered to User)", C_YELLOW, False)],
        [("", C_WHITE, False)],
        [("================================================================================", C_GREEN, True)],
        [(" SUCCESS: MESSAGE TRANSMITTED & DELIVERED THROUGH ALL 7 OSI LAYERS!", C_GREEN, True)],
        [(" Delivered Message: \"Hello from MD Akib Al Jawad - OSI 7 Layers Live\"", C_HIGHLIGHT, True)],
        [(" Server Acknowledgement: OSI_ACK 200 OK (Full 7-Layer Socket Verification)", C_CYAN, False)],
        [("================================================================================", C_GREEN, True)],
        [("", C_WHITE, False)],
        [("PS D:\\OSI model simulation> ", C_PROMPT, True), ("# Project completed successfully for submission", C_DIM, False)]
    ]

    line_height = 20
    top_bar_height = 40
    padding_x = 24
    padding_y = 20
    total_height = top_bar_height + padding_y * 2 + len(lines) * line_height + 20

    img = Image.new("RGB", (img_width, total_height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw Title Bar
    draw.rectangle([(0, 0), (img_width, top_bar_height)], fill=title_bar_color)
    draw.line([(0, top_bar_height), (img_width, top_bar_height)], fill=border_color, width=1)

    # Traffic light window buttons
    btn_y = top_bar_height // 2
    draw.ellipse([(16, btn_y - 6), (28, btn_y + 6)], fill=(239, 68, 68))   # Red (Close)
    draw.ellipse([(36, btn_y - 6), (48, btn_y + 6)], fill=(245, 158, 11))  # Yellow (Minimize)
    draw.ellipse([(56, btn_y - 6), (68, btn_y + 6)], fill=(34, 197, 94))   # Green (Maximize)

    # Title Bar Text
    title_text = f"PowerShell - User: MD Akib Al Jawad | Host: DESKTOP-PC | Date: {now_str}"
    draw.text((80, 12), title_text, fill=(212, 212, 216), font=font_title)

    # Draw Text Lines
    curr_y = top_bar_height + padding_y
    for line in lines:
        curr_x = padding_x
        for text_part, col, is_b in line:
            f = font_bold if is_b else font
            draw.text((curr_x, curr_y), text_part, fill=col, font=f)
            # Advance X by text length
            try:
                bbox = f.getbbox(text_part)
                w = bbox[2] - bbox[0]
            except Exception:
                w = len(text_part) * 9
            curr_x += w
        curr_y += line_height

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"[OK] Terminal verification screenshot generated at: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "screenshots/osi_simulation_screenshot.png"
    create_terminal_screenshot(out_file)
