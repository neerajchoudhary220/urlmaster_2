import subprocess
import random
import re
import sys,requests,urllib3



def get_public_url(herd_link:str):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    herd_clean = re.sub(r'^https?://', '', herd_link).strip('/').replace('.test','')
    local_port = 80
    remote_port = random.randint(3000, 9999)
    ssh_user = "tunneluser"
    ssh_host = "neerajchoudhary.fun"
    ssh_key = "~/.ssh/id_tunnel"
    public_subdomain = f"{herd_clean}-{remote_port}"  # use dash
    public_url = f"https://{public_subdomain}.{ssh_host}"
    # === TUNNEL COMMAND ===
    ssh_command = [
        "ssh",
        "-i", ssh_key,
        "-N",
        "-R", f"{remote_port}:127.0.0.1:{local_port}",
        f"{ssh_user}@{ssh_host}"
    ]
    process = subprocess.Popen(ssh_command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    res = requests.get(public_url,verify=False)
    print(process.pid)
    print(public_url)
    if res.status_code==200:
        tunnel_info = {"public_url": public_url, "pid": process.pid, "herd_link": urherd_linkl}
        save_tunnel(tunnel_info)
        print(process.pid)
        
        return public_url
    else:
        return HTTPException(400,' Tunnel issue')
   
   
get_public_url("http://user_disable_and_delete.test")