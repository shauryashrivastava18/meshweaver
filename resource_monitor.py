import psutil

def get_resource_info():
    """Collect current CPU and RAM usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()

    resource_info = {
        "cpu_percent": cpu_usage,
        "ram_percent": ram.percent,
        "ram_used_mb": round(ram.used / (1024 * 1024), 2),
        "ram_total_mb": round(ram.total / (1024 * 1024), 2)
    }

    return resource_info


if __name__ == "__main__":
    info = get_resource_info()
    print("Resource Monitoring")
    print("-----------------")
    print(f"CPU Usage: {info['cpu_percent']}%")
    print(f"RAM Usage: {info['ram_percent']}%")
    print(f"RAM Used: {info['ram_used_mb']} MB")
    print(f"RAM Total: {info['ram_total_mb']} MB")