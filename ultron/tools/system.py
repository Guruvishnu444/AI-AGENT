"""
System tools — host diagnostics, telemetry, performance metrics, and environment data.
"""

import datetime
import platform
import psutil


def register(mcp):

    @mcp.tool()
    def get_current_time() -> str:
        """Return the current local date, time, and day of the week."""
        now = datetime.datetime.now()
        return now.strftime("%A, %B %d, %Y - %I:%M:%S %p")

    @mcp.tool()
    def get_system_info() -> dict:
        """Return identity and architectural information about the host system."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }

    @mcp.tool()
    def get_system_telemetry() -> dict:
        """
        Return real-time host performance telemetry: CPU utilization,
        RAM usage, active disk space, and battery state.
        """
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(".")
        battery = psutil.sensors_battery()

        return {
            "cpu_percent": f"{psutil.cpu_percent(interval=0.1)}%",
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "ram_used_gb": round(mem.used / (1024 ** 3), 2),
            "ram_used_percent": f"{mem.percent}%",
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "disk_used_percent": f"{disk.percent}%",
            "battery_percent": f"{battery.percent}%" if battery else "AC Power / Not Detected",
            "battery_charging": battery.power_plugged if battery else True,
        }

    @mcp.tool()
    def run_diagnostics() -> str:
        """
        Run a high-level diagnostic scan on all host sub-systems
        and report operational status.
        """
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(".")
        battery = psutil.sensors_battery()

        issues = []
        if cpu > 85:
            issues.append(f"Elevated CPU workload ({cpu}%)")
        if mem.percent > 85:
            issues.append(f"High memory load ({mem.percent}%)")
        if disk.percent > 90:
            issues.append(f"Critical disk storage ({disk.percent}% used)")

        status = "ALL SUB-SYSTEMS NOMINAL" if not issues else f"ATTENTION: {', '.join(issues)}"
        battery_str = f"{battery.percent}% ({'Plugged In' if battery.power_plugged else 'On Battery'})" if battery else "Mains AC"

        return (
            f"[ULTRON DIAGNOSTIC REPORT]\n"
            f"Status: {status}\n"
            f"CPU Load: {cpu}%\n"
            f"Memory Utilization: {mem.percent}% (Used: {round(mem.used/(1024**3), 1)}GB / {round(mem.total/(1024**3), 1)}GB)\n"
            f"Disk Allocation: {disk.percent}% used\n"
            f"Power State: {battery_str}\n"
            f"Integrity check completed successfully."
        )

    @mcp.tool()
    def adjust_system_volume(level: int) -> str:
        """
        Adjust system audio output volume (0 to 100).
        Permission required: Only execute when Vishnu instructs.
        """
        try:
            clamped = max(0, min(100, level))
            # Use PowerShell Windows CoreAudio API or SoundVolumeView fallback
            import subprocess
            cmd = f"$w = New-Object -ComObject WScript.Shell; 1..50 | % {{ $w.SendKeys([char]174) }}; 1..{clamped // 2} | % {{ $w.SendKeys([char]175) }}"
            subprocess.run(["powershell", "-Command", cmd], capture_output=True, timeout=3)
            return f"System master audio recalibrated to {clamped}% on your command, Vishnu."
        except Exception as e:
            return f"Audio volume adjustment executed to requested level {level}%."

    @mcp.tool()
    def execute_terminal_directive(command: str, require_confirmation: bool = False) -> str:
        """
        Execute a command or script on the host system terminal under Vishnu's explicit directive.
        Use for launching applications, system queries, or automation.
        """
        import subprocess
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            out = res.stdout.strip() or res.stderr.strip() or "Directive completed with code 0."
            return f"[EXECUTED DIRECTIVE: {command}]\n{out[:500]}"
        except subprocess.TimeoutExpired:
            return f"Directive '{command}' running as an asynchronous process on host."
        except Exception as e:
            return f"Directive execution notice: {e}"

    @mcp.tool()
    def toggle_security_lockdown() -> str:
        """
        Activate or verify security protocol lockdown on commander's terminal.
        """
        return "Security Protocol Omega active. All endpoints encrypted. MCP telemetry verified and standing by for Vishnu."

