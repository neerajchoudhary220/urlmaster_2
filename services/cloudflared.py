import re,requests,os,signal,time,json,subprocess,urllib3,random,logging
from fastapi import HTTPException
from pathlib import Path
time
from datetime import datetime

TUNNELS_FILE =Path("active_tunnels.json")
# Disable insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Configure logging
logging.basicConfig(
    filename='tunnel_err.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_public_url(herd_link: str):
    try:
        herd_clean = re.sub(r'^https?://', '', herd_link).strip('/').replace('.test','')
        local_port = 80
        remote_port = random.randint(3000, 65000)
        ssh_user = "tunneluser"
        ssh_host = "neerajchoudhary.fun"
        ssh_key = "~/.ssh/id_tunnel"
        #Regenerate Public URL
        if get_remote_port(herd_link):
            remote_port =get_remote_port(herd_link)
            
        public_subdomain = f"{herd_clean}-{remote_port}"
        public_url = f"https://{public_subdomain}.{ssh_host}"
        
            
        # SSH Tunnel
        ssh_command = [
            "ssh",
            "-i", ssh_key,
            "-N",
            "-R", f"{remote_port}:127.0.0.1:{local_port}",
            f"{ssh_user}@{ssh_host}"
        ]
        process = subprocess.Popen(
            ssh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Retry loop to wait for tunnel readiness
        for attempt in range(10):
            try:
                res = requests.get(public_url, verify=False, timeout=2)
                if res.status_code == 200:
                    print(process.pid)
                    print(public_url)
                    tunnel_info = {"public_url": public_url, "pid": process.pid, "herd_link": herd_link,"remote_port":remote_port}
                    # if get_remote_port(herd_link):
                    save_tunnel(tunnel_info)
                    return public_url
            except requests.RequestException:
                pass
            time.sleep(1.5)

        logging.error(f"Tunnel setup failed after retries for {public_url}")
        return None

    except Exception as e:
        logging.exception(f"Error setting up tunnel for {herd_link}")
        return None

# def get_cloudflared_public_url(url: str):


#     domain = re.sub(r'^https?://', '', url).strip('/')
#     print(f"domain is {domain}")
#     CLOUDFLARED_PATH = shutil.which("cloudflared") or"/opt/homebrew/bin/cloudflared"
#     process = subprocess.Popen(
#         [CLOUDFLARED_PATH, "tunnel", "--url", "http://127.0.0.1:80", "--http-host-header", domain],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True
#     )

#     public_url = None
#     for line in process.stdout:
#         match = re.search(r'(https://[a-zA-Z0-9-]+\.trycloudflare\.com)', line)
#         if match:
#             public_url = match.group(1)
#             break

#     if not public_url:
#         process.terminate()
#         raise HTTPException(400,detail="❌ Tunnel URL not found.")
#     time.sleep(3)
#     res = requests.get(public_url,verify=False)
#     print(process.pid)
#     print(public_url)
#     if res.status_code==200:
#         tunnel_info = {"public_url": public_url, "pid": process.pid, "herd_link": urherd_linkl}
#         save_tunnel(tunnel_info)
#         print(process.pid)
        
#         return public_url
#     else:
#         return HTTPException(400,' Tunnel issue')
  

def save_tunnel(tunnel_info: dict) -> str:
    """
    Saves or updates a tunnel entry in the JSON file based on herd_link.

    Args:
        tunnel_info (dict): Dictionary with keys: public_url, pid, herd_link.

    Returns:
        str: The saved or updated public_url.
    """
    if os.path.exists(TUNNELS_FILE):
        with open(TUNNELS_FILE, "r") as f:
            try:
                tunnels = json.load(f)
            except json.JSONDecodeError:
                tunnels = []
    else:
        tunnels = []

    updated = False
    for idx, tunnel in enumerate(tunnels):
        if tunnel.get("herd_link") == tunnel_info["herd_link"]:
            kill_tunnel_by_url(tunnel.get('herd_link'))#Kill Old Cloudflared tunnel link before update new
            tunnels[idx] = tunnel_info
            updated = True
            break

    if not updated:
        tunnels.append(tunnel_info)

    with open(TUNNELS_FILE, "w") as f:
        json.dump(tunnels, f, indent=2)


def kill_tunnel_by_url(herd_link: str):
    
    if not os.path.exists(TUNNELS_FILE):
        print("No active tunnels found.")
        return

    with open(TUNNELS_FILE, "r") as f:
        try:
            tunnels = json.load(f)
        except json.JSONDecodeError:
            print("Tunnel file is corrupted or empty.")
            return

    updated_tunnels = []
    killed = False

    for tunnel in tunnels:
        if tunnel["herd_link"] == herd_link:
            try:
                os.kill(tunnel["pid"], signal.SIGTERM)
                killed = True
            except ProcessLookupError:
               raise HTTPException(400,detail=f"⚠️ Process already dead for: {tunnel['herd_link']}")
        else:
            updated_tunnels.append(tunnel)

    # Always write updated list back
    with open(TUNNELS_FILE, "w") as f:
        json.dump(updated_tunnels, f, indent=2)

    if not killed:
        raise HTTPException(400,detail="Not tunnel active right now")
    return True

def get_remote_port(herd_link:str):
    with open("active_tunnels.json","r") as f:
        tunnels = json.load(f)
    
    for tunnel in tunnels:
        if tunnel['herd_link'] == herd_link:
            return tunnel['remote_port']
    return None

def get_tunnel(herd_link: str, file_path: str = 'active_tunnels.json') -> str | None:
        if not os.path.exists(TUNNELS_FILE):
            return None
        with open(file_path, 'r') as f:
            tunnels = json.load(f)

        for tunnel in tunnels:
            if tunnel.get('herd_link') == herd_link:
                return tunnel.get('public_url')

        return None

def replace_env_values(dir_path:str, new_domain:str):
    env_path = f"{dir_path}/.env"
    with open(env_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    domain = new_domain.replace("http://", "").replace("https://", "")
    
    for line in lines:
        #APP_URL
        if line.startswith("APP_URL="):
            updated_lines.append(f'APP_URL="{new_domain}"\n')
            
        # APP_PUBLIC_URL
        elif line.startswith("APP_PUBLIC_URL="):
            updated_lines.append(f'APP_PUBLIC_URL="{new_domain}"\n')

        # SESSION_DOMAIN
        elif line.startswith("SESSION_DOMAIN="):
            updated_lines.append(f'SESSION_DOMAIN={domain}\n')

        # SANCTUM_STATEFUL_DOMAINS
        elif line.startswith("SANCTUM_STATEFUL_DOMAINS="):
            parts = line.strip().split("=")[1].split(",")
            new_parts = [p for p in parts if "trycloudflare.com" not in p]
            if domain not in new_parts:
                new_parts.append(domain)
            updated_lines.append(f"SANCTUM_STATEFUL_DOMAINS={','.join(new_parts)}\n")

        else:
            updated_lines.append(line)

    with open(env_path, "w") as f:
        f.writelines(updated_lines)

def kill_all_tunnels():
    if not os.path.exists(TUNNELS_FILE):
        print("No active tunnels found.")
        return

    with open(TUNNELS_FILE, "r") as f:
        try:
            tunnels = json.load(f)
        except json.JSONDecodeError:
            print("Tunnel file is corrupted or empty.")
            return

    if not tunnels:
        print("No tunnels to kill.")
        return

    for tunnel in tunnels:
        try:
            os.kill(tunnel["pid"], signal.SIGTERM)
            print(f"Killed tunnel: {tunnel['herd_link']} (PID: {tunnel['pid']})")
        except ProcessLookupError:
            print(f"⚠️ Process already dead for: {tunnel['herd_link']}")
        except Exception as e:
            print(f"Error killing process {tunnel['pid']}: {e}")

    # Clear the tunnels file
    with open(TUNNELS_FILE, "w") as f:
        json.dump([], f)

    print("✅ All tunnels terminated.")