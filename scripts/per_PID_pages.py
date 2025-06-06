import sys

def parse_smaps(pid):
    rss_kb = 0
    anon_kb = 0
    try:
        with open(f"/proc/{pid}/smaps", "r") as f:
            for line in f:
                if line.startswith("Rss:"):
                    rss_kb += int(line.split()[1])
                elif line.startswith("Anonymous:"):
                    anon_kb += int(line.split()[1])
        file_kb = rss_kb - anon_kb
        return anon_kb // 4, file_kb // 4  # convert to 4KB pages
    except Exception as e:
        print(f"Error reading /proc/{pid}/smaps: {e}")
        return None

def get_process_name(pid):
    try:
        with open(f"/proc/{pid}/comm", "r") as f:
            return f.read().strip()
    except:
        return "unknown"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: sudo python3 per_pid_pages.py <PID>")
        sys.exit(1)

    pid = sys.argv[1]
    result = parse_smaps(pid)
    if result:
        anon_pages, file_pages = result
        name = get_process_name(pid)
        print(f"Process: {name} (PID {pid})")
        print(f"  Anonymous pages : {anon_pages} pages (4KB each)")
        print(f"  File-backed pages: {file_pages} pages (4KB each)")
