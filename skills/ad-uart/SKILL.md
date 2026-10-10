---
name: ad-uart
description: Send and receive UART (serial) data with an Analog Discovery's DIO pins from Python, including baud rate, parity, and stop bits. Use to talk to or monitor a device's serial console without a USB-serial adapter.
---

# UART

Prereq: `ad-connect` template. 3.3 V logic only. Wiring to tell the user (`ad-user-handoff`): Analog Discovery `DIO0` (TX) to the target's RX, `DIO1` (RX) to the target's TX, `GND` to target ground. Passive listening: leave TX unconnected and set only RX.

```python
# body: runs inside the ad-connect template
dwf.FDwfDigitalUartReset(hdwf)
dwf.FDwfDigitalUartRateSet(hdwf, c_double(115200))   # baud
dwf.FDwfDigitalUartBitsSet(hdwf, 8)
dwf.FDwfDigitalUartParitySet(hdwf, 0)                # 0 none, 1 even, 2 odd, 3 mark, 4 space
dwf.FDwfDigitalUartStopSet(hdwf, c_double(1))        # stop bits
dwf.FDwfDigitalUartTxSet(hdwf, 0)                    # DIO0
dwf.FDwfDigitalUartRxSet(hdwf, 1)                    # DIO1
count, parity = c_int(), c_int()
dwf.FDwfDigitalUartTx(hdwf, None, 0)                 # initialize TX at its idle level
dwf.FDwfDigitalUartRx(hdwf, None, 0, byref(count), byref(parity))   # initialize RX
time.sleep(0.2)

dwf.FDwfDigitalUartTx(hdwf, create_string_buffer(b"help\r\n"), 6)   # send the bytes: length excludes the trailing zero

received = bytearray()
buf = create_string_buffer(8192)
end = time.time() + 2                                # listen for 2 s
while time.time() < end:
    time.sleep(0.01)
    if dwf.FDwfDigitalUartRx(hdwf, buf, 8192, byref(count), byref(parity)) != 1:
        raise SystemExit(last_error())
    received += buf.raw[:count.value]
    if parity.value:
        print("parity/framing error code", parity.value)
print(received.decode("ascii", errors="replace"))
```

- Wait before and between `Rx` polls: the receiver buffer holds only a few KB. Poll at least every 10 ms at high baud rates.
- The `Tx` call returns after queuing; transmission time is `bytes * 10 / baud` seconds.
- Receive-only monitoring in a loop: sample `Digital_Uart_RX.py`. Invert polarity (RS-232 style) with `FDwfDigitalUartPolaritySet(hdwf, 1)`.
- Voltage levels beyond 3.3 V (RS-232, RS-485): not supported directly. Tell the user a level shifter or transceiver is required.
- Debugging a non-working link: capture with `ad-logic-analyzer` and decode with `ad-decode-capture`.

## Docs

- [SDK Reference Manual: Digital UART](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- Samples: `Digital_Uart.py`, `Digital_Uart_RX.py`
