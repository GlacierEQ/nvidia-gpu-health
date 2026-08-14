#include <math.h>
#include <stdint.h>
#include <stdio.h>

#define EVIDENCE_STATE "LOCAL_SYNTHETIC_GPU_HEALTH_MODEL_NOT_NVIDIA_TELEMETRY_AUTHORITY"

typedef enum {
    GPU_HEALTH_NOMINAL = 0,
    GPU_HEALTH_WARNING = 1,
    GPU_HEALTH_CRITICAL = 2,
    GPU_HEALTH_INVALID = 3
} GpuHealthCode;

typedef struct {
    uint32_t gpu_id;
    uint32_t ecc_single_bit_errors;
    uint32_t ecc_double_bit_errors;
    double nvlink_bandwidth_gbps;
} GpuHealthSample;

typedef struct {
    uint32_t ecc_single_bit_warning;
    double min_nvlink_bandwidth_gbps;
} GpuHealthPolicy;

GpuHealthCode evaluate_gpu_health(GpuHealthSample sample, GpuHealthPolicy policy) {
    if (!isfinite(sample.nvlink_bandwidth_gbps) || sample.nvlink_bandwidth_gbps < 0.0 ||
        !isfinite(policy.min_nvlink_bandwidth_gbps) || policy.min_nvlink_bandwidth_gbps < 0.0) {
        return GPU_HEALTH_INVALID;
    }
    if (sample.ecc_double_bit_errors > 0U) {
        return GPU_HEALTH_CRITICAL;
    }
    if (sample.ecc_single_bit_errors >= policy.ecc_single_bit_warning ||
        sample.nvlink_bandwidth_gbps < policy.min_nvlink_bandwidth_gbps) {
        return GPU_HEALTH_WARNING;
    }
    return GPU_HEALTH_NOMINAL;
}

int main(void) {
    const GpuHealthPolicy policy = {1000U, 700.0};
    const GpuHealthSample nominal = {0U, 12U, 0U, 900.0};
    const GpuHealthSample warning = {1U, 1000U, 0U, 850.0};
    const GpuHealthSample critical = {2U, 0U, 1U, 900.0};
    const GpuHealthSample invalid = {3U, 0U, 0U, NAN};

    if (evaluate_gpu_health(nominal, policy) != GPU_HEALTH_NOMINAL ||
        evaluate_gpu_health(warning, policy) != GPU_HEALTH_WARNING ||
        evaluate_gpu_health(critical, policy) != GPU_HEALTH_CRITICAL ||
        evaluate_gpu_health(invalid, policy) != GPU_HEALTH_INVALID) {
        return 1;
    }

    printf("%s\n", EVIDENCE_STATE);
    printf("operational_authority=false\n");
    return 0;
}
