import subprocess
import platform
import re

def get_wifi_passwords_windows():
    output = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [line.split(":")[1].strip() for line in output if "All User Profile" in line]

    wifi_list = []
    for profile in profiles:
        try:
            result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8').split('\n')
            password = [line.split(":")[1].strip() for line in result if "Key Content" in line]
            wifi_list.append((profile, password[0] if password else ""))
        except:
            wifi_list.append((profile, "Error"))
    return wifi_list

def get_wifi_passwords_linux():
    import os
    wifi_list = []
    path = "/etc/NetworkManager/system-connections/"
    try:
        files = subprocess.check_output(['ls', path]).decode().split('\n')
        for file in files:
            if file.strip() == '':
                continue
            try:
                content = subprocess.check_output(['sudo', 'cat', f"{path}{file}"]).decode()
                ssid = re.search(r'ssid=(.*)', content)
                psk = re.search(r'psk=(.*)', content)
                wifi_list.append((ssid.group(1) if ssid else file, psk.group(1) if psk else ""))
            except:
                wifi_list.append((file, "Permission Denied"))
    except:
        wifi_list.append(("Error", "Could not read network files"))
    return wifi_list

def get_wifi_passwords_macos():
    wifi_list = []
    try:
        # Get known SSIDs
        output = subprocess.check_output(['/usr/bin/security', 'find-generic-password', '-D', 'AirPort network password', '-a', '', '-g'], stderr=subprocess.STDOUT).decode()
        ssids = re.findall(r'"acct"<blob>="(.*?)"', output)

        for ssid in ssids:
            try:
                password = subprocess.check_output(['security', 'find-generic-password', '-D', 'AirPort network password', '-a', ssid, '-g'], stderr=subprocess.STDOUT).decode()
                match = re.search(r'password: "(.*)"', password)
                wifi_list.append((ssid, match.group(1) if match else ""))
            except:
                wifi_list.append((ssid, "Permission Denied"))
    except:
        wifi_list.append(("Error", "Could not fetch saved networks"))
    return wifi_list

def main():
    os_name = platform.system()
    print("\n{:<30}| {:<}".format("Wi-Fi Name", "Password"))
    print("-" * 50)

    if os_name == "Windows":
        wifi_list = get_wifi_passwords_windows()
    elif os_name == "Linux":
        wifi_list = get_wifi_passwords_linux()
    elif os_name == "Darwin":
        wifi_list = get_wifi_passwords_macos()
    else:
        print("Unsupported OS")
        return

    for wifi, password in wifi_list:
        print("{:<30}| {:<}".format(wifi, password))

if __name__ == "__main__":
    main()
