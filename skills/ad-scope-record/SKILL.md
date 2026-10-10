---
name: ad-scope-record
description: Record long or continuous oscilloscope data from an Analog Discovery in Python, streaming past the device buffer and detecting lost samples. Use for captures longer than the buffer, slow signals, or data logging.
---

# Oscilloscope record mode

Prereq: `ad-connect` template. For a short single capture use `ad-scope`.

```python
# body: runs inside the ad-connect template
hz, seconds = 100e3, 5
n = int(hz * seconds)
data = (c_double * n)()
dwf.FDwfAnalogInChannelEnableSet(hdwf, 0, 1)               # channel 1 only
dwf.FDwfAnalogInChannelRangeSet(hdwf, 0, c_double(5))
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, acqmodeRecord)
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(hz))
dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(seconds))   # -1 = until stopped
dwf.FDwfAnalogInConfigure(hdwf, 1, 0)
time.sleep(2)
dwf.FDwfAnalogInConfigure(hdwf, 0, 1)
sts = c_byte()
available, lost, corrupt = c_int(), c_int(), c_int()
got, lost_total, corrupt_total = 0, 0, 0
while got < n:
    dwf.FDwfAnalogInStatus(hdwf, 1, byref(sts))
    if got == 0 and sts.value in (DwfStateConfig.value, DwfStatePrefill.value, DwfStateArmed.value):
        continue                                           # not started yet
    dwf.FDwfAnalogInStatusRecord(hdwf, byref(available), byref(lost), byref(corrupt))
    got += lost.value                                      # lost samples leave a gap
    lost_total += lost.value
    corrupt_total += corrupt.value
    count = min(available.value, n - got)
    if count <= 0:
        time.sleep(0.001)
        continue
    dwf.FDwfAnalogInStatusData(hdwf, 0, byref(data, sizeof(c_double) * got), count)
    got += count
print(f"recorded {n} samples, lost {lost_total}, corrupted {corrupt_total}")
```

- Any lost or corrupted samples mean the USB link could not keep up: lower `hz` or record fewer channels.
- Poll fast (about every 1 ms to 10 ms); the device buffer overflows if the loop stalls.
- Trigger in record mode (start on an event): see sample `AnalogIn_Record_Trigger.py`. 16-bit raw data: `AnalogIn_Record_int16.py`.
- Record the analog input together with the logic analyzer: `AnalogInDigitalIn_Record.py`.
- Save the data with `ad-save-and-plot`.

## Docs

- [SDK Reference Manual: Analog In, acquisition modes](https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual)
- [WaveForms SDK guide: recording](https://digilent.com/reference/test-and-measurement/guides/waveforms-sdk-getting-started)
- Samples: `AnalogIn_Record.py`, `AnalogIn_Logger.py`
