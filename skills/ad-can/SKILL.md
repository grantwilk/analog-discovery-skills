---
name: ad-can
description: Send and receive CAN bus frames with an Analog Discovery's DIO pins from Python. Use to test CAN nodes; requires an external CAN transceiver.
---

# CAN

Prereq: `ad-connect` template. The Analog Discovery's DIO pins are **logic-level only (3.3 V)**: they connect to a CAN transceiver's `TXD`/`RXD`, not to the CAN bus itself. Tell the user (`ad-user-handoff`): a 3.3 V CAN transceiver board is required; `DIO0` to transceiver `TXD`, `DIO1` to transceiver `RXD`, `GND` common; the bus needs 120 Ohm termination at both ends.

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalCanReset(hdwf)
dwf.FDwfDigitalCanRateSet(hdwf, c_double(500e3))    # bit rate
dwf.FDwfDigitalCanPolaritySet(hdwf, 0)              # 0 normal, 1 inverted
dwf.FDwfDigitalCanTxSet(hdwf, 0)                    # DIO0
dwf.FDwfDigitalCanRxSet(hdwf, 1)                    # DIO1
dwf.FDwfDigitalCanTx(hdwf, -1, 0, 0, 0, None)       # initialize TX (id -1 = drive idle only)
dwf.FDwfDigitalCanRx(hdwf, None, None, None, None, None, 0, None)   # initialize RX
time.sleep(0.5)

payload = (c_ubyte * 4)(0, 1, 2, 3)
dwf.FDwfDigitalCanTx(hdwf, 0x3FD, 0, 0, 4, payload) # id, extended (0/1), remote (0/1), data length, data

ident, extended, remote, dlc, status = c_int(), c_int(), c_int(), c_int(), c_int()
data = (c_ubyte * 8)()
end = time.time() + 5
while time.time() < end:
    time.sleep(0.01)
    dwf.FDwfDigitalCanRx(hdwf, byref(ident), byref(extended), byref(remote), byref(dlc),
                         data, 8, byref(status))
    if status.value != 0:                           # 1 ok, 2 bit-stuffing error, 3 CRC error, other error
        print(f"id=0x{ident.value:X} ext={extended.value} rtr={remote.value} status={status.value} "
              f"data={bytes(data[:dlc.value]).hex(' ')}")
```

- Without another node on the bus, nothing ACKs the frame and the transmitter retries. A loopback test needs two nodes.
- Some samples open the device with `FDwfDeviceConfigOpen(-1, 3, ...)` (a configuration with a larger digital buffer); see `ad-device-config`.
- If received frames always show errors, check bit rate and polarity first.
- CAN FD is not supported by this API.
- Passive monitoring of an existing bus: `ad-protocol-spy`.

## Docs

- [SDK Reference Manual: Digital CAN](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `Digital_Can.py` (replace `time.clock()` with `time.time()`; `clock` was removed in Python 3.8)
