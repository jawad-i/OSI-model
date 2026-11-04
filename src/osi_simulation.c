#include "osi_layers.h"

int main(int argc, char *argv[]) {
    const char *message = "Hello OSI Network! Data travelling across 7 layers.";
    if (argc > 1) {
        message = argv[1];
    }

    printf("\n" ANSI_BOLD ANSI_CYAN "========================================================================\n" ANSI_RESET);
    printf(ANSI_BOLD ANSI_CYAN "         FULL OSI 7-LAYER END-TO-END SIMULATION PIPELINE\n" ANSI_RESET);
    printf(ANSI_BOLD ANSI_CYAN "========================================================================\n" ANSI_RESET);
    printf("Original Application Message: \"" ANSI_BOLD ANSI_YELLOW "%s" ANSI_RESET "\"\n\n", message);

    char l7_buf[BUFFER_SIZE];
    char l6_buf[BUFFER_SIZE];
    char l5_buf[BUFFER_SIZE];
    char l4_buf[BUFFER_SIZE];
    char l3_buf[BUFFER_SIZE];
    char l2_buf[BUFFER_SIZE];
    char l1_bitstream[BITSTREAM_SIZE];

    printf(ANSI_BOLD ANSI_BG_BLUE " >>> PHASE 1: SENDER ENCAPSULATION (DOWNWARD: L7 -> L1) <<< " ANSI_RESET "\n\n");

    // L7
    layer7_application_send(message, l7_buf, sizeof(l7_buf));
    print_zigzag_indicator(LAYER_7_APPLICATION, LAYER_6_PRESENTATION, "DOWNWARD");

    // L6
    layer6_presentation_send(l7_buf, l6_buf, sizeof(l6_buf));
    print_progress_checkpoint(1, "Layers 7 & 6 Encapsulated (Application & Presentation)", 1);

    print_zigzag_indicator(LAYER_6_PRESENTATION, LAYER_5_SESSION, "DOWNWARD");

    // L5
    layer5_session_send(l6_buf, l5_buf, sizeof(l5_buf));
    print_zigzag_indicator(LAYER_5_SESSION, LAYER_4_TRANSPORT, "DOWNWARD");

    // L4
    layer4_transport_send(l5_buf, l4_buf, sizeof(l4_buf), 54321, 8080);
    print_progress_checkpoint(2, "Layers 5 & 4 Encapsulated (Session & Transport)", 1);

    print_zigzag_indicator(LAYER_4_TRANSPORT, LAYER_3_NETWORK, "DOWNWARD");

    // L3
    layer3_network_send(l4_buf, l3_buf, sizeof(l3_buf), "192.168.1.100", "192.168.1.200");
    print_zigzag_indicator(LAYER_3_NETWORK, LAYER_2_DATALINK, "DOWNWARD");

    // L2
    layer2_datalink_send(l3_buf, l2_buf, sizeof(l2_buf), "00:1A:2B:3C:4D:5E", "AA:BB:CC:DD:EE:FF");
    print_progress_checkpoint(3, "Layers 3 & 2 Encapsulated (Network & Data Link)", 1);

    print_zigzag_indicator(LAYER_2_DATALINK, LAYER_1_PHYSICAL, "DOWNWARD");

    // L1
    layer1_physical_send(l2_buf, l1_bitstream, sizeof(l1_bitstream));
    print_progress_checkpoint(4, "Layer 1 Encapsulated (Physical Bitstream Ready)", 1);

    printf("\n" ANSI_BOLD ANSI_BG_GREEN " >>> PHASE 2: PHYSICAL TRANSMISSION OVER NETWORK MEDIUM <<< " ANSI_RESET "\n");
    printf(ANSI_GREEN "Transmitting %zu bits through physical communication channel...\n" ANSI_RESET, strlen(l1_bitstream));
    printf(ANSI_CYAN "[WIRE SIGNAL]: %s\n\n" ANSI_RESET, l1_bitstream);

    printf(ANSI_BOLD ANSI_BG_BLUE " >>> PHASE 3: RECEIVER DECAPSULATION (UPWARD: L1 -> L7) <<< " ANSI_RESET "\n\n");

    char rx_l2_frame[BUFFER_SIZE];
    char rx_l3_packet[BUFFER_SIZE];
    char rx_l4_segment[BUFFER_SIZE];
    char rx_l5_session[BUFFER_SIZE];
    char rx_l6_presentation[BUFFER_SIZE];
    char rx_l7_app[BUFFER_SIZE];
    char final_message[BUFFER_SIZE];

    // L1 -> L2
    layer1_physical_recv(l1_bitstream, rx_l2_frame, sizeof(rx_l2_frame));
    print_zigzag_indicator(LAYER_1_PHYSICAL, LAYER_2_DATALINK, "UPWARD");

    // L2 -> L3
    layer2_datalink_recv(rx_l2_frame, rx_l3_packet, sizeof(rx_l3_packet));
    print_progress_checkpoint(1, "Layers 1 & 2 Decapsulated (Physical & Data Link)", 0);

    print_zigzag_indicator(LAYER_2_DATALINK, LAYER_3_NETWORK, "UPWARD");

    // L3 -> L4
    layer3_network_recv(rx_l3_packet, rx_l4_segment, sizeof(rx_l4_segment));
    print_zigzag_indicator(LAYER_3_NETWORK, LAYER_4_TRANSPORT, "UPWARD");

    // L4 -> L5
    layer4_transport_recv(rx_l4_segment, rx_l5_session, sizeof(rx_l5_session));
    print_progress_checkpoint(2, "Layers 3 & 4 Decapsulated (Network & Transport)", 0);

    print_zigzag_indicator(LAYER_4_TRANSPORT, LAYER_5_SESSION, "UPWARD");

    // L5 -> L6
    layer5_session_recv(rx_l5_session, rx_l6_presentation, sizeof(rx_l6_presentation));
    print_zigzag_indicator(LAYER_5_SESSION, LAYER_6_PRESENTATION, "UPWARD");

    // L6 -> L7
    layer6_presentation_recv(rx_l6_presentation, rx_l7_app, sizeof(rx_l7_app));
    print_progress_checkpoint(3, "Layers 5 & 6 Decapsulated (Session & Presentation)", 0);

    print_zigzag_indicator(LAYER_6_PRESENTATION, LAYER_7_APPLICATION, "UPWARD");

    // L7
    layer7_application_recv(rx_l7_app, final_message, sizeof(final_message));
    print_progress_checkpoint(4, "Layer 7 Decapsulated (Application Payload Delivered)", 0);

    printf("\n" ANSI_BOLD ANSI_GREEN "========================================================================\n" ANSI_RESET);
    printf(ANSI_BOLD ANSI_GREEN " SUCCESS: MESSAGE DELIVERED ACROSS ALL 7 OSI LAYERS!\n" ANSI_RESET);
    printf(ANSI_BOLD ANSI_GREEN " Delivered Application Message: \"%s\"\n" ANSI_RESET, final_message);
    printf(ANSI_BOLD ANSI_GREEN "========================================================================\n\n" ANSI_RESET);

    return 0;
}
