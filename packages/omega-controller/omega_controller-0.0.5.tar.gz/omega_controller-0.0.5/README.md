## Omega Controller (Python)

Lightweight Python driver for Omega CN-series temperature controllers using Modbus over serial (via `minimalmodbus`).

### Features
- **PV/SV**: get present value and set temperature setpoint
- **On/Off**: get and set the controller on/off
- **Modes**: PID, ON/OFF, MANUAL, and **PID Program (Ramp/Soak)**
- **PID tuning**: get/set P, I, D
- **Program params**: read/write 64-register blocks for Ramp/Soak (A/B)
- **Error handling**: maps Omega error/status codes and raises helpful exceptions

Install dependencies:
```bash
pip install minimalmodbus
```

Install this driver from via pypi:
```bash
pip install omega-controller
```

### Quickstart
```python
from omega_controller import OmegaController, OmegaControllerError

# Adjust port/slave as needed for your setup
ctrl = OmegaController(port="COM3", slave_address=1, baudrate=9600, parity="even", bytesize=7, stopbits=1, mode="ascii")

try:
    # Optional: raise if the controller is reporting an error
    ctrl.check_errors()

    # Read process value (°C)
    pv = ctrl.get_pv()
    print("PV:", pv)

    # Set temperature setpoint (°C)
    ctrl.set_sv(150.0)

    # Switch to PID Program (Ramp/Soak) mode
    ctrl.set_control_method("program")

    # Tune PID
    ctrl.set_p(12.3)
    ctrl.set_i(600)
    ctrl.set_d(120)

except OmegaControllerError as e:
    print("Controller error:", e)
finally:
    ctrl.close()
```

### API Overview
- **PV/SV**
  - `get_pv(raise_on_error=False) -> Optional[float]`
  - `get_sv() -> Optional[float]`
  - `set_sv(temp_c: float) -> None`
- **Control method**
  - `get_control_method() -> Optional[int]`  (0=PID, 1=ON/OFF, 2=MANUAL, 3=PROGRAM)
  - `set_control_method(method: int|str) -> None`
- **PID**
  - `get_p()/set_p()` – proportional band (0.1 resolution)
  - `get_i()/set_i()` – integral time (seconds)
  - `get_d()/set_d()` – derivative time (seconds)
- **Ramp/Soak program parameters**
  - Blocks: **A** = `0x2000–0x203F`, **B** = `0x2080–0x20BF` (64 regs each)
  - `read_program_block(block)` / `write_program_block(block, values)`
  - `read_program_param(block, offset)` / `write_program_param(block, offset, value)`
- **Errors**
  - `check_errors(raise_on_error=True)` – checks status and PV error codes
  - Raises `OmegaControllerError` with descriptive message

### Serial Settings
- Some models use alternate status/PV addresses; this driver handles common variants

### Compatibility
- Tested on: **Omega CN7800**
- Expected to work with many CN-series models using the same Modbus map

### Roadmap - Contributions Welcome
- [ ] Test on additional Omega models
- [ ] Add remaining serial commands from the manual (alarms, limits, etc.)