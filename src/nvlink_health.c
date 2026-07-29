#include <stdio.h>
#include <stdint.h>

typedef struct {
    uint32_t gpu_id;
    uint32_t ecc_single_bit_errors;
    uint32_t ecc_double_bit_errors;
    double nvlink_bandwidth_gbps;
} NVLinkHealthState;

int evaluate_gpu_health(NVLinkHealthState state) {
    if (state.ecc_double_bit_errors > 0) return 2; // FATAL_HARDWARE_ERROR
    if (state.ecc_single_bit_errors > 1000) return 1; // WARN_REASSIGN
    return 0; // HEALTHY
}

int main() {
    NVLinkHealthState gpu0 = {0, 12, 0, 900.0};
    int status = evaluate_gpu_health(gpu0);
    printf("NVIDIA GPU #%d NVLink Health Code: %d (0=HEALTHY)\n", gpu0.gpu_id, status);
    return 0;
}
