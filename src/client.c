#include "osi_layers.h"

int main(int argc, char *argv[]) {
    const char *message = "Hello OSI Network! Data travelling across 7 layers.";
    const char *server_ip = "127.0.0.1";
    int port = DEFAULT_PORT;

    if (argc > 1) {
        message = argv[1];
    }
    if (argc > 2) {
        server_ip = argv[2];
    }
    if (argc > 3) {
        port = atoi(argv[3]);
    }

    printf("\n" ANSI_BOLD ANSI_GREEN "================================================================" ANSI_RESET "\n");
    printf(ANSI_BOLD ANSI_GREEN "       OSI CLIENT (SENDER) - 7-LAYER ENCAPSULATION" ANSI_RESET "\n");
    printf(ANSI_BOLD ANSI_GREEN "================================================================" ANSI_RESET "\n");
    printf("Target Server: %s:%d\n", server_ip, port);
    printf("Original Message: \"%s\"\n\n", message);

    initialize_network_environment();

    char l7_buf[BUFFER_SIZE];
    char l6_buf[BUFFER_SIZE];
    char l5_buf[BUFFER_SIZE];
    char l4_buf[BUFFER_SIZE];
    char l3_buf[BUFFER_SIZE];
    char l2_buf[BUFFER_SIZE];
    char l1_bitstream[BITSTREAM_SIZE];

    printf(ANSI_BOLD "=== INITIATING DOWNWARD FLOW (L7 -> L1) ===\n\n" ANSI_RESET);

    // Layer 7: Application
    layer7_application_send(message, l7_buf, sizeof(l7_buf));
    print_zigzag_indicator(LAYER_7_APPLICATION, LAYER_6_PRESENTATION, "DOWNWARD");

    // Layer 6: Presentation
    layer6_presentation_send(l7_buf, l6_buf, sizeof(l6_buf));
    // Checkpoint 1 after every 2 layers (7 & 6)
    print_progress_checkpoint(1, "Layers 7 & 6 Completed: Application & Presentation Encapsulated", 1);

    print_zigzag_indicator(LAYER_6_PRESENTATION, LAYER_5_SESSION, "DOWNWARD");

    // Layer 5: Session
    layer5_session_send(l6_buf, l5_buf, sizeof(l5_buf));
    print_zigzag_indicator(LAYER_5_SESSION, LAYER_4_TRANSPORT, "DOWNWARD");

    // Layer 4: Transport
    layer4_transport_send(l5_buf, l4_buf, sizeof(l4_buf), 54321, (uint16_t)port);
    // Checkpoint 2 after every 2 layers (5 & 4)
    print_progress_checkpoint(2, "Layers 5 & 4 Completed: Session & Transport Encapsulated", 1);

    print_zigzag_indicator(LAYER_4_TRANSPORT, LAYER_3_NETWORK, "DOWNWARD");

    // Layer 3: Network
    layer3_network_send(l4_buf, l3_buf, sizeof(l3_buf), "192.168.1.100", "192.168.1.200");
    print_zigzag_indicator(LAYER_3_NETWORK, LAYER_2_DATALINK, "DOWNWARD");

    // Layer 2: Data Link
    layer2_datalink_send(l3_buf, l2_buf, sizeof(l2_buf), "00:1A:2B:3C:4D:5E", "AA:BB:CC:DD:EE:FF");
    // Checkpoint 3 after every 2 layers (3 & 2)
    print_progress_checkpoint(3, "Layers 3 & 2 Completed: Network & Data Link Encapsulated", 1);

    print_zigzag_indicator(LAYER_2_DATALINK, LAYER_1_PHYSICAL, "DOWNWARD");

    // Layer 1: Physical (bitstream)
    layer1_physical_send(l2_buf, l1_bitstream, sizeof(l1_bitstream));

    // Real Socket Communication (Transmission over physical medium)
    printf(ANSI_BOLD "\n=== TRANSMITTING THROUGH REAL SOCKET TO %s:%d ===\n" ANSI_RESET, server_ip, port);
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        fprintf(stderr, ANSI_RED "[ERROR] Could not create socket.\n" ANSI_RESET);
        cleanup_network_environment();
        return 1;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons((uint16_t)port);
    server_addr.sin_addr.s_addr = inet_addr(server_ip);

    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, ANSI_RED "[ERROR] Socket connection failed to %s:%d\n" ANSI_RESET, server_ip, port);
        CLOSE_SOCKET(sock);
        cleanup_network_environment();
        return 1;
    }

    size_t bitstream_len = strlen(l1_bitstream);
    uint32_t net_len = htonl((uint32_t)bitstream_len);
    send(sock, (const char *)&net_len, sizeof(net_len), 0);

    int sent_bytes = send(sock, l1_bitstream, (int)bitstream_len, 0);
    if (sent_bytes < 0) {
        fprintf(stderr, ANSI_RED "[ERROR] Socket send failed.\n" ANSI_RESET);
    } else {
        printf(ANSI_GREEN "[SOCKET] Successfully transmitted %d physical bit characters over the wire!\n" ANSI_RESET, sent_bytes);
    }

    // Checkpoint 4 after Layer 1 physical transmission
    print_progress_checkpoint(4, "Layer 1 Completed: Physical Bitstream Transmitted over Socket Medium", 1);

    // Wait for server acknowledgement
    char ack_buf[256];
    int recv_bytes = recv(sock, ack_buf, sizeof(ack_buf) - 1, 0);
    if (recv_bytes > 0) {
        ack_buf[recv_bytes] = '\0';
        printf(ANSI_BOLD ANSI_CYAN "[SERVER ACK] %s\n" ANSI_RESET, ack_buf);
    }

    CLOSE_SOCKET(sock);
    cleanup_network_environment();

    printf("\n" ANSI_BOLD ANSI_GREEN "=== CLIENT TRANSMISSION WORKFLOW COMPLETED SUCCESSFULLY ===" ANSI_RESET "\n\n");
    return 0;
}
