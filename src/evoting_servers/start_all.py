from multiprocessing import Process
import os

def run_server(path):
    os.system(f"python3 {path}")  # ← aqui está corrigido

if __name__ == "__main__":
    servers = [
        "src/evoting_servers/adm_server.py",
        "src/evoting_servers/reg_server.py",
        "src/evoting_servers/tal_server.py",
        "src/evoting_servers/val_server.py",
    ]

    processes = []

    for server in servers:
        p = Process(target=run_server, args=(server,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
