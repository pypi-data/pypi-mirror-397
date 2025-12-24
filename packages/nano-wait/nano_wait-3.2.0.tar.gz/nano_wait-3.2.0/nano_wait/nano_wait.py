from .core import NanoWait
from .utils import log_message, get_speed_value
import time

def wait(
    t: float,
    wifi: str | None = None,
    speed: str | float = "normal",
    smart: bool = False,
    verbose: bool = False,
    log: bool = False
) -> float:
    """
    Adaptive smart wait — replaces time.sleep() with intelligence.

    Args:
        t (float): Base wait time in seconds.
        wifi (str, optional): Wi-Fi SSID to evaluate.
        speed (str|float): 'slow', 'normal', 'fast', 'ultra', or custom float.
        smart (bool): Enable Smart Context Mode.
        verbose (bool): Print debug info.
        log (bool): Write log to file.

    Returns:
        float: Wait time executed (seconds).
    """
    nw = NanoWait()

    if smart:
        speed_value = nw.smart_speed(wifi)
        mode = "smart"
    else:
        speed_value = get_speed_value(speed)
        mode = "manual"

    factor = (
        nw.compute_wait_wifi(speed_value, wifi)
        if wifi else
        nw.compute_wait_no_wifi(speed_value)
    )

    wait_time = round(max(0.05, min(t / factor, t)), 3)

    if verbose:
        print(
            f"[NanoWait] 🧠 mode={mode} | speed={speed_value:.2f} | "
            f"factor={factor:.2f} | wait={wait_time:.3f}s"
        )

    if log:
        log_message(
            f"mode={mode} speed={speed_value:.2f} factor={factor:.2f} wait={wait_time:.3f}s"
        )

    time.sleep(wait_time)
    return wait_time
