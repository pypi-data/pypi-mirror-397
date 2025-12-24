from bec_server.scan_server.scans import Scan


class DeviceProgressScan(Scan):
    """A scan that simulates device progress updates."""

    scan_name = "device_progress_grid_scan"

    def scan_report_instructions(self):
        yield from self.stubs.scan_report_instruction({"device_progress": ["waveform"]})
