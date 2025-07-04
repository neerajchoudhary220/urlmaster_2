from services import cloudflared
import json

remote_port=''

def get_remote_port(herd_link:str):
    with open("active_tunnels.json","r") as f:
        tunnels = json.load(f)
    
    for tunnel in tunnels:
        if tunnel['herd_link'] == herd_link:
            return tunnel['remote_port']
    return None

remote_port = get_remote_port("http://sembark3.test")
if get_remote_port("http://sembark3.test"):
    
    print(remote_port)
else:
    print("not found")

    