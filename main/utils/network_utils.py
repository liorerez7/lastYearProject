import subprocess

def get_windows_host_ip():
    """
    Get the Windows host IP address from WSL.
    """
    result = subprocess.run(
        ["wsl", "ip", "route"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"❌ Failed to get Windows IP: {result.stderr}")

    for line in result.stdout.splitlines():
        if line.startswith("default via"):
            return line.split()[2]
    raise Exception("❌ Could not find default route IP.")
