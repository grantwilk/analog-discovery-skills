---
name: ad-i2c
description: Act as an I2C master with an Analog Discovery's DIO pins from Python to scan for addresses and read or write device registers. Use to find and talk to I2C sensors, EEPROMs, and ICs.
---

# I2C master

Prereq: `ad-connect` template. 3.3 V logic only. Wiring to tell the user (`ad-user-handoff`): `DIO0` SCL, `DIO1` SDA, `GND` to target ground; **pull-up resistors (about 2.2 kOhm to 10 kOhm to 3.3 V) on SCL and SDA are required** and must exist on the target board or be added. Passive snooping: `ad-protocol-spy`.

**Addresses:** the SDK takes the 8-bit form (7-bit address shifted left by one). A 7-bit address `0x1D` is passed as `0x1D << 1`.

## Scan the bus

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalI2cReset(hdwf)
dwf.FDwfDigitalI2cRateSet(hdwf, c_double(100e3))
dwf.FDwfDigitalI2cSclSet(hdwf, 0)
dwf.FDwfDigitalI2cSdaSet(hdwf, 1)
nak = c_int()
dwf.FDwfDigitalI2cClear(hdwf, byref(nak))
if nak.value == 0:
    raise SystemExit("bus held low: check pull-ups, power, and wiring")
found = []
for addr in range(1, 0x78):
    dwf.FDwfDigitalI2cWrite(hdwf, addr << 1, None, 0, byref(nak))   # address only
    if nak.value == 0:
        found.append(hex(addr))
print("devices at 7-bit addresses:", found)
```

## Register read and write

```python
# body: runs inside the ad-connect template, after the bus setup above
addr, reg = 0x1D, 0x0D                                   # example: accelerometer WHO_AM_I
nak = c_int()
rx = (c_ubyte * 1)()
dwf.FDwfDigitalI2cWriteRead(hdwf, addr << 1, (c_ubyte * 1)(reg), 1, rx, 1, byref(nak))   # write reg, restart, read 1
if nak.value != 0:
    raise SystemExit(f"NAK {nak.value}")
print(f"reg 0x{reg:02X} = 0x{rx[0]:02X}")

dwf.FDwfDigitalI2cWrite(hdwf, addr << 1, (c_ubyte * 2)(0x2A, 0x01), 2, byref(nak))   # write 0x01 to register 0x2A
```

- `nak` is `0` on success (ACK); a positive value is the index of the byte that was NAKed (`1` = address); a negative value is a bus error.
- `FDwfDigitalI2cRead(hdwf, addr << 1, buf, n, byref(nak))` reads without writing a register first.
- No ACK from a known device: wrong address, no power, no pull-ups, or SCL/SDA swapped.
- Clock stretching is supported; set `FDwfDigitalI2cStretchSet(hdwf, 1)` when the target needs it.
- Bus state in the SDK is sticky; call `FDwfDigitalI2cClear` again after a fault.

## Docs

- [SDK Reference Manual: Digital I2C](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `Digital_I2c.py`, `Digital_I2c_Spy.py`
