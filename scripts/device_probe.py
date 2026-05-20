import argparse
import asyncio
import ipaddress
import json
import socket
import time
from pathlib import Path

import aiohttp

try:
    from bleak import BleakScanner
except Exception:
    BleakScanner = None

try:
    from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
except Exception:
    ServiceBrowser = None
    ServiceListener = object
    Zeroconf = None


COMMON_PORTS = [
    21, 22, 23, 53, 80, 81, 88, 123, 139, 443, 445, 554, 8000, 8008,
    8009, 8080, 8081, 8443, 8888, 9000, 9999, 1883, 5353,
]

COMMON_HTTP_PATHS = [
    "/",
    "/status",
    "/info",
    "/api",
    "/api/status",
    "/api/info",
    "/device",
    "/device/info",
    "/version",
    "/description.xml",
    "/setup.xml",
]


class MdnsListener(ServiceListener):
    def __init__(self):
        self.events = []

    def add_service(self, zc, service_type, name):
        info = zc.get_service_info(service_type, name)
        self.events.append(serialize_service_info(service_type, name, info))

    def update_service(self, zc, service_type, name):
        info = zc.get_service_info(service_type, name)
        self.events.append(serialize_service_info(service_type, name, info))

    def remove_service(self, zc, service_type, name):
        self.events.append({"type": service_type, "name": name, "removed": True})


def serialize_service_info(service_type, name, info):
    if not info:
        return {"type": service_type, "name": name, "info": None}
    addresses = []
    for addr in info.addresses:
        try:
            addresses.append(socket.inet_ntoa(addr))
        except OSError:
            pass
    props = {}
    for key, value in info.properties.items():
        key_text = key.decode(errors="ignore") if isinstance(key, bytes) else str(key)
        value_text = value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
        props[key_text] = value_text
    return {
        "type": service_type,
        "name": name,
        "server": info.server,
        "port": info.port,
        "addresses": addresses,
        "properties": props,
    }


async def scan_ble(name_hint, timeout):
    if BleakScanner is None:
        return {"error": "bleak not installed or bluetooth backend unavailable", "devices": []}
    devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
    matches = []
    for address, payload in devices.items():
        device, adv = payload
        name = device.name or adv.local_name or ""
        uuids = list(adv.service_uuids or [])
        if not name_hint or name_hint.lower() in name.lower():
            matches.append(
                {
                    "address": address,
                    "name": name,
                    "rssi": adv.rssi,
                    "uuids": uuids,
                    "manufacturer_data": {str(k): v.hex() for k, v in (adv.manufacturer_data or {}).items()},
                }
            )
    return {"devices": matches}


async def probe_port(ip, port, timeout=1.5):
    result = {"port": port, "open": False}
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
        result["open"] = True
        if port in (21, 22, 23, 80, 554, 8000, 8080, 8888):
            try:
                if port in (80, 8000, 8080, 8888):
                    writer.write(b"GET / HTTP/1.0\r\nHost: probe\r\n\r\n")
                    await writer.drain()
                banner = await asyncio.wait_for(reader.read(256), timeout=1.0)
                if banner:
                    result["banner"] = banner.decode(errors="ignore").strip()
            except Exception:
                pass
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    return result


async def probe_http(session, ip, port, path):
    scheme = "https" if port in (443, 8443) else "http"
    url = f"{scheme}://{ip}:{port}{path}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=3), ssl=False) as resp:
            text = await resp.text(errors="ignore")
            return {
                "url": url,
                "status": resp.status,
                "server": resp.headers.get("Server"),
                "content_type": resp.headers.get("Content-Type"),
                "snippet": text[:200],
            }
    except Exception as exc:
        return {"url": url, "error": str(exc)}


async def probe_host(ip):
    port_results = await asyncio.gather(*(probe_port(ip, port) for port in COMMON_PORTS))
    open_ports = [item["port"] for item in port_results if item["open"]]
    http_results = []
    if open_ports:
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for port in open_ports:
                if port in (80, 81, 88, 443, 8000, 8008, 8009, 8080, 8081, 8443, 8888, 9000, 9999):
                    for path in COMMON_HTTP_PATHS:
                        tasks.append(probe_http(session, ip, port, path))
            if tasks:
                http_results = await asyncio.gather(*tasks)
    return {
        "ip": ip,
        "ports": port_results,
        "http": http_results,
    }


def ssdp_discover(timeout=3):
    message = "\r\n".join(
        [
            "M-SEARCH * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            'MAN: "ssdp:discover"',
            "MX: 2",
            "ST: ssdp:all",
            "",
            "",
        ]
    ).encode()
    responses = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.settimeout(timeout)
    sock.sendto(message, ("239.255.255.250", 1900))
    start = time.time()
    while time.time() - start < timeout:
        try:
            data, addr = sock.recvfrom(4096)
            responses.append({"from": addr[0], "port": addr[1], "data": data.decode(errors="ignore")[:1000]})
        except socket.timeout:
            break
        except Exception:
            break
    sock.close()
    return responses


def mdns_discover(timeout=5):
    if Zeroconf is None or ServiceBrowser is None:
        return {"error": "zeroconf not installed", "services": []}
    service_types = [
        "_http._tcp.local.",
        "_googlecast._tcp.local.",
        "_airplay._tcp.local.",
        "_hap._tcp.local.",
        "_workstation._tcp.local.",
    ]
    zc = Zeroconf()
    listener = MdnsListener()
    browsers = [ServiceBrowser(zc, service_type, listener) for service_type in service_types]
    time.sleep(timeout)
    zc.close()
    return {"services": listener.events}


def expand_hosts(subnet):
    net = ipaddress.ip_network(subnet, strict=False)
    return [str(ip) for ip in net.hosts()]


async def run(args):
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ble": None,
        "mdns": None,
        "ssdp": None,
        "hosts": [],
    }

    if args.scan_ble:
        results["ble"] = await scan_ble(args.ble_name, args.timeout)

    if args.scan_lan:
        results["mdns"] = mdns_discover()
        results["ssdp"] = ssdp_discover()
        hosts = expand_hosts(args.subnet)
        limited_hosts = hosts[: args.max_hosts]
        tasks = [probe_host(ip) for ip in limited_hosts]
        results["hosts"] = await asyncio.gather(*tasks)

    if args.ip:
        results["hosts"].append(await probe_host(args.ip))

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifacts_dir / "probe_result.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nSaved to: {output_path.resolve()}")


def build_parser():
    parser = argparse.ArgumentParser(description="Probe a legacy smart speaker over BLE and LAN.")
    parser.add_argument("--scan-ble", action="store_true", help="Scan nearby BLE advertisements.")
    parser.add_argument("--ble-name", default="", help="Filter BLE devices by name hint.")
    parser.add_argument("--timeout", type=int, default=12, help="BLE scan timeout in seconds.")
    parser.add_argument("--scan-lan", action="store_true", help="Scan local subnet and discover mDNS/SSDP.")
    parser.add_argument("--subnet", default="192.168.1.0/24", help="Subnet for LAN scan.")
    parser.add_argument("--max-hosts", type=int, default=32, help="Limit hosts scanned from subnet.")
    parser.add_argument("--ip", help="Probe a known device IP.")
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(run(args))
