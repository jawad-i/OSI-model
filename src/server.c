#include "osi_layers.h"

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;
    int run_once = 1; // Default to single run for tests/scripts; pass -c or --continuous to keep running

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-c") == 0 || strcmp(argv[i], "--continuous") == 0) {
            run_once = 0;
        } else if (atoi(argv[i]) > 0) {
            port = atoi(argv[i]);
        }
    }

    printf("\n" ANSI_BOLD ANSI_CYAN "================================================================" ANSI_RESET "\n");
    printf(ANSI_BOLD ANSI_CYAN "       OSI SERVER (RECEIVER) - 7-LAYER DECAPSULATION" ANSI_RESET "\n");
    printf(ANSI_BOLD ANSI_CYAN "================================================================" ANSI_RESET "\n");
    printf("Listening on port: %d (Mode: %s)\n\n", port, run_once ? "Single Request" : "Continuous Service");

    initialize_network_environment();

    SOCKET listen_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_sock == INVALID_SOCKET) {
        fprintf(stderr, ANSI_RED "[ERROR] Could not create server socket.\n" ANSI_RESET);
        cleanup_network_environment();
        return 1;
    }

    int opt = 1;
#ifdef _WIN32
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, (const char *)&opt, sizeof(opt));
#else
    setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons((uint16_t)port);

    if (bind(listen_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, ANSI_RED "[ERROR] Socket bind failed on port %d.\n" ANSI_RESET, port);
        CLOSE_SOCKET(listen_sock);
        cleanup_network_environment();
        return 1;
    }

    if (listen(listen_sock, 5) < 0) {
        fprintf(stderr, ANSI_RED "[ERROR] Socket listen failed.\n" ANSI_RESET);
        CLOSE_SOCKET(listen_sock);
        cleanup_network_environment();
        return 1;
    }

    printf(ANSI_YELLOW "[SERVER] Waiting for incoming OSI physical transmission on port %d...\n" ANSI_RESET, port);
    fflush(stdout);

    do {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        SOCKET client_sock = accept(listen_sock, (struct sockaddr *)&client_addr, &client_len);
        if (client_sock == INVALID_SOCKET) {
            fprintf(stderr, ANSI_RED "[ERROR] Accept failed.\n" ANSI_RESET);
            break;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
        printf(ANSI_GREEN "\n[SOCKET CONNECTED] Client connected from %s:%d\n" ANSI_RESET,
               client_ip, ntohs(client_addr.sin_port));

        char bitstream_in[BITSTREAM_SIZE];
        uint32_t net_len = 0;
        int len_bytes = recv(client_sock, (char *)&net_len, sizeof(net_len), 0);
        if (len_bytes <= 0) {
            fprintf(stderr, ANSI_RED "[WARNING] Client disconnected before sending frame length.\n" ANSI_RESET);
            CLOSE_SOCKET(client_sock);
            continue;
        }
        uint32_t expected_len = ntohl(net_len);
        if (expected_len >= BITSTREAM_SIZE) {
            expected_len = BITSTREAM_SIZE - 1;
        }

        uint32_t total_recv = 0;
        while (total_recv < expected_len) {
            int bytes = recv(client_sock, bitstream_in + total_recv, expected_len - total_recv, 0);
            if (bytes <= 0) break;
            total_recv += bytes;
        }

        if (total_recv == 0) {
            fprintf(stderr, ANSI_RED "[WARNING] No data received from client.\n" ANSI_RESET);
            CLOSE_SOCKET(client_sock);
            continue;
        }

        bitstream_in[total_recv] = '\0';
        printf(ANSI_CYAN "[SOCKET RECV] Received %u physical bit characters from wire (expected: %u)\n\n" ANSI_RESET, total_recv, expected_len);

        printf(ANSI_BOLD "=== INITIATING UPWARD DECAPSULATION FLOW (L1 -> L7) ===\n\n" ANSI_RESET);

        char l2_frame[BUFFER_SIZE];
        char l3_packet[BUFFER_SIZE];
        char l4_segment[BUFFER_SIZE];
        char l5_session[BUFFER_SIZE];
        char l6_presentation[BUFFER_SIZE];
        char l7_app_data[BUFFER_SIZE];
        char final_message[BUFFER_SIZE];

        // Layer 1: Physical
        layer1_physical_recv(bitstream_in, l2_frame, sizeof(l2_frame));
        print_zigzag_indicator(LAYER_1_PHYSICAL, LAYER_2_DATALINK, "UPWARD");

        // Layer 2: Data Link
        layer2_datalink_recv(l2_frame, l3_packet, sizeof(l3_packet));
        // Checkpoint 1 after every 2 layers (1 & 2)
        print_progress_checkpoint(1, "Layers 1 & 2 Completed: Physical Reconstructed & Data Link Validated", 0);

        print_zigzag_indicator(LAYER_2_DATALINK, LAYER_3_NETWORK, "UPWARD");

        // Layer 3: Network
        layer3_network_recv(l3_packet, l4_segment, sizeof(l4_segment));
        print_zigzag_indicator(LAYER_3_NETWORK, LAYER_4_TRANSPORT, "UPWARD");

        // Layer 4: Transport
        layer4_transport_recv(l4_segment, l5_session, sizeof(l5_session));
        // Checkpoint 2 after every 2 layers (3 & 4)
        print_progress_checkpoint(2, "Layers 3 & 4 Completed: Network Routed & Transport Verified", 0);

        print_zigzag_indicator(LAYER_4_TRANSPORT, LAYER_5_SESSION, "UPWARD");

        // Layer 5: Session
        layer5_session_recv(l5_session, l6_presentation, sizeof(l6_presentation));
        print_zigzag_indicator(LAYER_5_SESSION, LAYER_6_PRESENTATION, "UPWARD");

        // Layer 6: Presentation
        layer6_presentation_recv(l6_presentation, l7_app_data, sizeof(l7_app_data));
        // Checkpoint 3 after every 2 layers (5 & 6)
        print_progress_checkpoint(3, "Layers 5 & 6 Completed: Session Terminated & Data Decrypted", 0);

        print_zigzag_indicator(LAYER_6_PRESENTATION, LAYER_7_APPLICATION, "UPWARD");

        // Layer 7: Application
        layer7_application_recv(l7_app_data, final_message, sizeof(final_message));
        // Checkpoint 4 after Layer 7
        print_progress_checkpoint(4, "Layer 7 Completed: Application Payload Delivered to Receiver", 0);

        printf("\n" ANSI_BOLD ANSI_GREEN "****************************************************************" ANSI_RESET "\n");
        printf(ANSI_BOLD ANSI_GREEN " [DELIVERED MESSAGE]: %s" ANSI_RESET "\n", final_message);
        printf(ANSI_BOLD ANSI_GREEN "****************************************************************" ANSI_RESET "\n\n");

        // Send ACK back
        const char *ack = "OSI_ACK: 7-Layer Decapsulation Completed Successfully!";
        send(client_sock, ack, (int)strlen(ack), 0);
        CLOSE_SOCKET(client_sock);

    } while (!run_once);

    CLOSE_SOCKET(listen_sock);
    cleanup_network_environment();

    printf(ANSI_BOLD ANSI_CYAN "=== SERVER DECAPSULATION WORKFLOW COMPLETED SUCCESSFULLY ===" ANSI_RESET "\n\n");
    return 0;
}
