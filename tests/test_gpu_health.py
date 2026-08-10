import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gpu_health import GpuSample, health_index, THROTTLE_C

def test_optimal_cool():
    h = health_index(GpuSample(temp_c=40, power_w=400, sm_util=0.5, mem_util=0.4))
    assert h["status"] in ("OPTIMAL", "NOMINAL")
    assert h["health_index"] > 0.3
def test_throttle_risk():
    h = health_index(GpuSample(temp_c=THROTTLE_C + 1, power_w=750, sm_util=0.95, mem_util=0.9))
    assert h["status"] in ("THROTTLE_RISK", "CRITICAL")

if __name__ == "__main__":
    test_optimal_cool()
    test_throttle_risk()
    print("ok")
