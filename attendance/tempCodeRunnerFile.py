def is_same_subnet(client_ip: str, server_ip: str) -> bool:
    client_octets = client_ip.split('.')[:3]
    server_octets = server_ip.split('.')[:3]
    return client_octets == server_octets
