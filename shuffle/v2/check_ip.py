import ipaddress
ip = "$exec.all_fields.data.src_ip".strip()
MY_INTERNAL_RANGES = [ipaddress.ip_network("150.1.7.0/24")]
try:
    a = ipaddress.ip_address(ip)
    internal = (not a.is_global) or any(a in n for n in MY_INTERNAL_RANGES)
    print("private" if internal else "public")
except ValueError:
    print("private")
