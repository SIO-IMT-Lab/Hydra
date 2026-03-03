# ADS Utilities

Tools for reading voltages from ADS1015 analog-to-digital converters.

## ads.py

Print scaled voltages from one or more ADS1015 devices:

```bash
python ads.py --addresses 0x48 0x49 0x4A 0x4B --ratio 11.06 --interval 2
```

Options:

- `--addresses` – I2C addresses of ADS1015 chips (default `0x48 0x49 0x4A 0x4B`).
- `--ratio` – scaling factor applied to the raw voltage (default `24/2.17`).
- `--interval` – delay between readings in seconds (default `1`).

## ads_gui.py

Display the voltages in a Tkinter window:

```bash
python ads_gui.py --addresses 0x48 --interval 0.5
```

The same command line options as `ads.py` are available.
