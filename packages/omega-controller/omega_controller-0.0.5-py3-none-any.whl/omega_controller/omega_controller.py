import minimalmodbus
from typing import Optional, Union, List, Sequence

# Error maps per Omega manuals. Keys are raw 16-bit register values (hex shown in docs).
# Communication Error Messages table indicates:
# - Error Status register at 0x102E (or 0x4750 on some models)
# - PV register readback at 0x1000 (or 0x4700 on some models) may return 0x8002, 0x8003, 0x8004, 0x8006, etc.
PV_ERROR_CODES = {
    0x8002: "Re-initialize, no temperature at this time",
    0x8003: "Input sensor did not connect",
    0x8004: "Input signal error",
    0x8006: "ADC fail",
}

STATUS_ERROR_CODES = {
    0x0001: "PV unstable",
    0x0002: "Re-initialize, no temperature at this time",
    0x0003: "Input sensor did not connect",
    0x0004: "Input signal error",
    0x0005: "Over input range",
    0x0006: "ADC fail",
    0x0007: "EEPROM read/write error",
}

# ------------------------------ error handling ------------------------------
class OmegaControllerError(Exception):
    """Represents an error reported by the Omega controller.

    Attributes:
        source: Where the error came from ("pv" or "status").
        register: Modbus register address that contained the error code.
        code: 16-bit error code value as returned by the device.
        description: Human-readable description of the error.
    """

    def __init__(self, source: str, register: int, code: int, description: str) -> None:
        self.source = source
        self.register = register
        self.code = code
        self.description = description
        super().__init__(
            f"Omega error from {source} 0x{register:04X}: 0x{code:04X} - {description}"
        )

class OmegaController:
    """
    Omega temperature controller driver using Modbus over serial via minimalmodbus.

    - Communication per `omega_logger.py` template (ASCII, 7E1, 9600 baud by default)
    - Exposes low-level register/bit helpers and high-level convenience methods.

    Address map (hex):
      - 0x1000: Process value (PV), unit 0.1 °C
      - 0x1001: Set value (SV), unit 0.1 °C
      - 0x0814: RUN/STOP bit (0 = STOP, 1 = RUN)
    """

    # Holding/Input registers
    ADDR_PV = 0x1000
    ADDR_SV = 0x1001
    # Some models use alternate addresses for PV and error status
    ADDR_PV_ALT = 0x4700
    # Control / PID parameters
    ADDR_CONTROL_METHOD = 0x1005  # 0=PID, 1=ON/OFF, 2=Manual Tuning, 3=PID Program
    ADDR_P = 0x1009              # Proportional Band (0.1 units)
    ADDR_I = 0x100A              # Integral time (seconds)
    ADDR_D = 0x100B              # Derivative time (seconds)

    # Program (Ramp/Soak) parameter blocks
    ADDR_PROG_BLOCK_A_BASE = 0x2000  # 0x2000-0x203F
    ADDR_PROG_BLOCK_B_BASE = 0x2080  # 0x2080-0x20BF
    PROGRAM_BLOCK_SIZE = 0x40        # 64 registers per block

    # Manual mode parameters
    ADDR_MANUAL_OUTPUT_1 = 0x1012
    ADDR_MANUAL_OUTPUT_2 = 0x1013

    # Coil/bit registers
    ADDR_RUNSTOP = 0x0814

    # Error/status registers (primary/alternate models)
    ADDR_STATUS = 0x102E
    ADDR_STATUS_ALT = 0x4750

    def __init__(
        self,
        port: str,
        slave_address: int = 1,
        baudrate: int = 9600,
        parity: Union[str, int] = minimalmodbus.serial.PARITY_EVEN,
        bytesize: int = 7,
        stopbits: int = 1,
        timeout: Union[int, float] = 5,
        mode: Union[str, int] = minimalmodbus.MODE_ASCII,
    ) -> None:
        self.instrument = minimalmodbus.Instrument(port, slave_address)

        # Serial configuration (Omega expects 7E1 for ASCII mode)
        self.instrument.serial.baudrate = baudrate
        # Normalize parity if provided as string (e.g., "even", "odd", "none")
        if isinstance(parity, str):
            p = parity.strip().lower()
            if p in ("even", "e"):
                parity_const = minimalmodbus.serial.PARITY_EVEN
            elif p in ("odd", "o"):
                parity_const = minimalmodbus.serial.PARITY_ODD
            elif p in ("none", "n"):
                parity_const = minimalmodbus.serial.PARITY_NONE
            else:
                raise ValueError(f"Unsupported parity: {parity}")
        else:
            parity_const = parity
        self.instrument.serial.parity = parity_const
        self.instrument.serial.bytesize = bytesize
        self.instrument.serial.stopbits = stopbits
        self.instrument.serial.timeout = timeout
        
        # Normalize mode if provided as string (e.g., "ascii", "acii", "rtu")
        if isinstance(mode, str):
            m = mode.strip().lower()
            if m in ("ascii", "acii"):
                mode_const = minimalmodbus.MODE_ASCII
            elif m in ("rtu",):
                mode_const = minimalmodbus.MODE_RTU
            else:
                raise ValueError(f"Unsupported mode: {mode}")
        else:
            mode_const = mode
        self.instrument.mode = mode_const

    # ----------------------------- context mgmt -----------------------------
    def close(self) -> None:
        try:
            self.instrument.serial.close()
        except Exception:
            # Best-effort close
            pass

    def __enter__(self) -> "OmegaController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------ low-level -------------------------------
    def read_register(
        self,
        address: int,
        number_of_decimals: int = 0,
        functioncode: int = 3,
        signed: bool = False,
    ) -> int:
        """Read a single register.

        Uses Modbus function 03 (holding) by default as per Omega docs.
        """
        return self.instrument.read_register(
            address,
            number_of_decimals=number_of_decimals,
            functioncode=functioncode,
            signed=signed,
        )

    def read_registers(
        self,
        address: int,
        count: int,
        functioncode: int = 3,
    ) -> List[int]:
        """Read multiple consecutive registers (Modbus function 03)."""
        return list(self.instrument.read_registers(address, count, functioncode=functioncode))

    def write_register(
        self,
        address: int,
        value: Union[int, float],
        number_of_decimals: int = 0,
        functioncode: int = 6,
        signed: bool = False,
    ) -> None:
        """Write a single register (Modbus function 06)."""
        self.instrument.write_register(
            address,
            value,
            number_of_decimals=number_of_decimals,
            functioncode=functioncode,
            signed=signed,
        )

    def write_registers(
        self,
        address: int,
        values: Sequence[int],
        functioncode: int = 16,
    ) -> None:
        """Write multiple consecutive registers (Modbus function 16)."""
        self.instrument.write_registers(address, list(values), functioncode=functioncode)

    def read_bit(self, address: int, functioncode: int = 2) -> int:
        """Read a discrete/bit register (function 02). Returns 0 or 1."""
        return int(self.instrument.read_bit(address, functioncode=functioncode))

    def write_bit(self, address: int, value: int, functioncode: int = 5) -> None:
        """Write a bit/coil (function 05). Value should be 0 or 1."""
        self.instrument.write_bit(address, int(bool(value)), functioncode=functioncode)

    # ------------------------------ high-level ------------------------------

    def get_control_method(self) -> Optional[int]:
        """Return control method (0=PID,1=ON/OFF,2=Manual Tuning,3=PID Program)."""
        try:
            return int(self.read_register(self.ADDR_CONTROL_METHOD, number_of_decimals=0))
        except IOError:
            return None

    def set_control_method(self, method: Union[int, str]) -> None:
        """Set control method. Accepts int 0-3 or strings: 'pid','onoff','manual','program'."""
        if isinstance(method, str):
            m = method.strip().lower()
            table = {"pid": 0, "onoff": 1, "manual": 2, "ramp_soak": 3, "program": 3, "pid program": 3, "pid_program": 3}
            if m not in table:
                raise ValueError("Unsupported control method string")
            value = table[m]
        else:
            value = int(method)
        if value not in (0, 1, 2, 3):
            raise ValueError("Control method must be 0,1,2, or 3")
        self.write_register(self.ADDR_CONTROL_METHOD, value, number_of_decimals=0)

    def get_pv(self, raise_on_error: bool = False) -> Optional[float]:
        """Return process value in °C.

        If the PV register contains an Omega error code (e.g., 0x8002), either
        returns None or raises OmegaControllerError if raise_on_error=True.
        """
        # Read raw (no decimal scaling) so we can detect special error codes
        try:
            pv_raw = self.read_register(self.ADDR_PV, number_of_decimals=0)
        except IOError:
            # Communication issue
            return None

        # Check for documented PV error codes
        if pv_raw in PV_ERROR_CODES:
            if raise_on_error:
                raise OmegaControllerError(
                    source="pv",
                    register=self.ADDR_PV,
                    code=pv_raw,
                    description=PV_ERROR_CODES[pv_raw],
                )
            return None

        # Otherwise interpret PV as 0.1 °C units
        return float(pv_raw) / 10.0
        
    def get_sv(self) -> Optional[float]:
        """Return current setpoint in °C."""
        try:
            return float(self.read_register(self.ADDR_SV, number_of_decimals=1))
        except IOError:
            return None

    def set_sv(self, temperature_c: Union[int, float]) -> None:
        """Set the setpoint in °C. Value is rounded to 0.1 °C resolution."""
        self.write_register(self.ADDR_SV, float(temperature_c), number_of_decimals=1)


    def get_manual_output_1(self) -> Optional[float]:
        """Return manual output 1 in °C."""
        try:
            return float(self.read_register(self.ADDR_MANUAL_OUTPUT_1, number_of_decimals=1))
        except IOError:
            return None

    def set_manual_output_1(self, output: Union[int, float]) -> None:
        """Set manual output 1 in °C."""
        self.write_register(self.ADDR_MANUAL_OUTPUT_1, float(output), number_of_decimals=1)

    def get_manual_output_2(self) -> Optional[float]:
        """Return manual output 2 in °C."""
        try:
            return float(self.read_register(self.ADDR_MANUAL_OUTPUT_2, number_of_decimals=1))
        except IOError:
            return None

    def set_manual_output_2(self, output: Union[int, float]) -> None:
        """Set manual output 2 in °C."""
        self.write_register(self.ADDR_MANUAL_OUTPUT_2, float(output), number_of_decimals=1)

    def run(self) -> None:
        """Set controller to RUN mode (0814h bit = 1)."""
        self.write_bit(self.ADDR_RUNSTOP, 1)

    def stop(self) -> None:
        """Set controller to STOP mode (0814h bit = 0)."""
        self.write_bit(self.ADDR_RUNSTOP, 0)

    def is_running(self) -> Optional[bool]:
        """Return True if RUN, False if STOP. None on communication error."""
        try:
            return bool(self.read_bit(self.ADDR_RUNSTOP))
        except IOError:
            return None

    def get_p(self) -> Optional[float]:
        """Return proportional band (0.1 resolution)."""
        try:
            return float(self.read_register(self.ADDR_P, number_of_decimals=1))
        except IOError:
            return None

    def set_p(self, p: Union[int, float]) -> None:
        """Set proportional band. Resolution 0.1 units; valid 0.1..999.9."""
        self.write_register(self.ADDR_P, float(p), number_of_decimals=1)

    def get_i(self) -> Optional[int]:
        """Return integral time in seconds (0..9999)."""
        try:
            return int(self.read_register(self.ADDR_I, number_of_decimals=0))
        except IOError:
            return None

    def set_i(self, ti_seconds: int) -> None:
        """Set integral time in seconds (0..9999)."""
        self.write_register(self.ADDR_I, int(ti_seconds), number_of_decimals=0)

    def get_d(self) -> Optional[int]:
        """Return derivative time in seconds (0..9999)."""
        try:
            return int(self.read_register(self.ADDR_D, number_of_decimals=0))
        except IOError:
            return None

    def set_d(self, td_seconds: int) -> None:
        """Set derivative time in seconds (0..9999)."""
        self.write_register(self.ADDR_D, int(td_seconds), number_of_decimals=0)

    # ---- PID program control (Ramp/Soak) parameter blocks ----
    def read_program_block(self, block: Union[int, str] = 0) -> Optional[List[int]]:
        """Read a 64-register program parameter block.

        block: 0/"A" -> 0x2000..0x203F, 1/"B" -> 0x2080..0x20BF.
        Returns list of 64 integers, or None on communication error.
        """
        base = self._resolve_program_block_base(block)
        try:
            return self.read_registers(base, self.PROGRAM_BLOCK_SIZE)
        except IOError:
            return None

    def write_program_block(self, block: Union[int, str], values: Sequence[int]) -> None:
        """Write a 64-register program parameter block.

        Length must be exactly 64. Values are written as raw register values.
        """
        if len(values) != self.PROGRAM_BLOCK_SIZE:
            raise ValueError("Program block must contain exactly 64 register values")
        base = self._resolve_program_block_base(block)
        self.write_registers(base, values)

    def read_program_param(self, block: Union[int, str], offset: int) -> Optional[int]:
        """Read a single program parameter at given offset (0..63)."""
        if not 0 <= offset < self.PROGRAM_BLOCK_SIZE:
            raise ValueError("offset must be in 0..63")
        base = self._resolve_program_block_base(block)
        try:
            return int(self.read_register(base + offset, number_of_decimals=0))
        except IOError:
            return None

    def write_program_param(self, block: Union[int, str], offset: int, value: int) -> None:
        """Write a single program parameter at given offset (0..63)."""
        if not 0 <= offset < self.PROGRAM_BLOCK_SIZE:
            raise ValueError("offset must be in 0..63")
        base = self._resolve_program_block_base(block)
        self.write_register(base + offset, int(value), number_of_decimals=0)

    # ------------------------------ helpers ---------------------------------
    def _resolve_program_block_base(self, block: Union[int, str]) -> int:
        if isinstance(block, str):
            b = block.strip().upper()
            if b in ("A", "0"):
                return self.ADDR_PROG_BLOCK_A_BASE
            if b in ("B", "1"):
                return self.ADDR_PROG_BLOCK_B_BASE
            raise ValueError("Unknown program block; use 'A' or 'B'")
        idx = int(block)
        if idx == 0:
            return self.ADDR_PROG_BLOCK_A_BASE
        if idx == 1:
            return self.ADDR_PROG_BLOCK_B_BASE
        raise ValueError("Program block index must be 0 or 1")

    # ------------------------------ error API --------------------------------
    def read_status_code(self) -> Optional[int]:
        """Read the controller status/error code.

        Tries the primary status register first (0x102E), then an alternate
        address (0x4750) used on some models. Returns None on comms error.
        A return value of 0 means "no error".
        """
        try:
            return int(self.read_register(self.ADDR_STATUS, number_of_decimals=0))
        except IOError:
            # Try alternate model address
            try:
                return int(
                    self.read_register(self.ADDR_STATUS_ALT, number_of_decimals=0)
                )
            except IOError:
                return None

    def get_status_error(self) -> Optional[OmegaControllerError]:
        """Return an OmegaControllerError if status register reports error, else None."""
        code = self.read_status_code()
        if code is None or code == 0:
            return None
        description = STATUS_ERROR_CODES.get(code, "Unknown status error")
        return OmegaControllerError(
            source="status",
            register=self.ADDR_STATUS,
            code=code,
            description=description,
        )

    def check_errors(self, raise_on_error: bool = True) -> Optional[OmegaControllerError]:
        """Check for any current controller errors.

        - Looks at the status/error register.
        - Also checks PV error codes.
        Returns an error object or None. If raise_on_error=True, raises the
        error instead of returning it.
        """
        # Status register first
        status_err = self.get_status_error()
        if status_err is not None:
            if raise_on_error:
                raise status_err
            return status_err

        # PV error codes
        try:
            pv_raw = self.read_register(self.ADDR_PV, number_of_decimals=0)
        except IOError:
            return None
        if pv_raw in PV_ERROR_CODES:
            err = OmegaControllerError(
                source="pv",
                register=self.ADDR_PV,
                code=pv_raw,
                description=PV_ERROR_CODES[pv_raw],
            )
            if raise_on_error:
                raise err
            return err

        return None