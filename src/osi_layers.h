#ifndef OSI_LAYERS_H
#define OSI_LAYERS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #ifdef _MSC_VER
        #pragma comment(lib, "ws2_32.lib")
    #endif
    typedef int socklen_t;
    #define CLOSE_SOCKET(s) closesocket(s)
#else
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #define CLOSE_SOCKET(s) close(s)
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
#endif

#define DEFAULT_PORT 8080
#define BUFFER_SIZE 4096
#define BITSTREAM_SIZE 32768

/* ANSI Color Escape Codes */
#define ANSI_RESET   "\x1b[0m"
#define ANSI_BOLD    "\x1b[1m"
#define ANSI_RED     "\x1b[31m"
#define ANSI_GREEN   "\x1b[32m"
#define ANSI_YELLOW  "\x1b[33m"
#define ANSI_BLUE    "\x1b[34m"
#define ANSI_MAGENTA "\x1b[35m"
#define ANSI_CYAN    "\x1b[36m"
#define ANSI_WHITE   "\x1b[37m"
#define ANSI_BG_BLUE "\x1b[44m"
#define ANSI_BG_GREEN "\x1b[42m"

/* OSI Layer Enumeration */
typedef enum {
    LAYER_7_APPLICATION = 7,
    LAYER_6_PRESENTATION = 6,
    LAYER_5_SESSION = 5,
    LAYER_4_TRANSPORT = 4,
    LAYER_3_NETWORK = 3,
    LAYER_2_DATALINK = 2,
    LAYER_1_PHYSICAL = 1
} OSILayer;

/* Layer Packet Data Structure */
typedef struct {
    char raw_payload[BUFFER_SIZE];
    size_t payload_len;
    char bitstream[BITSTREAM_SIZE];
    size_t bit_count;
} OSIPacket;

/* Function Declarations: Encapsulation (Transmit / Client Side: 7 -> 1) */
void layer7_application_send(const char *app_message, char *output, size_t max_len);
void layer6_presentation_send(const char *input, char *output, size_t max_len);
void layer5_session_send(const char *input, char *output, size_t max_len);
void layer4_transport_send(const char *input, char *output, size_t max_len, uint16_t src_port, uint16_t dst_port);
void layer3_network_send(const char *input, char *output, size_t max_len, const char *src_ip, const char *dst_ip);
void layer2_datalink_send(const char *input, char *output, size_t max_len, const char *src_mac, const char *dst_mac);
void layer1_physical_send(const char *frame, char *bitstream_out, size_t max_bits);

/* Function Declarations: Decapsulation (Receive / Server Side: 1 -> 7) */
void layer1_physical_recv(const char *bitstream_in, char *frame_out, size_t max_len);
void layer2_datalink_recv(const char *frame_in, char *packet_out, size_t max_len);
void layer3_network_recv(const char *packet_in, char *segment_out, size_t max_len);
void layer4_transport_recv(const char *segment_in, char *session_data_out, size_t max_len);
void layer5_session_recv(const char *session_data_in, char *pres_data_out, size_t max_len);
void layer6_presentation_recv(const char *pres_data_in, char *app_data_out, size_t max_len);
void layer7_application_recv(const char *app_data_in, char *final_message_out, size_t max_len);

/* Helper Functions */
void log_layer_step(OSILayer layer, const char *action, const char *details);
void print_progress_checkpoint(int stage, const char *description, int is_encapsulation);
void print_zigzag_indicator(OSILayer from_layer, OSILayer to_layer, const char *arrow_dir);
void text_to_binary(const char *text, char *binary_out, size_t max_bits);
void binary_to_text(const char *binary_in, char *text_out, size_t max_len);
uint16_t calculate_checksum(const char *data);
void initialize_network_environment(void);
void cleanup_network_environment(void);

#endif /* OSI_LAYERS_H */
