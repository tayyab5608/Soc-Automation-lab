# 🛡️ SOC Automation Lab
## Wazuh + Shuffle SOAR + VirusTotal + Discord

![SOC Lab](https://img.shields.io/badge/SOC-Automation%20Lab-blue?style=for-the-badge)
![Wazuh](https://img.shields.io/badge/Wazuh-SIEM-orange?style=for-the-badge)
![Shuffle](https://img.shields.io/badge/Shuffle-SOAR-purple?style=for-the-badge)
![VirusTotal](https://img.shields.io/badge/VirusTotal-Threat%20Intel-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Required-blue?style=for-the-badge)

---

## 📖 Table of Contents

1. [What Is This Lab?](#-what-is-this-lab)
2. [Why This Lab Matters](#-why-this-lab-matters)
3. [Lab Architecture](#-lab-architecture)
4. [Infrastructure Requirements](#-infrastructure-requirements)
5. [Prerequisites](#-prerequisites)
6. [PART 1 — Install Shuffle SOAR on Linux](#-part-1--install-shuffle-soar-on-linux)
7. [PART 2 — Deploy Webhook in Shuffle](#-part-2--deploy-webhook-in-shuffle)
8. [PART 3 — Configure Wazuh Integration](#-part-3--configure-wazuh-integration)
9. [PART 4 — Configure VirusTotal Enrichment](#-part-4--configure-virustotal-enrichment)
10. [PART 5 — Add Subnet Filter Conditions](#-part-5--add-subnet-filter-conditions)
11. [PART 6 — Configure Discord SOC Alerts](#-part-6--configure-discord-soc-alerts)
12. [PART 7 — Configure Wazuh Active Response](#-part-7--configure-wazuh-active-response)
13. [PART 8 — Red Team Attack Simulation](#-part-8--red-team-attack-simulation)
14. [PART 9 — Verify the Full Pipeline](#-part-9--verify-the-full-pipeline)
15. [Contributing](#-contributing)
16. [License](#-license)

---

## 🔍 What Is This Lab?

This is a **fully automated, self-hosted SOC (Security Operations Center) lab** built entirely with open-source tools. It simulates a real-world enterprise security environment where every component works together automatically — from attack detection all the way to IP blocking and team notification.

Here is what happens when an attacker runs an Nmap scan in this lab:

```
Attacker runs Nmap  →  Suricata detects it  →  Wazuh correlates it
→  Shuffle receives the alert via Webhook
→  VirusTotal scores the attacker IP
→  Discord sends a rich SOC alert to your team
→  Wazuh automatically blocks the attacker IP via firewall-drop
→  IP is automatically unblocked after 10 minutes
```

**Everything above happens automatically. Zero manual steps.**

---

## 🎯 Why This Lab Matters

| Skill You Learn | Why It Is Important |
|----------------|---------------------|
| SIEM Integration | Every SOC analyst works with SIEM tools daily |
| SOAR Automation | Reduces alert fatigue and cuts manual response time |
| Threat Intelligence | IP enrichment is a core analyst workflow |
| Active Response | Automated containment is a critical blue team skill |
| Network Detection | IDS/IPS configuration is fundamental to defense |
| Incident Response | End-to-end IR pipeline mirrors a real enterprise SOC |

> This lab is perfect for **SOC Analysts, Blue Team Engineers, Cybersecurity Students**, and anyone preparing for **CompTIA CySA+, CEH, SC-200**, or building a portfolio for job applications.

---

## 🏗️ Lab Architecture

```
+--------------------------------------------------+
|           Isolated Subnet (YOUR_SUBNET/24)       |
+--------------------------------------------------+
         |              |                |
+--------v------+ +-----v--------+ +----v-----------+
| Kali Linux    | | Target Host  | | Suricata       |
| (Attacker)    | | Windows +    | | Network IDS    |
| YOUR_KALI_IP  | | Sysmon       | | YOUR_SURI_IP   |
+---------------+ | YOUR_WIN_IP  | +-------+--------+
         |        +--------------+         |
         |    Attack + Sysmon Telemetry    EVE JSON
         +-------------------+-------------+
                             |
                    +--------v-------+
                    |  Wazuh SIEM    |
                    | YOUR_WAZUH_IP  |
                    +--------+-------+
                             |
               +-------------+-------------+
               |                           |
       Active Response              Webhook Forward
       firewall-drop                       |
       [Blocks Attacker]          +--------v--------+
                                  |  Shuffle SOAR   |
                                  | YOUR_SHUFFLE_IP |
                                  +--------+--------+
                                           |
                               +-----------+-----------+
                               |                       |
                      +--------v------+     +----------v-----+
                      | VirusTotal    |     | Discord        |
                      | IP Enrichment |     | SOC Alerts     |
                      +---------------+     +----------------+
```

---

## 💻 Infrastructure Requirements

| Machine | Role | OS | Minimum RAM | Minimum Storage |
|---------|------|----|-------------|-----------------|
| Shuffle Server | SOAR Platform | RHEL / Rocky / CentOS | 8 GB | 40 GB |
| Wazuh Manager | SIEM Engine | Ubuntu 22.04 LTS | 4 GB | 50 GB |
| Target Host | Monitored Endpoint | Windows 10/11 | 4 GB | 40 GB |
| Suricata IDS | Network Detection | Ubuntu 22.04 LTS | 2 GB | 20 GB |
| Kali Linux | Attack Simulation | Kali 2024+ | 2 GB | 20 GB |

> 💡 All machines must be on the same isolated network subnet for the lab to work correctly.

---

## 📋 Prerequisites

Before starting, make sure you have the following ready:

- [ ] A fresh Linux server for Shuffle (RHEL, Rocky Linux, or CentOS 8/9 recommended)
- [ ] Wazuh Manager already installed — [Official Wazuh Installation Guide](https://documentation.wazuh.com/current/installation-guide/index.html)
- [ ] VirusTotal account with a free API key — [Register here](https://www.virustotal.com/gui/join-us)
- [ ] Discord server with a dedicated SOC alerts channel
- [ ] A Discord Webhook URL for that channel
- [ ] All VMs placed on the same isolated network

---

---

# 🔵 PART 1 — Install Shuffle SOAR on Linux

---

## Step 1.1 — System Requirements Check

Before installing, your Shuffle server must meet these requirements:

### ✅ RAM Requirement

Shuffle + OpenSearch requires at least **5 GB of free RAM** available at the time of startup. OpenSearch alone uses 2–4 GB.

Check your available RAM:
```bash
free -h
```

Example of a healthy output:
```
              total   used   free
Mem:           15Gi   4.2Gi  10Gi
Swap:           0B      0B    0B
```

If free RAM is below 5 GB, **do not continue** — add more RAM to your VM first.

---

### ✅ Disable Swap Memory

OpenSearch requires swap to be disabled. If swap is active, OpenSearch will perform poorly or crash.

Check if swap is on:
```bash
swapon --show
```

If you see any output (swap is active), disable it:
```bash
sudo swapoff -a
```

Make it permanent across reboots by commenting out the swap line in fstab:
```bash
sudo nano /etc/fstab
```

Find any line containing the word `swap` and add a `#` at the start to comment it out:
```
# /swapfile none swap sw 0 0
```

Save and exit. Verify swap is now off:
```bash
free -h
```

The swap row should show all zeros.

---

### ✅ Set Virtual Memory Limit for OpenSearch

OpenSearch requires a higher virtual memory map count than Linux allows by default. This is the **most important setting** — skipping it causes OpenSearch to crash in a restart loop.

```bash
# Apply immediately (takes effect right now)
sudo sysctl -w vm.max_map_count=262144

# Make it survive reboots
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

---

## Step 1.2 — Install Docker

Shuffle runs entirely inside Docker containers, so we install Docker first.

### Add Docker Repository

```bash
sudo dnf install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

### Install Docker Engine

```bash
sudo dnf install -y docker-ce docker-ce-cli containerd.io
```

### Install Docker Compose Plugin

```bash
sudo dnf install -y docker-compose-plugin
```

### Start and Enable Docker

```bash
sudo systemctl enable --now docker
```

### Verify Docker Is Running

```bash
sudo systemctl status docker
sudo docker --version
sudo docker compose version
```

Expected output:
```
Active: active (running)
Docker version 24.x.x
Docker Compose version v2.x.x
```

---

## Step 1.3 — Prepare the Database Folder

OpenSearch stores all Shuffle data in a folder called `shuffle-database`. We must create it and set the correct ownership before starting the containers.

```bash
mkdir shuffle-database
sudo chown -R 1000:1000 shuffle-database
```

> ⚠️ If you skip the `chown` command, OpenSearch will fail to write data and will keep restarting.

---

## Step 1.4 — Clone and Deploy Shuffle

```bash
git clone https://github.com/Shuffle/Shuffle.git
cd Shuffle
sudo docker compose up -d
```

> **Note:** Use `https://github.com/Shuffle/Shuffle.git` — this is the current official repository. The older URL `github.com/frikky/Shuffle` still exists but may not always be up to date.

Docker will now pull all required images and start the containers. This may take 3–5 minutes on first run depending on your internet speed.

---

## Step 1.5 — Verify All Containers Are Running

```bash
sudo docker compose ps
```

You should see all containers with the status **Up**:

```
NAME                 STATUS
shuffle-backend      Up
shuffle-frontend     Up
shuffle-opensearch   Up
shuffle-orborus      Up
```

> If `shuffle-opensearch` shows **Restarting**, wait 2 minutes and check again. OpenSearch takes longer to initialize. If it keeps restarting, verify your `vm.max_map_count` setting and available RAM.

---

## Step 1.6 — Access the Shuffle Web Interface

Open your browser and go to:

```
http://YOUR_SHUFFLE_SERVER_IP:3001
```

On your first visit, Shuffle will ask you to create an admin account. Create a username and strong password — you will use these to log in every time.

---

---

# 🔵 PART 2 — Deploy Webhook in Shuffle

---

## Step 2.1 — Create a New Workflow

1. Log into Shuffle at `http://YOUR_SHUFFLE_IP:3001`
2. Click **"Workflows"** in the left sidebar
3. Click **"New Workflow"**
4. Name it: `SOC Incident Response`
5. Click **Create**

---

## Step 2.2 — Add the Webhook Trigger Node

1. In the workflow canvas, click **"Triggers"** in the left panel
2. Drag a **Webhook** node onto the canvas
3. Click the Webhook node to open its configuration panel
4. Click **"Start"** to activate the listener

---

## Step 2.3 — Copy the Webhook URL

After clicking Start, copy the generated Webhook URL. It will look like:

```
http://YOUR_SHUFFLE_IP:3001/api/v1/hooks/webhook_XXXXXXXXXXXXXXXXXXXXXXXX
```

> 💾 Save this URL — you will paste it into the Wazuh configuration in the next section.

---

## Step 2.4 — Save the Workflow

Click the **Save** button (floppy disk icon) at the top of the canvas.

---

---

# 🔵 PART 3 — Configure Wazuh Integration

---

## Step 3.1 — SSH Into Your Wazuh Manager

```bash
ssh your_user@YOUR_WAZUH_MANAGER_IP
```

---

## Step 3.2 — Edit the Main Configuration File

```bash
sudo nano /var/ossec/etc/ossec.conf
```

---

## Step 3.3 — Add the Integration Block

Scroll to the **very bottom** of the file and paste this block **directly before** the closing `</ossec_config>` tag:

```xml
<integration>
  <name>custom-webhook</name>
  <hook_url>http://YOUR_SHUFFLE_IP:3001/api/v1/hooks/webhook_YOUR_HOOK_ID</hook_url>
  <level>7</level>
  <alert_format>json</alert_format>
</integration>
```

Replace `YOUR_SHUFFLE_IP` and `webhook_YOUR_HOOK_ID` with your actual Shuffle Webhook URL.

> **What each field does:**
> - `<hook_url>` — The Shuffle Webhook URL that receives Wazuh alerts
> - `<level>7</level>` — Only forward alerts with severity level 7 or above
> - `<alert_format>json</alert_format>` — Send data as JSON so Shuffle can parse it properly

---

## Step 3.4 — Restart Wazuh Manager

```bash
sudo systemctl restart wazuh-manager
sudo systemctl status wazuh-manager
```

---

## Step 3.5 — Verify Integration Is Active

```bash
sudo tail -f /var/ossec/logs/ossec.log | grep -i integration
```

You should see log lines showing the integration is initializing or sending alerts.

---

---

# 🔵 PART 4 — Configure VirusTotal Enrichment

---

## Step 4.1 — Get Your VirusTotal API Key

1. Go to [virustotal.com](https://www.virustotal.com) and log in
2. Click your profile icon in the top right
3. Select **"API Key"**
4. Copy your free API key

> Free VirusTotal accounts support 4 API requests per minute and 500 per day — more than enough for this lab.

---

## Step 4.2 — Remove the "Change Me" Placeholder Node

When you create a new Shuffle workflow, it includes a placeholder node called **"Change Me"**. This node does nothing and must be deleted before connecting VirusTotal.

1. Click the **"Change Me"** node on the canvas
2. Right-click → **Delete**
3. Click the connection arrow between Webhook and Change Me
4. Press **Delete** key to remove the line

---

## Step 4.3 — Add VirusTotal to the Canvas

1. Click **"Apps"** in the left panel
2. Search for **"VirusTotal v3"**
3. Drag **VirusTotal v3** onto the canvas
4. Draw a connection arrow from the **Webhook** node to the **VirusTotal v3** node

---

## Step 4.4 — Configure the VirusTotal Node

Click the VirusTotal node to open its settings:

**Action:** Select `get an ip report`

**IP Field:** Enter this exact string:
```
$exec.all_fields.full_log.src_ip
```

> This tells Shuffle to extract the attacker's source IP from the Wazuh JSON alert and send it to VirusTotal automatically.

---

## Step 4.5 — Add API Key Authentication

1. Click the **"Authenticate"** button inside the VirusTotal node
2. Set **Authentication Type** to: `ApiKey`
3. Set **Key Name** to: `x-apikey`
4. Paste your VirusTotal API key in the **Value** field
5. Click **Submit**

---

## Step 4.6 — Save the Workflow

Click **Save** at the top of the canvas.

---

---

# 🔵 PART 5 — Add Subnet Filter Conditions

---

We only want to query VirusTotal for **public IP addresses**. Private/internal IPs like `192.168.x.x` or `10.x.x.x` will always return empty results and waste your free API quota.

---

## Step 5.1 — Open the Condition Editor

Click directly on the **connection arrow** between the Webhook node and the VirusTotal node.

A side panel will open. Click **"New Condition"**.

---

## Step 5.2 — Condition Row 1 — Ensure IP Field Is Not Empty

| Field | Value |
|-------|-------|
| Left Box (Source) | `$exec.all_fields.full_log.src_ip` |
| Middle Dropdown | `matches regex` |
| Right Box (Value) | `.+` |

> `.+` means "must contain at least one character." If the IP field is empty, the pipeline stops here and VirusTotal is not called.

Set the connector to: **AND**

---

## Step 5.3 — Condition Row 2 — Block Private / Local IPs

| Field | Value |
|-------|-------|
| Left Box (Source) | `$exec.all_fields.full_log.src_ip` |
| Middle Dropdown | `matches regex` |
| Right Box (Value) | `^(?!192\.168\.)^(?!10\.)^(?!172\.16\.).*` |

> This regex blocks all RFC1918 private IP ranges. Only public IP addresses will pass through to VirusTotal.

---

## Step 5.4 — Save the Conditions

Click **Submit** to save.

---

---

# 🔵 PART 6 — Configure Discord SOC Alerts

---

## Step 6.1 — Create a Discord Webhook

1. Open Discord and go to your SOC server
2. Right-click your SOC alerts channel → **Edit Channel**
3. Go to **Integrations** → **Webhooks** → **New Webhook**
4. Name it: `Shuffle SOC Bot`
5. Click **Copy Webhook URL**

The URL looks like:
```
https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
```

---

## Step 6.2 — Add HTTP Node to Canvas

1. In Shuffle, click **"Apps"** → search for **"HTTP"**
2. Drag the **HTTP** app onto the canvas
3. Draw a connection from the **VirusTotal** node → **HTTP** node
4. Draw a second connection from the **Webhook** node → **HTTP** node

> This triangle layout ensures your Discord channel gets a notification whether or not the VirusTotal lookup succeeds.

---

## Step 6.3 — Configure the HTTP Node

Click the HTTP node and fill in the following:

**Method:** `POST`

**URL:** Paste your Discord Webhook URL

**Headers:** Leave blank

**Body:** Paste this JSON template:

```json
{
  "embeds": [
    {
      "title": "🚨 SOC ALERT: High Severity Intrusion Detected",
      "color": 15158332,
      "fields": [
        {
          "name": "📋 Rule ID",
          "value": "$exec.all_fields.rule.id",
          "inline": true
        },
        {
          "name": "⚠️ Severity Level",
          "value": "$exec.all_fields.rule.level",
          "inline": true
        },
        {
          "name": "🌐 Attacker IP",
          "value": "$exec.all_fields.full_log.src_ip",
          "inline": true
        },
        {
          "name": "🖥️ Target Host",
          "value": "$exec.all_fields.agent.name",
          "inline": true
        },
        {
          "name": "📝 Alert Description",
          "value": "$exec.all_fields.rule.description"
        },
        {
          "name": "🔴 VirusTotal Malicious Score",
          "value": "$virustotal_v3_1.body.data.attributes.last_analysis_stats.malicious"
        }
      ],
      "footer": {
        "text": "🛡️ Wazuh + Shuffle SOAR | SOC Automation Lab"
      }
    }
  ]
}
```

---

## Step 6.4 — Save the Workflow

Click **Save** at the top of the canvas.

---

---

# 🔵 PART 7 — Configure Wazuh Active Response

---

Active Response makes Wazuh automatically block the attacker's IP at the firewall the moment a high-severity alert fires — no human action needed.

---

## Step 7.1 — Create a Custom Detection Rule

SSH into your Wazuh Manager:

```bash
ssh your_user@YOUR_WAZUH_MANAGER_IP
sudo nano /var/ossec/etc/rules/local_rules.xml
```

Add this block inside the `<group>` structure:

```xml
<group name="custom_recon,">

  <!-- Elevate Suricata Nmap scan alerts above the integration threshold -->
  <rule id="100005" level="7">
    <if_sid>86600</if_sid>
    <match>nmap</match>
    <description>Elevated Suricata Alert: Nmap Port Scan Detected</description>
  </rule>

</group>
```

Save and exit.

> **What this rule does:**
> - Triggers when Suricata fires alert SID 86600 (ET SCAN category)
> - Matches any alert containing the word "nmap"
> - Sets severity to level 7, which triggers both the integration webhook and the active response

---

## Step 7.2 — Add Active Response Configuration

```bash
sudo nano /var/ossec/etc/ossec.conf
```

Add these blocks **directly above** the closing `</ossec_config>` tag:

```xml
<!-- Log all active response actions to a dedicated file -->
<localfile>
  <log_format>syslog</log_format>
  <location>/var/ossec/logs/active-responses.log</location>
</localfile>

<!-- Define the firewall-drop command -->
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<!-- Trigger firewall-drop on all agents when a level 7+ alert fires -->
<active-response>
  <command>firewall-drop</command>
  <location>all</location>
  <level>7</level>
  <timeout>600</timeout>
</active-response>
```

> **What `<timeout>600</timeout>` does:** The attacker IP is automatically unblocked after 600 seconds (10 minutes). This prevents permanent accidental blocks in a lab environment.

---

## Step 7.3 — Verify the firewall-drop Script

```bash
ls -la /var/ossec/active-response/bin/firewall-drop
sudo chmod 750 /var/ossec/active-response/bin/firewall-drop
```

---

## Step 7.4 — Validate Configuration and Restart

Check syntax first:
```bash
sudo /var/ossec/bin/wazuh-logtest
```

Then restart Wazuh:
```bash
sudo systemctl restart wazuh-manager
sudo systemctl status wazuh-manager
```

---

---

# 🔵 PART 8 — Red Team Attack Simulation

---

Now we trigger the entire automated pipeline by launching a real Nmap scan from the Kali attacker machine.

---

## Step 8.1 — Confirm All Services Are Running

On your Shuffle server:
```bash
sudo docker compose ps
```

On your Wazuh Manager:
```bash
sudo systemctl status wazuh-manager
```

Both should show everything running and active.

---

## Step 8.2 — Open Monitoring Terminals

Open separate terminal windows so you can watch the pipeline execute in real time.

**Terminal 1 — Watch Active Response Log:**
```bash
ssh your_user@YOUR_WAZUH_MANAGER_IP
sudo tail -f /var/ossec/logs/active-responses.log
```

**Terminal 2 — Watch Wazuh Alerts:**
```bash
sudo tail -f /var/ossec/logs/alerts/alerts.json | grep -i "nmap\|100005"
```

**Terminal 3 — Watch Shuffle Orborus:**
```bash
# On your Shuffle server
sudo docker logs -f shuffle-orborus
```

---

## Step 8.3 — Launch the Attack from Kali Linux

SSH into your Kali machine:
```bash
ssh kali@YOUR_KALI_IP
```

Run an aggressive port scan against the target host:
```bash
sudo nmap -sS -sV -A -p 21,22,80,135,139,445 YOUR_TARGET_HOST_IP
```

> **What each flag does:**
> - `-sS` — TCP SYN stealth scan (sends SYN packets, never completes the handshake)
> - `-sV` — Probe open ports to detect service versions
> - `-A` — Enables OS detection, script scanning, and traceroute
> - `-p` — Scans only specific ports common to Windows environments

---

---

# 🔵 PART 9 — Verify the Full Pipeline

---

## Step 9.1 — Confirm Active Response Fired

On your Wazuh Manager:
```bash
sudo cat /var/ossec/logs/active-responses.log
```

Expected output:
```
Thu Oct 01 03:22:10 UTC 2026 /var/ossec/active-response/bin/firewall-drop add - YOUR_KALI_IP 1727734930 100005
```

---

## Step 9.2 — Confirm Attacker Is Blocked

Back on Kali, test if you can still reach the target:
```bash
ping -c 4 YOUR_TARGET_HOST_IP
```

Expected result:
```
4 packets transmitted, 0 received, 100% packet loss
```

The target host is now unreachable from the attacker machine.

---

## Step 9.3 — Confirm Shuffle Workflow Executed

1. Open Shuffle at `http://YOUR_SHUFFLE_IP:3001`
2. Go to **Workflows** → click your `SOC Incident Response` workflow
3. Click the **"Runs"** or **"Executions"** tab
4. You should see a **green SUCCESS** execution

Click the execution entry to inspect the full data flow:
- Webhook payload received from Wazuh (attacker IP, rule ID, severity)
- VirusTotal API response (malicious score, detection stats)
- HTTP POST response from Discord (status 204 = success)

---

## Step 9.4 — Confirm Discord Alert Was Received

Open your Discord SOC alerts channel. You should see a rich embed message like:

```
🚨 SOC ALERT: High Severity Intrusion Detected

📋 Rule ID          ⚠️ Severity Level     🌐 Attacker IP
100005              7                     [Kali IP Address]

🖥️ Target Host
[Target Hostname]

📝 Alert Description
Elevated Suricata Alert: Nmap Port Scan Detected

🔴 VirusTotal Malicious Score
[Score from VirusTotal]

🛡️ Wazuh + Shuffle SOAR | SOC Automation Lab
```

---

## Step 9.5 — Confirm Automatic IP Unblock After 10 Minutes

After 600 seconds, verify the block was automatically removed:
```bash
sudo grep "firewall-drop delete" /var/ossec/logs/active-responses.log
```

Expected output:
```
Thu Oct 01 03:32:10 UTC 2026 /var/ossec/active-response/bin/firewall-drop delete - YOUR_KALI_IP 1727734930 100005
```

Test connectivity from Kali again — it should now succeed.

---

## 🤝 Contributing

Contributions are welcome. If you want to improve this lab, add integrations, or fix anything:

1. Fork this repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m "Add: description"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

### Ideas for Future Additions

- [ ] TheHive integration for case management
- [ ] MISP integration for threat sharing
- [ ] Slack alternative to Discord notifications
- [ ] Kubernetes deployment option
- [ ] Automated setup bash script

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Wazuh](https://wazuh.com) — Open source SIEM and XDR
- [Shuffle SOAR](https://shuffler.io) — Open source security automation
- [VirusTotal](https://virustotal.com) — Threat intelligence platform
- [Suricata](https://suricata.io) — Open source network IDS/IPS

---

<div align="center">

**Built with ❤️ for the Cybersecurity Community**

*If this lab helped you learn something, please ⭐ star this repository!*

</div>
