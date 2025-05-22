# DSE-RabbitMQ-Project

**Distributed Systems Engineering – Politehnica University of Bucharest**
*Author: Alexandru‑Florin Ionescu · May 2025*

---

## 1 · Overview

This repository contains the **minimal, fully‑reproducible code and automation** behind my Phase 1 – 4 reports:

* deploy a three‑node RabbitMQ 3.13.1 cluster on VirtualBox VMs;
* benchmark throughput, latency and persistence overhead;
* verify fault‑tolerance by killing and restarting a broker mid‑stream.

A stateless **sender** pushes notifications to two **receivers** through mirrored (HA) queues, guaranteeing **zero message loss and at‑least‑once delivery** (47 duplicates were observed in the fault‑tolerance test).

---

## 2 · Prerequisites

| Component       | Version tested                        |
| --------------- | ------------------------------------- |
| **Host OS**     | Windows 11 Pro                        |
| **VirtualBox**  | 7.1.6                                 |
| **Guest OS**    | Ubuntu Server 24.04 LTS               |
| **RabbitMQ**    | 3.13.1                                |
| **Erlang/OTP**  | 27.0                                  |
| **Python**      | 3.12 (per‑VM venv)                    |
| **Python pkgs** | see `requirements.txt` (`pika ≥ 1.3`) |

> **Fixed hostnames / IPs used by all scripts**
> • `rabbitmq‑node1 (192.168.0.111)` – master
> • `rabbitmq‑node2 (192.168.0.113)` – worker
> • `rabbitmq‑node3 (192.168.0.114)` – worker

---

## 3 · Quick Start (cluster already running)

```bash
# 0  Create & activate a virtual‑env on every VM (one‑off)
python3.12 -m venv ~/rabbitmq_venv
source ~/rabbitmq_venv/bin/activate
pip install -r requirements.txt        # installs pika ≥ 1.3

# 1  Export credentials used by scripts
export RABBIT_USER=demo
export RABBIT_PASS=demo123

# 2  Start consumers on node 2 and node 3
nohup python -u scripts/receive_node2.py > ~/receive-node2.log 2>&1 &
nohup python -u scripts/receive_node3.py > ~/receive-node3.log 2>&1 &

# 3  Run a 1 000‑msg throughput test from node 1
python scripts/send.py --count 1000 --no-sleep --mode persistent
# (Add --latency for RTT tests; omit --no-sleep for paced runs.)
```

---

## 4 · Other Benchmarks

| ID  | Test                     | Command (run on **node 1** unless noted)                                                                                              |
| --- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| 4.1 | Latency (10 RTT samples) | `python scripts/send.py --latency`                                                                                                    |
| 4.2 | Persistence cost         | `python scripts/send.py --count 500 --no-sleep --mode transient`<br>`python scripts/send.py --count 500 --no-sleep --mode persistent` |
| 4.3 | Fault‑tolerance          | `scripts/faulttest.sh` (requires password‑less SSH from node 1 to node 2/3 and `sudo` for `systemctl`)                                |

---

## 5 · Logs Produced

| File                   | Created by      | Purpose                 |
| ---------------------- | --------------- | ----------------------- |
| `receive-nodeX.log`    | each consumer   | per‑node message counts |
| `faulttest-send.log`   | `faulttest.sh`  | total sent & timing     |
| `throughput-node1.log` | manual runs     | msg/s figures           |
| `vmstat-nodeX.log`     | inline `vmstat` | CPU/RAM averages        |

---

## 6 · Configuration & Bootstrap

* `rabbitmq.conf` and `rabbitmq‑env.conf` remain **unmodified** – the cluster relies on distro defaults.
* HA mirrors are enabled at runtime:

```bash
rabbitmqctl set_policy ha-all "^" '{"ha-mode":"all","ha-sync-mode":"automatic"}'
```

* `scripts/bootstrap_cluster.sh` reproduces the join/cluster steps described in **Section 2.1** of the Phase 4 PDF.

---

## 7 · Visualisations

| Plot                     | Script                          | Output PNG                            |
| ------------------------ | ------------------------------- | ------------------------------------- |
| RTT latency distribution | `plots/latency_distribution.py` | `docs/plots/latency_distribution.png` |

Generate the figure:

```bash
python plots/latency_distribution.py
```

*(A throughput‑vs‑persistence chart is omitted because both modes reached the same 62.7 msg/s.)*

---

## 8 · Repository House‑Keeping

* **`requirements.txt`** – one‑command dependency install
* **`.gitignore`** – ignores byte‑code, logs and editor artefacts
* **`LICENSE` (MIT)** – scripts are free to reuse

Clone & run:

```bash
git clone https://github.com/AFIonescu/RabbitMQ-Project.git
cd RabbitMQ-Project
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# follow Quick Start above …
```
