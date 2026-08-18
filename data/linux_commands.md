# Linux Core Administration Reference

## Disk Management
- `df -h`: Displays available disk space on file systems in human-readable format (GB, MB).
- `du -sh <directory>`: Summarizes total disk usage of a specific directory.
- `lsblk -f`: Lists block devices with file system types and mount points.

## Process & System Monitoring
- `top` / `htop`: Real-time process viewer and system resource monitor.
- `systemctl status <service>`: Check operational state of a systemd unit.
- `systemctl restart <service>`: Restart a service immediately.
- `journalctl -u <service> -f`: Follow live system logs for a specific service.

## File Permissions & Ownership
- `chmod 755 <file>`: Sets read, write, execute for owner (7), and read/execute for group/others (5).
- `chmod +x <file>`: Adds executable permission to file for all users.
- `chown <user>:<group> <file>`: Changes owner and group of a file.

## Critical Safety Warning
- Never run `rm -rf /` or `dd if=/dev/zero of=/dev/sdX` without verifying disk device names, as these cause unrecoverable data loss.