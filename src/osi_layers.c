#include "osi_layers.h"

/* Simple 16-bit checksum calculation */
uint16_t calculate_checksum(const char *data) {
    uint32_t sum = 0;
    while (*data) {
        sum += (unsigned char)(*data++);
        if (sum > 0xFFFF) {
            sum = (sum & 0xFFFF) + (sum >> 16);
        }
    }
    return (uint16_t)(~sum & 0xFFFF);
}

void initialize_network_environment(void) {
#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) {
        fprintf(stderr, ANSI_RED "[ERROR] WSAStartup failed: %d\n" ANSI_RESET, WSAGetLastError());
        exit(EXIT_FAILURE);
    }
#endif
}

void cleanup_network_environment(void) {
#ifdef _WIN32
    WSACleanup();
#endif
}

void text_to_binary(const char *text, char *binary_out, size_t max_bits) {
    size_t bit_idx = 0;
    for (size_t i = 0; text[i] != '\0'; i++) {
        unsigned char c = (unsigned char)text[i];
        for (int b = 7; b >= 0; b--) {
            if (bit_idx + 1 >= max_bits) {
                binary_out[bit_idx] = '\0';
                return;
            }
            binary_out[bit_idx++] = (c & (1 << b)) ? '1' : '0';
        }
    }
    binary_out[bit_idx] = '\0';
}

void binary_to_text(const char *binary_in, char *text_out, size_t max_len) {
    size_t len = strlen(binary_in);
    size_t out_idx = 0;
    for (size_t i = 0; i + 8 <= len; i += 8) {
        if (out_idx + 1 >= max_len) break;
        unsigned char c = 0;
        for (int b = 0; b < 8; b++) {
            c = (c << 1) | (binary_in[i + b] - '0');
        }
        text_out[out_idx++] = (char)c;
    }
    text_out[out_idx] = '\0';
}

void log_layer_step(OSILayer layer, const char *action, const char *details) {
    const char *color = ANSI_RESET;
    const char *name = "Unknown";
    switch (layer) {
        case LAYER_7_APPLICATION:  color = ANSI_GREEN;   name = "Layer 7 [Application ]"; break;
        case LAYER_6_PRESENTATION: color = ANSI_CYAN;    name = "Layer 6 [Presentation]"; break;
        case LAYER_5_SESSION:      color = ANSI_MAGENTA; name = "Layer 5 [Session     ]"; break;
        case LAYER_4_TRANSPORT:    color = ANSI_YELLOW;  name = "Layer 4 [Transport   ]"; break;
        case LAYER_3_NETWORK:      color = ANSI_BLUE;    name = "Layer 3 [Network     ]"; break;
        case LAYER_2_DATALINK:     color = ANSI_RED;     name = "Layer 2 [Data Link   ]"; break;
        case LAYER_1_PHYSICAL:     color = ANSI_WHITE;   name = "Layer 1 [Physical    ]"; break;
    }
    printf("%s%s%s | %-16s | %s\n", color, name, ANSI_RESET, action, details);
}

void print_zigzag_indicator(OSILayer from_layer, OSILayer to_layer, const char *arrow_dir) {
    printf(ANSI_BOLD ANSI_CYAN "  [FLOW] %s (Layer %d %s Layer %d)\n" ANSI_RESET,
           arrow_dir, (int)from_layer, (from_layer > to_layer ? "-->" : "<--"), (int)to_layer);
}

void print_progress_checkpoint(int stage, const char *description, int is_encapsulation) {
    const char *type = is_encapsulation ? "ENCAPSULATION" : "DECAPSULATION";
    const char *pct = "";
    switch (stage) {
        case 1: pct = "25% [##........]"; break;
        case 2: pct = "50% [#####.....]"; break;
        case 3: pct = "75% [#######...]"; break;
        case 4: pct = "100% [##########]"; break;
    }
    printf("\n" ANSI_BOLD ANSI_BG_BLUE " >>> STACK PROGRESS: %s STAGE %d/4 | %s " ANSI_RESET "\n", type, stage, pct);
    printf(ANSI_YELLOW "     Checkpoint: %s\n" ANSI_RESET "\n", description);
}

/* ==================== ENCAPSULATION IMPLEMENTATION ==================== */

void layer7_application_send(const char *app_message, char *output, size_t max_len) {
    snprintf(output, max_len, "[APP|PROTO=HTTP/1.1|DATA=%s]", app_message);
    log_layer_step(LAYER_7_APPLICATION, "ENCAP START", output);
}

void layer6_presentation_send(const char *input, char *output, size_t max_len) {
    snprintf(output, max_len, "[PRES|ENC=AES256|COMPR=OFF|PAYLOAD=%s]", input);
    log_layer_step(LAYER_6_PRESENTATION, "FORMAT & ENCRYPT", output);
}

void layer5_session_send(const char *input, char *output, size_t max_len) {
    snprintf(output, max_len, "[SESS|ID=0x5A1B|SYNC=TRUE|PAYLOAD=%s]", input);
    log_layer_step(LAYER_5_SESSION, "SESSION SYNC", output);
}

void layer4_transport_send(const char *input, char *output, size_t max_len, uint16_t src_port, uint16_t dst_port) {
    uint16_t csum = calculate_checksum(input);
    snprintf(output, max_len, "[TCP|SRC_PORT=%u|DST_PORT=%u|SEQ=1001|ACK=0|CSUM=0x%04X|PAYLOAD=%s]",
             src_port, dst_port, csum, input);
    log_layer_step(LAYER_4_TRANSPORT, "ADD TCP HDR", output);
}

void layer3_network_send(const char *input, char *output, size_t max_len, const char *src_ip, const char *dst_ip) {
    snprintf(output, max_len, "[IP|VER=4|SRC_IP=%s|DST_IP=%s|TTL=64|PROTO=6|PAYLOAD=%s]",
             src_ip, dst_ip, input);
    log_layer_step(LAYER_3_NETWORK, "ADD IP ROUTE", output);
}

void layer2_datalink_send(const char *input, char *output, size_t max_len, const char *src_mac, const char *dst_mac) {
    uint16_t fcs = calculate_checksum(input);
    snprintf(output, max_len, "[ETH|SMAC=%s|DMAC=%s|TYPE=0x0800|FRAME=%s|FCS=0x%04X]",
             src_mac, dst_mac, input, fcs);
    log_layer_step(LAYER_2_DATALINK, "FRAME & CRC", output);
}

void layer1_physical_send(const char *frame, char *bitstream_out, size_t max_bits) {
    const char *preamble = "1010101010101011"; // 16-bit Preamble + SFD
    char data_bits[BITSTREAM_SIZE - 64];
    text_to_binary(frame, data_bits, sizeof(data_bits));
    snprintf(bitstream_out, max_bits, "%s%s", preamble, data_bits);

    char sample[65];
    strncpy(sample, bitstream_out, 48);
    sample[48] = '\0';
    strcat(sample, "...[BITS]");
    log_layer_step(LAYER_1_PHYSICAL, "BIT ENCODING", sample);
}

/* ==================== DECAPSULATION IMPLEMENTATION ==================== */

void layer1_physical_recv(const char *bitstream_in, char *frame_out, size_t max_len) {
    // Strip 16-bit Preamble/SFD if present
    const char *data_bits = bitstream_in;
    if (strncmp(bitstream_in, "1010101010101011", 16) == 0) {
        data_bits = bitstream_in + 16;
    }
    binary_to_text(data_bits, frame_out, max_len);
    log_layer_step(LAYER_1_PHYSICAL, "BIT DECODING", "Raw bits reconstructed into Ethernet frame");
}

void layer2_datalink_recv(const char *frame_in, char *packet_out, size_t max_len) {
    log_layer_step(LAYER_2_DATALINK, "PARSE FRAME", "Validating MAC address & Frame Check Sequence (FCS)");
    const char *start = strstr(frame_in, "|FRAME=");
    if (start) {
        start += 7;
        const char *end = strstr(start, "|FCS=");
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(packet_out, start, len);
            packet_out[len] = '\0';
            return;
        }
    }
    strncpy(packet_out, frame_in, max_len - 1);
    packet_out[max_len - 1] = '\0';
}

void layer3_network_recv(const char *packet_in, char *segment_out, size_t max_len) {
    log_layer_step(LAYER_3_NETWORK, "PARSE IP", "Validating IP version, TTL, and routing headers");
    const char *start = strstr(packet_in, "|PAYLOAD=");
    if (start) {
        start += 9;
        const char *end = strrchr(start, ']');
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(segment_out, start, len);
            segment_out[len] = '\0';
            return;
        }
    }
    strncpy(segment_out, packet_in, max_len - 1);
    segment_out[max_len - 1] = '\0';
}

void layer4_transport_recv(const char *segment_in, char *session_data_out, size_t max_len) {
    log_layer_step(LAYER_4_TRANSPORT, "PARSE TCP", "Validating port numbers, sequence, and TCP checksum");
    const char *start = strstr(segment_in, "|PAYLOAD=");
    if (start) {
        start += 9;
        const char *end = strrchr(start, ']');
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(session_data_out, start, len);
            session_data_out[len] = '\0';
            return;
        }
    }
    strncpy(session_data_out, segment_in, max_len - 1);
    session_data_out[max_len - 1] = '\0';
}

void layer5_session_recv(const char *session_data_in, char *pres_data_out, size_t max_len) {
    log_layer_step(LAYER_5_SESSION, "VERIFY SESSION", "Verifying session ID, dialog control, and sync token");
    const char *start = strstr(session_data_in, "|PAYLOAD=");
    if (start) {
        start += 9;
        const char *end = strrchr(start, ']');
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(pres_data_out, start, len);
            pres_data_out[len] = '\0';
            return;
        }
    }
    strncpy(pres_data_out, session_data_in, max_len - 1);
    pres_data_out[max_len - 1] = '\0';
}

void layer6_presentation_recv(const char *pres_data_in, char *app_data_out, size_t max_len) {
    log_layer_step(LAYER_6_PRESENTATION, "DECRYPT/FORMAT", "Decrypted AES256 payload & decoded data syntax");
    const char *start = strstr(pres_data_in, "|PAYLOAD=");
    if (start) {
        start += 9;
        const char *end = strrchr(start, ']');
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(app_data_out, start, len);
            app_data_out[len] = '\0';
            return;
        }
    }
    strncpy(app_data_out, pres_data_in, max_len - 1);
    app_data_out[max_len - 1] = '\0';
}

void layer7_application_recv(const char *app_data_in, char *final_message_out, size_t max_len) {
    log_layer_step(LAYER_7_APPLICATION, "DELIVER TO APP", "Application payload ready for user consumption");
    const char *start = strstr(app_data_in, "|DATA=");
    if (start) {
        start += 6;
        const char *end = strrchr(start, ']');
        if (end) {
            size_t len = (size_t)(end - start);
            if (len >= max_len) len = max_len - 1;
            strncpy(final_message_out, start, len);
            final_message_out[len] = '\0';
            return;
        }
    }
    strncpy(final_message_out, app_data_in, max_len - 1);
    final_message_out[max_len - 1] = '\0';
}
