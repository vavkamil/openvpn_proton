#!/usr/bin/env python3

import os
import json
import time
import requests
import subprocess
from random import randrange


def check_if_root():
    # Check for root priviledges
    if os.getuid() != 0:
        print("[x] Please, run this as root!\n")
        quit()


def get_ip():
    res = requests.get("https://ifconfig.me", {"User-Agent": "curl/7.68.0"})

    return res.text


def parse_protonvpn_api():
    api_url = "https://api.protonmail.ch/vpn/logicals"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }

    res = requests.get(api_url, headers=headers)

    return res.json()


def get_servers(json_obj):
    logical_servers = json_obj["LogicalServers"]
    logical_servers.sort(key=lambda x: x["Name"])

    servers_dict = {}

    for vpn_server in logical_servers:
        if vpn_server["Tier"] != 1:
            continue

        country = vpn_server["EntryCountry"]
        name = vpn_server["Name"]
        load = vpn_server["Load"]

        if country not in servers_dict:
            servers_dict[country] = {}
        servers_dict[country][name] = load

    return servers_dict


def sort_by_load(servers_dict):
    server_load_dict = {}

    for country in servers_dict:
        sum_load = 0
        for server_name, server_load in servers_dict[country].items():
            sum_load = sum_load + server_load
        server_load_dict[country] = round(sum_load / len(servers_dict[country]))

    sorted_by_load = sorted(server_load_dict.items(), key=lambda item: item[1])

    return sorted_by_load


def main():
    check_if_root()

    print("[ OpenVPN / ProtonVPN ]\n")

    print("[i] Selecting fastest VPN server ...\n")

    json_obj = parse_protonvpn_api()

    servers_dict = get_servers(json_obj)

    sorted_by_load = sort_by_load(servers_dict)

    random_top_ten_country_code = sorted_by_load[:10][randrange(10)][0].lower()

    openvpn_config = f"{random_top_ten_country_code}.protonvpn.com.udp.ovpn"

    print(f"[i] Current IP: {get_ip()}\n")

    print(f"[i] Using: {openvpn_config}\n")
    subprocess.Popen(
        f"sudo openvpn --config ProtonVPN_server_configs/{openvpn_config} --auth-user-pass auth.txt",
        shell=True,
        stdout=subprocess.PIPE,
    )

    time.sleep(4)
    print(f"[i] Current IP: {get_ip()}\n")

    input("[!] Press any key to exit ...\n")
    subprocess.Popen(f"sudo killall openvpn", shell=True, stdout=subprocess.PIPE)

    time.sleep(3)
    print(f"[i] Current IP: {get_ip()}\n")


if __name__ == "__main__":
    main()
