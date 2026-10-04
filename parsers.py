# -*- coding: utf-8 -*-
import urllib.parse

def parse_nodes(uris):
    nodes = []
    tags_seen = set()

    for uri in uris:
        try:
            parsed = urllib.parse.urlparse(uri)
            scheme = parsed.scheme.lower()
            qs = urllib.parse.parse_qs(parsed.query)

            raw_tag = urllib.parse.unquote(parsed.fragment) if parsed.fragment else "Node"
            tag = raw_tag
            idx = 1
            while tag in tags_seen:
                tag = f"{raw_tag}_{idx}"
                idx += 1
            tags_seen.add(tag)

            if scheme == 'vless':
                node = {
                    "type": "vless",
                    "tag": tag,
                    "server": parsed.hostname,
                    "server_port": int(parsed.port) if parsed.port else 443,
                    "uuid": parsed.username,
                    "packet_encoding": "xudp"
                }
                if qs.get('security', [''])[0] in ['tls', 'reality']:
                    node["tls"] = {
                        "enabled": True,
                        "server_name": qs.get('sni', [''])[0]
                    }
                    if 'fp' in qs:
                        node["tls"]["utls"] = {
                            "enabled": True,
                            "fingerprint": qs.get('fp', ['chrome'])[0]
                        }
                if qs.get('security', [''])[0] == 'reality':
                    node["tls"]["reality"] = {
                        "enabled": True,
                        "public_key": qs.get('pbk', [''])[0],
                        "short_id": qs.get('sid', [''])[0]
                    }
                    if 'flow' in qs:
                        node["flow"] = qs.get('flow', [''])[0]
                if qs.get('type', [''])[0] == 'grpc':
                    node["transport"] = {
                        "type": "grpc",
                        "service_name": qs.get('serviceName', [''])[0]
                    }
                nodes.append(node)

            elif scheme in ['hysteria2', 'hy2']:
                node = {
                    "type": "hysteria2",
                    "tag": tag,
                    "server": parsed.hostname,
                    "server_port": int(parsed.port) if parsed.port else 443,
                    "password": parsed.username,
                    "tls": {
                        "enabled": True,
                        "server_name": qs.get('sni', [''])[0],
                        "insecure": qs.get('insecure', ['0'])[0] == '1',
                        "alpn": qs.get('alpn')[0].split(',') if 'alpn' in qs else ["h3"]
                    }
                }
                nodes.append(node)

        except Exception:
            continue

    return nodes
