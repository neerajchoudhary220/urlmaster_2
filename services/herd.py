import subprocess
from fastapi import HTTPException

def extract_sites_and_paths():
    result = subprocess.run(['herd', 'links'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error running 'herd links':", result.stderr)
        return []

    output = result.stdout
    results = []

    for line in output.splitlines():
        if line.startswith('|') and 'Site' not in line and '---' not in line:
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) >= 4:
                site = parts[0]
                url = parts[2]
                path = parts[3]
                results.append((site, url,path))
    
    
    sites =[]
    # Run and display
    for site, url,path in results:
        sites.append({
            'name':site,
            'url':url,
            'path':path,
        })
    return sites

def get_herd_link(path:str):
    sites = extract_sites_and_paths()
    #Check if already link available
    exist_path = any(site['path'] == path for site in sites)
    if  exist_path:
        return next((site['url'] for site in sites if site['path'] == path), None)

def link_with_herd(path: str):
    try:
        result = subprocess.run(
            ['herd', 'link'],
            cwd=path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr.strip() or "herd link failed")
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="'herd' command not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return get_herd_link(path)  # This is now properly reached

   
