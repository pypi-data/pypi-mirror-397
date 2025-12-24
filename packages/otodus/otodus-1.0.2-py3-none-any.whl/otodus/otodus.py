#!/usr/bin/env python3
"""
Otodus- The Megalodon of Automated Pentesting
author -IMApurbo 
"""
from flask import Flask, render_template_string, request, jsonify, Response, send_from_directory
import json
import os
import importlib.resources
import platformdirs
import threading
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import requests
import queue
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import copy
import socket
from collections import defaultdict

app = Flask(__name__)

# Puter AI Configuration
API_URL = "https://api.puter.com/drivers/call"
# ============================================================================
# AUTH TOKEN MANAGEMENT
# ============================================================================
CONFIG_DIR = Path(platformdirs.user_config_dir("otodus", ensure_exists=True))
AUTH_TOKEN_FILE = CONFIG_DIR / "auth_token.txt"

def load_auth_token():
    """Load the saved auth token from user config dir"""
    if AUTH_TOKEN_FILE.exists():
        with open(AUTH_TOKEN_FILE, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token
    return ""

def save_auth_token(token: str):
    """Save the auth token to user config dir"""
    AUTH_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)  # Ensure dir exists
    with open(AUTH_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token.strip())
    print(f"✓ Auth token saved securely to: {AUTH_TOKEN_FILE}")

# Global variable (loaded once at startup)
AUTH_TOKEN = load_auth_token()

@app.route('/get_auth_token', methods=['GET'])
def get_auth_token():
    token = load_auth_token()
    return jsonify({"token": token})

@app.route('/save_auth_token', methods=['POST'])
def save_auth_token_route():
    global AUTH_TOKEN
    data = request.get_json()
    token = data.get("token", "").strip()
    
    if not token:
        return jsonify({"success": False, "error": "Token cannot be empty"}), 400
    
    try:
        save_auth_token(token)
        AUTH_TOKEN = token  # Update the global variable immediately
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

WORKSPACE = Path("./bounty_workspace")
PROMPTS_DIR = Path(importlib.resources.files("otodus") / "prompts")
# === NEW: Dynamic detection of crawlerx executable ===
CRAWLERX_PATH = shutil.which("crawlerx")

if CRAWLERX_PATH is None:
    # Don't raise an immediate error — better to fail gracefully later with a clear message
    CRAWLERX_PATH = None
    print("⚠️  Warning: 'crawlerx' command not found in PATH. Crawling phase will be skipped.")
    print("   Install it with: pip install crawlerx")
else:
    CRAWLERX_PATH = Path(CRAWLERX_PATH)
    print(f"✓ Found crawlerx at: {CRAWLERX_PATH}")


# DNS wordlist for gobuster
DEFAULT_DNS_LIST = """www
mail
ftp
localhost
webmail
smtp
pop
ns1
webdisk
ns2
cpanel
whm
autodiscover
autoconfig
m
imap
test
ns
blog
pop3
dev
www2
admin
forum
news
vpn
ns3
mail2
new
mysql
old
lists
support
mobile
mx
static
docs
beta
shop
sql
secure
demo
cp
calendar
wiki
web
media
email
images
img
www1
intranet
portal
video
sip
dns2
api
cdn
stats
dns1
ns4
www3
dns
search
staging
server
mx1
chat
wap
my
svn
mail1
sites
proxy
ads
host
crm
cms
backup
mx2
lyncdiscover
info
apps
download
remote
db
forums
store
relay
files
newsletter
app
live
owa
en
start
sms
office
exchange
ipv4"""

# Global queues and state
log_queue = queue.Queue()
vuln_queue = queue.Queue()
reasoning_queue = queue.Queue()
state_lock = threading.Lock()

# ADD THESE NEW LINES - Persistent storage
all_logs = []  # Store all logs
all_reasoning = []  # Store all reasoning
all_vulnerabilities = []  # Store all vulnerabilities

# ============================================================================
# DATA MODELS
# ============================================================================
@dataclass
class Memory:
    """Shared memory for AI agents"""
    target: str = ""
    crawlerx_dir: str = ""
    endpoints: List[Dict[str, Any]] = None
    vulnerabilities: List[Dict[str, Any]] = None
    observations: List[str] = None
    decisions: List[str] = None
    tested_payloads: Dict[str, List[str]] = None
    subdomains: List[str] = None
    live_domains: List[str] = None
    selected_target: str = ""
   
    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = []
        if self.vulnerabilities is None:
            self.vulnerabilities = []
        if self.observations is None:
            self.observations = []
        if self.decisions is None:
            self.decisions = []
        if self.tested_payloads is None:
            self.tested_payloads = {}
        if self.subdomains is None:
            self.subdomains = []
        if self.live_domains is None:
            self.live_domains = []

@dataclass
class Endpoint:
    url: str
    method: str = "GET"
    parameters: Dict[str, str] = None
    headers: Dict[str, str] = None
    body: str = ""
    raw_request: str = ""
    response_status: int = 0
    response_body: str = ""
    response_headers: Dict[str, str] = None
    response_time: float = 0.0
   
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.headers is None:
            self.headers = {}
        if self.response_headers is None:
            self.response_headers = {}
   
    def get_signature(self) -> str:
        """Get unique signature for endpoint deduplication"""
        parsed = urlparse(self.url)
        path = parsed.path
        params = tuple(sorted(self.parameters.keys()))
        return f"{self.method}:{path}:{params}"

# Global state
state = {
    "stage": "idle",
    "progress": 0,
    "is_running": False,
}
memory = Memory()
prompt_loader = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def log(message: str, msg_type: str = "info"):
    """Add log message to queue AND persistent storage"""
    log_data = {"message": str(message), "type": msg_type}
    log_queue.put(log_data)
    all_logs.append(log_data)  # ADD THIS LINE
    print(f"[{msg_type.upper()}] {message}")

def reasoning_log(message: str, msg_type: str = "reasoning"):
    """Add reasoning message to special queue AND persistent storage"""
    reasoning_data = {"message": str(message), "type": msg_type}
    reasoning_queue.put(reasoning_data)
    all_reasoning.append(reasoning_data)  # ADD THIS LINE
    print(f"[REASONING] {message}")

def update_state(key: str, value: Any):
    """Thread-safe state update"""
    with state_lock:
        state[key] = value

def get_state_copy() -> Dict[str, Any]:
    """Get thread-safe copy of state"""
    with state_lock:
        return {
            "endpoints": len(memory.endpoints),
            "vulnerabilities": memory.vulnerabilities.copy() if memory.vulnerabilities else [],
            "stage": state["stage"],
            "progress": state["progress"],
            "subdomains": len(memory.subdomains),
            "live_domains": len(memory.live_domains)
        }

def setup_workspace():
    """Create workspace structure"""
    dirs = ["scans", "endpoints", "vulnerabilities", "reports", "recon"]
    for d in dirs:
        (WORKSPACE / d).mkdir(parents=True, exist_ok=True)

def check_tool_installed(tool_name: str) -> bool:
    """Check if a tool is installed"""
    return shutil.which(tool_name) is not None

def run_command(cmd: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """Run shell command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

# ============================================================================
# DOMAIN VALIDATION AND REACHABILITY
# ============================================================================
class DomainValidator:
    """Validates and checks domain reachability"""
   
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Basic domain validation"""
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9]'
            r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'
            r'+[a-zA-Z]{2,}$'
        )
        return bool(domain_pattern.match(domain))
   
    @staticmethod
    def check_dns_resolution(domain: str) -> bool:
        """Check if domain resolves"""
        try:
            socket.gethostbyname(domain)
            reasoning_log(f"✓ DNS resolution successful for {domain}", "recon")
            return True
        except socket.gaierror:
            reasoning_log(f"✗ DNS resolution failed for {domain}", "error")
            return False
   
    @staticmethod
    def check_http_reachability(domain: str) -> Optional[str]:
        """Check if domain is reachable via HTTP or HTTPS"""
        protocols = ['http', 'https']
       
        for protocol in protocols:
            url = f"{protocol}://{domain}"
            try:
                reasoning_log(f"Testing {url}...", "recon")
                response = requests.get(
                    url,
                    timeout=10,
                    allow_redirects=True,
                    verify=False
                )
                if response.status_code < 500:
                    reasoning_log(f"✓ {url} is reachable (Status: {response.status_code})", "success")
                    return url
            except Exception as e:
                reasoning_log(f"✗ {protocol.upper()} failed: {str(e)[:50]}", "error")
       
        return None

# ============================================================================
# SUBDOMAIN ENUMERATION
# ============================================================================
class SubdomainEnumerator:
    """Enumerates subdomains using multiple tools"""
   
    def __init__(self, domain: str, workspace: Path):
        self.domain = domain
        self.workspace = workspace / "recon"
        self.subdomains: Set[str] = set()
   
    def run_subfinder(self) -> Set[str]:
        """Run subfinder for subdomain enumeration"""
        if not check_tool_installed("subfinder"):
            log("⚠️ subfinder not installed, skipping...", "warning")
            return set()
       
        reasoning_log("🔍 Running subfinder...", "recon")
        output_file = self.workspace / f"subfinder_{self.domain}.txt"
       
        cmd = ["subfinder", "-d", self.domain, "-o", str(output_file), "-silent"]
        returncode, stdout, stderr = run_command(cmd, timeout=180)
       
        if returncode != 0:
            log(f"subfinder error: {stderr}", "error")
            return set()
       
        try:
            if output_file.exists():
                with open(output_file, 'r') as f:
                    subs = set(line.strip() for line in f if line.strip())
                reasoning_log(f"✓ subfinder found {len(subs)} subdomains", "success")
                return subs
        except Exception as e:
            log(f"Error reading subfinder output: {e}", "error")
       
        return set()
   
    def run_gobuster(self) -> Set[str]:
        """Run gobuster for DNS brute-forcing"""
        if not check_tool_installed("gobuster"):
            log("⚠️ gobuster not installed, skipping...", "warning")
            return set()
       
        reasoning_log("🔍 Running gobuster DNS...", "recon")
       
        # Create temporary wordlist
        wordlist_file = self.workspace / "dns_wordlist.txt"
        with open(wordlist_file, 'w') as f:
            f.write(DEFAULT_DNS_LIST)
       
        output_file = self.workspace / f"gobuster_{self.domain}.txt"
       
        cmd = [
            "gobuster", "dns",
            "-d", self.domain,
            "-w", str(wordlist_file),
            "-o", str(output_file),
            "-q"
        ]
       
        returncode, stdout, stderr = run_command(cmd, timeout=300)
       
        if returncode != 0 and "no such host" not in stderr.lower():
            log(f"gobuster warning: {stderr[:100]}", "warning")
       
        subs = set()
        try:
            if output_file.exists():
                with open(output_file, 'r') as f:
                    for line in f:
                        if "Found:" in line:
                            match = re.search(r'Found:\s+(\S+)', line)
                            if match:
                                subs.add(match.group(1))
                reasoning_log(f"✓ gobuster found {len(subs)} subdomains", "success")
        except Exception as e:
            log(f"Error reading gobuster output: {e}", "error")
       
        return subs
   
    def merge_results(self) -> List[str]:
        """Merge and deduplicate subdomain results"""
        reasoning_log("🔄 Merging subdomain results...", "recon")
       
        subfinder_subs = self.run_subfinder()
        gobuster_subs = self.run_gobuster()
       
        # Merge
        self.subdomains = subfinder_subs.union(gobuster_subs)
       
        # Add main domain if not present
        self.subdomains.add(self.domain)
       
        # Save merged results
        merged_file = self.workspace / f"all_subdomains_{self.domain}.txt"
        with open(merged_file, 'w') as f:
            for sub in sorted(self.subdomains):
                f.write(f"{sub}\n")
       
        reasoning_log(f"✓ Total unique subdomains: {len(self.subdomains)}", "success")
        return list(self.subdomains)
   
    def filter_live_domains(self, subdomains: List[str]) -> List[str]:
        """Filter live domains using httpx"""
        if not check_tool_installed("httpx"):
            log("⚠️ httpx not installed, using all subdomains", "warning")
            return subdomains
       
        reasoning_log("🔍 Filtering live domains with httpx...", "recon")
       
        # Create input file
        input_file = self.workspace / f"subdomains_input.txt"
        with open(input_file, 'w') as f:
            for sub in subdomains:
                f.write(f"{sub}\n")
       
        output_file = self.workspace / f"live_domains_{self.domain}.txt"
       
        cmd = [
            "httpx",
            "-l", str(input_file),
            "-o", str(output_file),
            "-silent",
            "-timeout", "10",
            "-follow-redirects",
            "-status-code"
        ]
       
        returncode, stdout, stderr = run_command(cmd, timeout=300)
       
        live = []
        try:
            if output_file.exists():
                with open(output_file, 'r') as f:
                    for line in f:
                        # Parse httpx output: http://domain.com [200]
                        match = re.search(r'(https?://[^\s\[]+)', line)
                        if match:
                            live.append(match.group(1))
                reasoning_log(f"✓ Found {len(live)} live domains", "success")
        except Exception as e:
            log(f"Error reading httpx output: {e}", "error")
       
        return live if live else subdomains

# ============================================================================
# CRAWLERX INTEGRATION
# ============================================================================
class CrawlerXRunner:
    def __init__(self, crawlerx_path: Optional[Path]):
        self.crawlerx_path = crawlerx_path

    def check_crawlerx(self) -> bool:
        if self.crawlerx_path is None or not self.crawlerx_path.exists():
            log("❌ CrawlerX not found in PATH", "error")
            log("Install with: pip install crawlerx", "info")
            return False
        return True

    def run_crawler(self, target_url: str, output_dir: Path) -> Optional[Path]:
        if not self.check_crawlerx():
            return None

        cmd = [
            str(self.crawlerx_path),   # ← safe because we already checked
            "-u", target_url,
            "-o", str(output_dir)
        ]
       
        log(f"Command: {' '.join(cmd)}", "info")
       
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
           
            # Stream output
            for line in process.stdout:
                if line.strip():
                    log(f"CrawlerX: {line.strip()}", "info")
           
            process.wait(timeout=600)
           
            if process.returncode == 0:
                # Find the created directory
                domain = urlparse(target_url).netloc
                crawlerx_dir = output_dir / f"crawlerx_{domain}"
               
                if crawlerx_dir.exists():
                    reasoning_log(f"✓ CrawlerX completed: {crawlerx_dir}", "success")
                    return crawlerx_dir
                else:
                    log(f"CrawlerX output directory not found", "error")
                    return None
            else:
                log(f"CrawlerX failed with code {process.returncode}", "error")
                return None
               
        except subprocess.TimeoutExpired:
            log("CrawlerX timeout (10 minutes)", "error")
            process.kill()
            return None
        except Exception as e:
            log(f"CrawlerX error: {e}", "error")
            return None

# ============================================================================
# CRAWLERX PARSER WITH DEDUPLICATION
# ============================================================================
class CrawlerXParser:
    """Parses CrawlerX output with endpoint deduplication"""
   
    def __init__(self, crawlerx_dir: Path):
        self.crawlerx_dir = Path(crawlerx_dir)
        if not self.crawlerx_dir.exists():
            raise FileNotFoundError(f"CrawlerX directory not found: {crawlerx_dir}")
   
    def parse_raw_request(self, req_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a .req file containing raw HTTP request"""
        try:
            with open(req_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
           
            lines = content.split('\n')
            if not lines:
                return None
           
            request_line = lines[0].strip()
            parts = request_line.split(' ')
            if len(parts) < 2:
                return None
           
            method = parts[0]
            path = parts[1]
           
            headers = {}
            body = ""
            in_body = False
           
            for line in lines[1:]:
                if not line.strip() and not in_body:
                    in_body = True
                    continue
               
                if in_body:
                    body += line + '\n'
                elif ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
           
            return {
                'method': method,
                'path': path,
                'headers': headers,
                'body': body.strip(),
                'raw': content
            }
       
        except Exception as e:
            log(f"Error parsing {req_file.name}: {e}", "error")
            return None
   
    def load_all_endpoints(self) -> List[Endpoint]:
        """Load all endpoints from CrawlerX output with deduplication"""
        endpoints = []
        signatures_seen = set()
       
        get_dir = self.crawlerx_dir / "get"
        if get_dir.exists():
            reasoning_log(f"📂 Loading GET requests from {get_dir}", "recon")
            for req_file in get_dir.glob("*.req"):
                endpoint = self._parse_and_create_endpoint(req_file)
                if endpoint:
                    sig = endpoint.get_signature()
                    if sig not in signatures_seen:
                        endpoints.append(endpoint)
                        signatures_seen.add(sig)
       
        post_dir = self.crawlerx_dir / "post"
        if post_dir.exists():
            reasoning_log(f"📂 Loading POST requests from {post_dir}", "recon")
            for req_file in post_dir.glob("*.req"):
                endpoint = self._parse_and_create_endpoint(req_file)
                if endpoint:
                    sig = endpoint.get_signature()
                    if sig not in signatures_seen:
                        endpoints.append(endpoint)
                        signatures_seen.add(sig)
       
        reasoning_log(f"✅ Loaded {len(endpoints)} unique endpoints (deduplicated)", "success")
        return endpoints
   
    def _parse_and_create_endpoint(self, req_file: Path) -> Optional[Endpoint]:
        """Parse request file and create Endpoint object"""
        parsed = self.parse_raw_request(req_file)
        if not parsed:
            return None
       
        host = parsed['headers'].get('Host', '')
        if not host:
            return None
       
        protocol = 'https' if 'https' in host.lower() or '443' in host else 'http'
        full_url = f"{protocol}://{host}{parsed['path']}"
       
        parsed_url = urlparse(full_url)
        url_params = parse_qs(parsed_url.query)
        params_dict = {k: v[0] if v else '' for k, v in url_params.items()}
       
        if parsed['method'] == 'POST' and parsed['body']:
            try:
                body_params = parse_qs(parsed['body'])
                for k, v in body_params.items():
                    params_dict[k] = v[0] if v else ''
            except:
                pass
       
        return Endpoint(
            url=full_url,
            method=parsed['method'],
            parameters=params_dict,
            headers=parsed['headers'],
            body=parsed['body'],
            raw_request=parsed['raw']
        )

# ============================================================================
# IMPROVED AI CALLING FUNCTION
# ============================================================================
def call_ai(message, show_prompt=False):
    """Call Puter AI API"""
    try:
        if show_prompt:
            preview = message[:200] + "..." if len(message) > 200 else message
            log(f"🤖 AI Prompt: {preview}", "ai")
        payload = {
            "interface": "puter-chat-completion",
            "driver": "openai-completion",
            "test_mode": False,
            "method": "complete",
            "args": {
                "messages": [
                    {"content": message}
                ],
                "model": "gpt-4o-mini"
            },
            "auth_token": AUTH_TOKEN
        }
        headers = {
            "Host": "api.puter.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json",
            "Origin": "http://localhost:5000",
            "Referer": "http://localhost:5000/",
            "Connection": "close",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
        }
        log("⏳ Waiting for AI response...", "ai")
        response = requests.post(
            API_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=60
        )
        if response.status_code != 200:
            log(f"❌ AI HTTP Error {response.status_code}", "error")
            return None
        data = response.json()
        if not data.get("success"):
            log(f"❌ AI API Error: {data}", "error")
            return None
        ai_response = data["result"]["message"]["content"]
        log(f"🤖 AI Response received", "ai-response")
        return ai_response
    except requests.exceptions.Timeout:
        log("❌ AI request timeout", "error")
    except Exception as e:
        log(f"❌ AI Exception: {str(e)}", "error")
    return None

# ============================================================================
# REQUEST SENDER
# ============================================================================
class RequestSender:
    """Sends requests and captures responses"""
   
    @staticmethod
    def send_request(endpoint: Endpoint) -> Endpoint:
        """Send request and capture response"""
        try:
            reasoning_log(f"📤 Sending {endpoint.method} to {endpoint.url[:60]}...", "testing")
           
            start_time = time.time()
           
            if endpoint.method == 'GET':
                response = requests.get(
                    endpoint.url,
                    headers=endpoint.headers,
                    timeout=15,
                    allow_redirects=True,
                    verify=False
                )
            elif endpoint.method == 'POST':
                response = requests.post(
                    endpoint.url,
                    headers=endpoint.headers,
                    data=endpoint.body,
                    timeout=15,
                    allow_redirects=True,
                    verify=False
                )
            else:
                response = requests.request(
                    endpoint.method,
                    endpoint.url,
                    headers=endpoint.headers,
                    data=endpoint.body,
                    timeout=15,
                    verify=False
                )
           
            response_time = time.time() - start_time
           
            endpoint.response_status = response.status_code
            endpoint.response_body = response.text[:5000]
            endpoint.response_headers = dict(response.headers)
            endpoint.response_time = response_time
           
            reasoning_log(f"✅ Response: {response.status_code} ({response_time:.2f}s)", "success")
           
            return endpoint
           
        except Exception as e:
            log(f"❌ Request error: {e}", "error")
            endpoint.response_status = 0
            endpoint.response_body = f"Error: {str(e)}"
            return endpoint

# ============================================================================
# PROMPT SYSTEM
# ============================================================================
class PromptLoader:
    """Loads and manages vulnerability prompts"""
   
    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self.prompts = {}
        self.load_prompts()
   
    def load_prompts(self):
        """Load all prompt files from prompts directory"""
        if not self.prompts_dir.exists():
            log("⚠️ Prompts directory not found, creating...", "warning")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            return
       
        for prompt_file in self.prompts_dir.glob("*.txt"):
            vuln_type = prompt_file.stem
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.prompts[vuln_type] = content
                    log(f"✓ Loaded prompt: {vuln_type}", "success")
            except Exception as e:
                log(f"❌ Error loading {prompt_file}: {e}", "error")
   
    def get_prompt(self, vuln_type: str) -> Optional[str]:
        """Get prompt for specific vulnerability type"""
        return self.prompts.get(vuln_type)
   
    def get_all_types(self) -> List[str]:
        """Get all loaded vulnerability types"""
        return list(self.prompts.keys())
   
    def get_classification_prompt(self) -> str:
        """Generate prompt for endpoint classification"""
        types = ", ".join(self.get_all_types())
        return f"""Available vulnerability types: {types}
Analyze the endpoint and classify which vulnerability types it might be susceptible to.
Return ONLY a JSON array of vulnerability types, ordered by likelihood (most likely first).
Example: ["sql_injection", "xss_reflected", "idor"]
If no vulnerabilities seem likely, return an empty array: []"""

# ============================================================================
# AGENT CLASSES (Planner, Classifier, Exploit, Verifier)
# ============================================================================
class PlannerAgent:
    """Plans the overall testing strategy"""
   
    def __init__(self, memory: Memory):
        self.memory = memory
   
    def create_plan(self, endpoints: List[Endpoint]) -> Dict[str, Any]:
        """Create testing plan based on loaded endpoints"""
        reasoning_log("🧠 Planner Agent: Analyzing endpoints and creating strategy...", "agent")
       
        get_count = sum(1 for ep in endpoints if ep.method == 'GET')
        post_count = sum(1 for ep in endpoints if ep.method == 'POST')
        with_params = sum(1 for ep in endpoints if ep.parameters)
       
        plan_prompt = f"""You are a bug bounty security researcher planning a testing strategy.
TARGET ANALYSIS:
- Total Unique Endpoints: {len(endpoints)}
- GET Requests: {get_count}
- POST Requests: {post_count}
- Parameterized Endpoints: {with_params}
SAMPLE ENDPOINTS:
{self._format_endpoints_sample(endpoints[:15])}
CREATE A TESTING PLAN:
1. Prioritize which endpoints to test first (based on parameters and methods)
2. Identify which vulnerability types are most likely
3. Suggest testing order
4. Estimate risk levels
Return your plan as JSON:
{{
  "priority_endpoints": ["url1", "url2"],
  "vulnerability_focus": ["sqli", "xss", "idor"],
  "testing_strategy": "description",
  "risk_assessment": "low/medium/high"
}}"""
       
        response = call_ai(plan_prompt)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    plan = json.loads(json_match.group())
                    self.memory.decisions.append(f"Plan: {plan.get('testing_strategy', 'N/A')}")
                    reasoning_log(f"📋 Strategy: {plan.get('testing_strategy', 'N/A')}", "decision")
                    return plan
            except Exception as e:
                log(f"Error parsing plan: {e}", "error")
       
        return {
            "priority_endpoints": [],
            "vulnerability_focus": [],
            "testing_strategy": "default scan",
            "risk_assessment": "medium"
        }
   
    def _format_endpoints_sample(self, endpoints: List[Endpoint]) -> str:
        """Format endpoints for AI"""
        result = []
        for ep in endpoints:
            params_str = f"params: {list(ep.parameters.keys())}" if ep.parameters else "no params"
            result.append(f"- [{ep.method}] {ep.url[:80]} ({params_str})")
        return "\n".join(result)

class ClassificationAgent:
    """Classifies endpoints by vulnerability type"""
   
    def __init__(self, memory: Memory, prompt_loader: PromptLoader):
        self.memory = memory
        self.prompt_loader = prompt_loader
   
    def classify_endpoint(self, endpoint: Endpoint) -> List[str]:
        """Classify endpoint using AI and request/response data"""
        reasoning_log(f"🧬 Classifying {endpoint.url[:60]}...", "classification")
       
        classification_prompt = f"""{self.prompt_loader.get_classification_prompt()}
ENDPOINT TO CLASSIFY:
URL: {endpoint.url}
Method: {endpoint.method}
Parameters: {json.dumps(endpoint.parameters, indent=2)}
RESPONSE STATUS: {endpoint.response_status}
RESPONSE TIME: {endpoint.response_time:.2f}s
RESPONSE BODY (first 1000 chars):
{endpoint.response_body[:1000]}
Based on the request/response data, return a JSON array of the TOP 3 most likely vulnerability types.
Return ONLY the JSON array, nothing else."""
       
        response = call_ai(classification_prompt, show_prompt=False)
        if response:
            try:
                json_match = re.search(r'\[[\s\S]*?\]', response)
                if json_match:
                    vuln_types = json.loads(json_match.group())
                    if vuln_types:
                        reasoning_log(f"✓ Classified as: {', '.join(vuln_types[:2])}", "classification")
                        return vuln_types
            except Exception as e:
                log(f"Classification parse error: {e}", "error")
       
        return []

class ExploitAgent:
    """Generates and tests payloads"""
  
    def __init__(self, memory: Memory, prompt_loader: PromptLoader):
        self.memory = memory
        self.prompt_loader = prompt_loader
  
    def test_endpoint(self, endpoint: Endpoint, vuln_types: List[str]) -> List[Dict[str, Any]]:
        """Test endpoint for vulnerabilities"""
        findings = []
      
        for vuln_type in vuln_types[:2]:  # Test top 2 most likely vuln types
            if not state["is_running"]:
                break
          
            reasoning_log(f"🎯 Testing {endpoint.url[:60]} for {vuln_type}", "testing")
          
            vuln_prompt = self.prompt_loader.get_prompt(vuln_type)
            if not vuln_prompt:
                continue
          
            payloads = self._generate_payloads(endpoint, vuln_type, vuln_prompt)
          
            for payload in payloads[:3]:  # Test up to 3 payloads per vuln type
                result = self._test_payload(endpoint, payload, vuln_type)
                if result:
                    findings.append(result)
      
        return findings
  
    def _generate_payloads(self, endpoint: Endpoint, vuln_type: str, vuln_prompt: str) -> List[str]:
        """Generate payloads using AI"""
      
        prompt = f"""{vuln_prompt}
ENDPOINT TO TEST:
URL: {endpoint.url}
Method: {endpoint.method}
Parameters: {json.dumps(endpoint.parameters, indent=2)}
ORIGINAL RESPONSE:
Status: {endpoint.response_status}
Body snippet: {endpoint.response_body[:500]}

Generate 3-5 targeted payloads to test for {vuln_type}.
Focus on:
- Payloads that match the vulnerability type
- Safe payloads (no damage)
- Payloads that can be verified in responses

Return ONLY a JSON array of payload strings:
["payload1", "payload2", "payload3"]"""
      
        response = call_ai(prompt, show_prompt=False)
        if response:
            try:
                json_match = re.search(r'\[[\s\S]*?\]', response)
                if json_match:
                    payloads = json.loads(json_match.group())
                    reasoning_log(f"🔧 Generated {len(payloads)} payloads for {vuln_type}", "payload")
                    return payloads
            except Exception as e:
                log(f"Payload generation parse error: {e}", "error")
      
        return []
  
    def _test_payload(self, endpoint: Endpoint, payload: str, vuln_type: str) -> Optional[Dict[str, Any]]:
        """Test a single payload and return finding with raw request/response"""
        try:
            test_endpoint = self._inject_payload(endpoint, payload)
          
            reasoning_log(f"📤 Testing payload: {payload[:50]}...", "testing")
          
            # Send the malicious request
            test_endpoint = RequestSender.send_request(test_endpoint)
          
            # Track tested payloads
            if endpoint.url not in self.memory.tested_payloads:
                self.memory.tested_payloads[endpoint.url] = []
            self.memory.tested_payloads[endpoint.url].append(payload)
          
            # Reconstruct full raw vulnerable response (headers + body)
            raw_vulnerable_response = f"HTTP/1.1 {test_endpoint.response_status}\n"
            for key, value in test_endpoint.response_headers.items():
                raw_vulnerable_response += f"{key}: {value}\n"
            raw_vulnerable_response += f"\n{test_endpoint.response_body}"
          
            return {
                "endpoint": endpoint.url,
                "method": test_endpoint.method,
                "vuln_type": vuln_type,
                "payload": payload,
                "response_code": test_endpoint.response_status,
                "response_body": test_endpoint.response_body,
                "response_time": test_endpoint.response_time,
                "response_headers": test_endpoint.response_headers,
                "original_response_code": endpoint.response_status,
                "raw_request": endpoint.raw_request,  # Original clean request from CrawlerX
                "raw_vulnerable_response": raw_vulnerable_response  # Full response showing vuln
            }
      
        except Exception as e:
            log(f"Payload test error: {e}", "error")
            return None
  
    def _inject_payload(self, endpoint: Endpoint, payload: str) -> Endpoint:
        """Inject payload into endpoint parameters or URL"""
        test_endpoint = copy.deepcopy(endpoint)
      
        if endpoint.parameters:
            # Inject into first parameter
            first_param = list(endpoint.parameters.keys())[0]
            test_endpoint.parameters[first_param] = payload
          
            parsed = urlparse(endpoint.url)
            new_query = urlencode(test_endpoint.parameters)
            test_endpoint.url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
          
            if endpoint.method == 'POST':
                test_endpoint.body = new_query
        else:
            # Fallback: append as query param
            separator = '&' if '?' in endpoint.url else '?'
            test_endpoint.url = f"{endpoint.url}{separator}test={payload}"
      
        return test_endpoint

class VerificationAgent:
    """Verifies vulnerability findings using AI"""
  
    def __init__(self, memory: Memory, prompt_loader: PromptLoader):
        self.memory = memory
        self.prompt_loader = prompt_loader
  
    def verify_finding(self, finding: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verify if finding is a true positive"""
        reasoning_log(f"🔬 Verifying {finding['vuln_type']} on {finding['endpoint'][:60]}...", "verification")
        
        vuln_prompt = self.prompt_loader.get_prompt(finding['vuln_type']) or ""
        
        verification_prompt = f"""You are a senior security researcher verifying a potential vulnerability.

VULNERABILITY TYPE: {finding['vuln_type']}

VULNERABILITY KNOWLEDGE:
{vuln_prompt}

TEST DETAILS:
Endpoint: {finding['endpoint']}
Method: {finding['method']}
Payload: {finding['payload']}
Original Status Code: {finding.get('original_response_code', 'N/A')}
Test Status Code: {finding['response_code']}
Response Time: {finding.get('response_time', 0):.2f}s

RAW REQUEST (Baseline):
{finding.get('raw_request', 'Not available')}

VULNERABLE RESPONSE:
{finding.get('raw_vulnerable_response', 'Not available')}

RESPONSE BODY SNIPPET (first 1500 chars):
{finding['response_body'][:1500]}

TASK:
1. Is this a TRUE POSITIVE or FALSE POSITIVE?
2. What specific evidence in the request/response confirms or refutes it?
3. What is the severity? (Critical/High/Medium/Low/Info)
4. What is the real-world impact?
5. Suggest 3-5 keywords or patterns from the response that prove the vulnerability (for highlighting)

Return ONLY valid JSON in this exact format:
{{
  "verdict": "TRUE_POSITIVE" or "FALSE_POSITIVE",
  "confidence": "high" or "medium" or "low",
  "severity": "Critical" or "High" or "Medium" or "Low" or "Info",
  "evidence": ["evidence point 1", "evidence point 2"],
  "impact": "Clear description of impact",
  "cwe": "CWE-XXX" or "N/A",
  "highlight_keywords": ["keyword1", "keyword2", "error message fragment", "payload reflection"]
}}"""
        
        response = call_ai(verification_prompt)
        if not response:
            log("AI verification failed: no response", "error")
            return None
        
        try:
            # Extract JSON from AI response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if not json_match:
                log("No JSON found in verification response", "error")
                return None
            
            verification = json.loads(json_match.group())
            
            if verification.get('verdict') == 'TRUE_POSITIVE':
                reasoning_log(
                    f"✅ CONFIRMED: {finding['vuln_type']} ({verification.get('severity', 'Medium')}) "
                    f"on {finding['endpoint'][:50]}",
                    "confirmed"
                )
                
                confirmed_vuln = {
                    "type": finding['vuln_type'],
                    "severity": verification.get('severity', 'Medium'),
                    "url": finding['endpoint'],
                    "method": finding['method'],
                    "payload": finding['payload'],
                    "evidence": verification.get('evidence', []),
                    "impact": verification.get('impact', 'No impact description provided'),
                    "cwe": verification.get('cwe', 'N/A'),
                    "confidence": verification.get('confidence', 'medium'),
                    "response_code": finding['response_code'],
                    "verified_at": datetime.now().isoformat(),
                    # Raw proof for frontend
                    "raw_request": finding.get('raw_request', 'Not available'),
                    "raw_vulnerable_response": finding.get('raw_vulnerable_response', 'Not available'),
                    # Keywords for automatic highlighting
                    "highlight_keywords": verification.get('highlight_keywords', [])
                }
                all_vulnerabilities.append(confirmed_vuln)
                return confirmed_vuln
            else:
                reasoning_log(f"❌ FALSE POSITIVE: {finding['vuln_type']}", "rejected")
                
        except json.JSONDecodeError as e:
            log(f"JSON parse error in verification: {e}", "error")
        except Exception as e:
            log(f"Verification error: {e}", "error")
        
        return None
# ============================================================================
# ORCHESTRATOR
# ============================================================================
class AgentOrchestrator:
    """Orchestrates the complete workflow"""
   
    def __init__(self, memory: Memory, prompt_loader: PromptLoader):
        self.memory = memory
        self.prompt_loader = prompt_loader
        self.planner = PlannerAgent(memory)
        self.classifier = ClassificationAgent(memory, prompt_loader)
        self.exploit = ExploitAgent(memory, prompt_loader)
        self.verifier = VerificationAgent(memory, prompt_loader)
   
    def run(self, domain: str):
        """Main orchestration workflow"""
        try:
            update_state("stage", "Initializing")
            update_state("progress", 2)
            reasoning_log("🤖 AI Agent System Starting...", "system")
           
            # PHASE 1: Domain Validation
            reasoning_log("=" * 60, "system")
            reasoning_log("PHASE 1: DOMAIN VALIDATION", "system")
            reasoning_log("=" * 60, "system")
            update_state("stage", "Validating Domain")
            update_state("progress", 5)
           
            validator = DomainValidator()
           
            if not validator.is_valid_domain(domain):
                log(f"❌ Invalid domain format: {domain}", "error")
                return
           
            if not validator.check_dns_resolution(domain):
                log(f"❌ Domain does not resolve: {domain}", "error")
                return
           
            update_state("progress", 10)
           
            # PHASE 2: Subdomain Enumeration
            reasoning_log("=" * 60, "system")
            reasoning_log("PHASE 2: SUBDOMAIN ENUMERATION", "system")
            reasoning_log("=" * 60, "system")
            update_state("stage", "Enumerating Subdomains")
            update_state("progress", 15)
           
            enumerator = SubdomainEnumerator(domain, WORKSPACE)
            all_subdomains = enumerator.merge_results()
            self.memory.subdomains = all_subdomains
           
            update_state("progress", 30)
           
            # PHASE 3: Live Domain Filtering
            reasoning_log("=" * 60, "system")
            reasoning_log("PHASE 3: LIVE DOMAIN FILTERING", "system")
            reasoning_log("=" * 60, "system")
            update_state("stage", "Filtering Live Domains")
            update_state("progress", 35)
           
            live_domains = enumerator.filter_live_domains(all_subdomains)
            self.memory.live_domains = live_domains
           
            if not live_domains:
                log("⚠️ No live domains found, using main domain", "warning")
                live_domains = [domain]
           
            update_state("progress", 40)
           
            # PHASE 4: Collect Reachable Targets
            reasoning_log("=" * 60, "system")
            reasoning_log("PHASE 4: COLLECTING REACHABLE TARGETS", "system")
            reasoning_log("=" * 60, "system")
            update_state("stage", "Checking Reachability")
            update_state("progress", 42)
           
            reachable_targets = self.collect_reachable_targets(domain, live_domains)
            total_targets = len(reachable_targets)
           
            if total_targets == 0:
                log("❌ No reachable targets found", "error")
                return
           
            reasoning_log(f"✓ Found {total_targets} reachable targets", "success")
            update_state("progress", 45)
           
            # Process each target sequentially
            for idx, (target_name, target_url) in enumerate(reachable_targets, 1):
                if not state["is_running"]:
                    break
               
                reasoning_log("=" * 60, "system")
                reasoning_log(f"PROCESSING TARGET {idx}/{total_targets}: {target_name} ({target_url})", "system")
                reasoning_log("=" * 60, "system")
               
                # Reset per-target memory
                self.memory = Memory(target=target_name, selected_target=target_url)
               
                # Calculate base progress for this target
                base_progress = ((idx - 1) / total_targets) * 100
               
                self._process_single_target(target_url, target_name, base_progress, total_targets)
           
            update_state("progress", 100)
            update_state("stage", "completed")
           
            # Summary
            reasoning_log("=" * 60, "system")
            reasoning_log("✅ SCAN COMPLETED", "success")
            reasoning_log("=" * 60, "system")
            reasoning_log(f"📊 STATISTICS:", "system")
            reasoning_log(f" • Domain: {domain}", "system")
            reasoning_log(f" • Subdomains Found: {len(self.memory.subdomains)}", "system")
            reasoning_log(f" • Live Domains: {len(self.memory.live_domains)}", "system")
            reasoning_log(f" • Targets Processed: {total_targets}", "system")
            reasoning_log("=" * 60, "system")
           
        except Exception as e:
            log(f"❌ Fatal error: {e}", "error")
            import traceback
            log(traceback.format_exc(), "error")
            update_state("stage", "error")
        finally:
            update_state("is_running", False)
   
    def collect_reachable_targets(self, domain: str, live_domains: List[str]) -> List[Tuple[str, str]]:
        """Return list of (target_name, reachable_url) pairs"""
        validator = DomainValidator()
        targets = []
       
        # Add live subdomains
        for sub in live_domains:
            url = validator.check_http_reachability(sub)
            if url:
                targets.append((sub, url))
                reasoning_log(f"✓ {sub} is reachable: {url}", "success")
       
        # Add main domain if not already included
        main_url = validator.check_http_reachability(domain)
        if main_url and not any(sub == domain for sub, _ in targets):
            targets.append((domain, main_url))
            reasoning_log(f"✓ Main domain is reachable: {main_url}", "success")
       
        return targets
   
    def _process_single_target(self, target_url: str, target_name: str, base_progress: float, total_targets: int):
        """Process one target completely"""
        # Per-target workspace
        target_workspace = WORKSPACE / target_name.replace(".", "_")
        target_workspace.mkdir(parents=True, exist_ok=True)
       
        # PHASE 5: Run CrawlerX
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 5: RUNNING CRAWLERX", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Running CrawlerX on {target_name}")
        update_state("progress", base_progress + 2)
       
        crawler = CrawlerXRunner(CRAWLERX_PATH)
        crawlerx_dir = crawler.run_crawler(target_url, target_workspace)
       
        if not crawlerx_dir:
            log(f"❌ CrawlerX failed for {target_name}", "error")
            return
       
        self.memory.crawlerx_dir = str(crawlerx_dir)
        update_state("progress", base_progress + 10)
       
        # PHASE 6: Load & Deduplicate Endpoints
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 6: LOADING & DEDUPLICATING ENDPOINTS", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Loading Endpoints for {target_name}")
       
        parser = CrawlerXParser(crawlerx_dir)
        endpoints = parser.load_all_endpoints()
       
        if not endpoints:
            log(f"❌ No endpoints found for {target_name}", "error")
            return
       
        update_state("progress", base_progress + 15)
       
        # PHASE 7: Capture Responses
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 7: CAPTURING RESPONSES", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Capturing Responses for {target_name}")
       
        for idx, endpoint in enumerate(endpoints[:30]):  # Limit for demo
            if not state["is_running"]:
                return
           
            endpoints[idx] = RequestSender.send_request(endpoint)
            progress = base_progress + 15 + int((idx + 1) * 10 / min(30, len(endpoints)))
            update_state("progress", progress)
       
        self.memory.endpoints = [asdict(ep) for ep in endpoints[:30]]
        update_state("progress", base_progress + 25)
       
        # PHASE 8: Strategic Planning
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 8: STRATEGIC PLANNING", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Strategic Planning for {target_name}")
        plan = self.planner.create_plan(endpoints[:30])
        update_state("progress", base_progress + 30)
       
        # PHASE 9: Classification
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 9: VULNERABILITY CLASSIFICATION", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Classifying Endpoints for {target_name}")
       
        classified = []
        for idx, endpoint in enumerate(endpoints[:20]):
            if not state["is_running"]:
                return
           
            vuln_types = self.classifier.classify_endpoint(endpoint)
            if vuln_types:
                classified.append((endpoint, vuln_types))
           
            progress = base_progress + 30 + int((idx + 1) * 5 / min(20, len(endpoints)))
            update_state("progress", progress)
       
        update_state("progress", base_progress + 35)
       
        # PHASE 10: Exploitation
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 10: INTELLIGENT EXPLOITATION", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Testing Vulnerabilities on {target_name}")
       
        all_findings = []
        for idx, (endpoint, vuln_types) in enumerate(classified[:15]):
            if not state["is_running"]:
                return
           
            findings = self.exploit.test_endpoint(endpoint, vuln_types)
            all_findings.extend(findings)
           
            progress = base_progress + 35 + int((idx + 1) * 10 / min(15, len(classified)))
            update_state("progress", progress)
       
        update_state("progress", base_progress + 45)
       
        # PHASE 11: Verification
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 11: VERIFICATION", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Verifying Findings for {target_name}")
       
        confirmed = []
        for idx, finding in enumerate(all_findings):
            if not state["is_running"]:
                return
           
            verified = self.verifier.verify_finding(finding)
            if verified:
                confirmed.append(verified)
                self.memory.vulnerabilities.append(verified)
                vuln_queue.put(verified)
           
            progress = base_progress + 45 + int((idx + 1) * 8 / max(1, len(all_findings)))
            update_state("progress", progress)
       
        update_state("progress", base_progress + 53)
       
        # PHASE 12: Save Results
        reasoning_log("=" * 60, "system")
        reasoning_log("PHASE 12: SAVING RESULTS", "system")
        reasoning_log("=" * 60, "system")
        update_state("stage", f"Saving Results for {target_name}")
        self._save_single_target_results(target_name)
        update_state("progress", base_progress + 55)  # End of this target
   
    def _save_single_target_results(self, target_name: str):
        """Save results for a single target"""
        target_safe = target_name.replace(".", "_")
        target_dir = WORKSPACE / "reports" / target_safe
        target_dir.mkdir(parents=True, exist_ok=True)
       
        try:
            with open(target_dir / "endpoints.json", 'w') as f:
                json.dump(self.memory.endpoints, f, indent=2)
           
            with open(target_dir / "vulnerabilities.json", 'w') as f:
                json.dump(self.memory.vulnerabilities, f, indent=2)
           
            with open(target_dir / "memory.json", 'w') as f:
                json.dump({
                    "target": self.memory.target,
                    "observations": self.memory.observations,
                    "decisions": self.memory.decisions,
                    "tested_payloads": self.memory.tested_payloads
                }, f, indent=2)
           
            reasoning_log(f"💾 Results saved for {target_name}", "success")
        except Exception as e:
            log(f"Error saving for {target_name}: {e}", "error")

# ============================================================================
# HTML TEMPLATE
# ============================================================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Otodus- The Megalodon of Automated Pentesting</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #fff;
            height: 100vh;
            overflow: hidden;
        }
        .container { display: flex; height: 100vh; }
        .sidebar {
            width: 280px;
            background: rgba(20, 20, 30, 0.95);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(167, 139, 250, 0.3);
            padding: 30px 20px;
            display: flex;
            flex-direction: column;
        }
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(135deg, #a78bfa, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
                /* Vulnerability Cards - Collapsible */
        .vuln-card {
            background: rgba(55, 55, 78, 0.6);
            border-left: 4px solid;
            border-radius: 8px;
            margin-bottom: 12px;
            animation: slideIn 0.3s ease;
            overflow: hidden;
        }

        .vuln-card.Critical { border-color: #ef4444; }
        .vuln-card.High { border-color: #f97316; }
        .vuln-card.Medium { border-color: #eab308; }
        .vuln-card.Low { border-color: #3b82f6; }
        .vuln-card.Info { border-color: #6b7280; }

        .vuln-title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 16px;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s;
        }

        .vuln-title:hover {
            background: rgba(167, 139, 250, 0.1);
        }

        .vuln-title-left {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1;
        }

        .vuln-type-name {
            font-weight: 600;
            font-size: 0.95rem;
            color: #fff;
        }

        .vuln-severity-badge {
            font-size: 0.7rem;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .vuln-severity-badge.Critical { background: #ef4444; color: #fff; }
        .vuln-severity-badge.High { background: #f97316; color: #fff; }
        .vuln-severity-badge.Medium { background: #eab308; color: #000; }
        .vuln-severity-badge.Low { background: #3b82f6; color: #fff; }
        .vuln-severity-badge.Info { background: #6b7280; color: #fff; }

        .vuln-method {
            font-size: 0.75rem;
            padding: 2px 8px;
            background: rgba(167, 139, 250, 0.3);
            border-radius: 4px;
            color: #a78bfa;
            font-family: 'Courier New', monospace;
        }

        .vuln-url-preview {
            font-size: 0.8rem;
            color: #9ca3af;
            font-family: 'Courier New', monospace;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 400px;
        }

        .vuln-expand-icon {
            font-size: 1.2rem;
            color: #a78bfa;
            transition: transform 0.3s;
        }

        .vuln-card.expanded .vuln-expand-icon {
            transform: rotate(90deg);
        }

        .vuln-details {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease-out;
        }

        .vuln-card.expanded .vuln-details {
            max-height: 5000px;
            transition: max-height 0.5s ease-in;
        }

        .vuln-details-content {
            padding: 0 16px 16px 16px;
            font-size: 0.85rem;
        }

        .vuln-section {
            margin-bottom: 16px;
        }

        .vuln-section-title {
            color: #a78bfa;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .vuln-section-content {
            color: #d1d5db;
            line-height: 1.6;
            padding-left: 8px;
        }

        .vuln-evidence-list {
            list-style: none;
            padding-left: 0;
        }

        .vuln-evidence-list li {
            padding: 6px 0 6px 20px;
            position: relative;
            color: #9ca3af;
        }

        .vuln-evidence-list li:before {
            content: "→";
            position: absolute;
            left: 0;
            color: #10b981;
        }

        .vuln-code-block {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(167, 139, 250, 0.2);
            border-radius: 6px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
            color: #e5e7eb;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 400px;
            overflow-y: auto;
        }

        .vuln-code-block mark {
            background: rgba(251, 191, 36, 0.3);
            color: #fbbf24;
            padding: 2px 4px;
            border-radius: 2px;
            font-weight: 600;
        }

        .vuln-metadata {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.8rem;
            color: #6b7280;
            padding: 8px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }

        .vuln-metadata-item {
            display: flex;
            gap: 6px;
        }

        .vuln-metadata-label {
            color: #9ca3af;
        }

        .vuln-metadata-value {
            color: #d1d5db;
            font-weight: 500;
        }
        .subtitle {
            color: #9ca3af;
            font-size: 0.85rem;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(167, 139, 250, 0.2);
        }
        .auth-section {
            margin-bottom: 30px;
            padding: 15px;
            background: rgba(55, 55, 78, 0.4);
            border-radius: 10px;
            border: 1px solid rgba(167, 139, 250, 0.3);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .auth-section label {
            font-size: 0.9rem;
            color: #a78bfa;
        }
        .auth-input {
            background: rgba(55, 55, 78, 0.8);
            border: 2px solid rgba(167, 139, 250, 0.3);
            border-radius: 8px;
            padding: 10px 12px;
            color: #fff;
            font-size: 0.95rem;
            width: 100%;
        }
        .auth-input:focus { outline: none; border-color: #a78bfa; }
	.btn-auth {
    		background: linear-gradient(135deg, #a78bfa, #ec4899);
    		color: #fff;
    		border: none;
    		border-radius: 8px;
    		padding: 10px 24px;
    		margin: 5px auto;
    		font-size: 0.95rem;
    		cursor: pointer;
    		font-weight: 600;
    		display: block;
		}


        .btn-auth:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(167, 139, 250, 0.4); }
        .auth-status {
            font-size: 0.85rem;
            color: #10b981;
            align-self: flex-start;
        }
        .auth-edit {
            font-size: 0.8rem;
            color: #9ca3af;
            cursor: pointer;
            text-decoration: underline;
            margin-left: 8px;
        }
        .auth-edit:hover { color: #a78bfa; }
        .stats {
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid rgba(167, 139, 250, 0.2);
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            font-size: 0.9rem;
        }
        .log-entry.info       { color: #9ca3af; }
.log-entry.success    { color: #10b981; }
.log-entry.error      { color: #ef4444; }
.log-entry.warning    { color: #f59e0b; }
.log-entry.recon      { color: #60a5fa; background: rgba(96, 165, 250, 0.1); }
.log-entry.agent      { color: #a78bfa; background: rgba(167, 139, 250, 0.1); border-left: 3px solid #a78bfa; }
.log-entry.ai         { color: #fbbf24; }
.log-entry.ai-response{ color: #34d399; }
.log-entry.testing    { color: #f59e0b; }
.log-entry.verification { color: #8b5cf6; }
.log-entry.confirmed  { color: #10b981; font-weight: bold; }
.log-entry.rejected   { color: #6b7280; }
.log-entry.system     { color: #a78bfa; font-weight: bold; }
.log-entry.classification { color: #06b6d4; }
.log-entry.payload    { color: #f97316; }
.log-entry.decision   { color: #ec4899; }
.log-timestamp        { color: #6b7280; margin-right: 10px; }
        .stat-label { color: #9ca3af; }
        .stat-value { color: #a78bfa; font-weight: 600; }
        /* === Rest of your styles unchanged === */
        .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .header { padding: 30px 40px; background: rgba(20, 20, 30, 0.5); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(167, 139, 250, 0.3); }
        .header h1 { font-size: 1.5rem; margin-bottom: 10px; }
        .header .tagline { color: #9ca3af; font-size: 0.9rem; margin-bottom: 20px; }
        .target-input-group { display: flex; gap: 15px; max-width: 900px; }
        .target-input { flex: 1; background: rgba(55, 55, 78, 0.8); border: 2px solid rgba(167, 139, 250, 0.3); border-radius: 12px; padding: 15px 20px; color: #fff; font-size: 1.05rem; }
        .target-input:focus { outline: none; border-color: #a78bfa; }
        .btn-scan { background: linear-gradient(135deg, #a78bfa, #ec4899); color: #fff; border: none; border-radius: 12px; padding: 15px 35px; font-size: 1.05rem; cursor: pointer; transition: all 0.3s; font-weight: 600; }
        .btn-scan:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(167, 139, 250, 0.4); }
        .btn-scan:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-stop { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .btn-report { background: linear-gradient(135deg, #10b981, #059669); }
        .progress-section { padding: 20px 40px; background: rgba(20, 20, 30, 0.3); }
        .progress-bar { width: 100%; height: 8px; background: rgba(55, 55, 78, 0.8); border-radius: 10px; overflow: hidden; margin-bottom: 10px; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #a78bfa, #ec4899); transition: width 0.5s ease; width: 0%; }
        .stage-info { display: flex; justify-content: space-between; font-size: 0.9rem; color: #9ca3af; }
        .content-area { flex: 1; display: flex; overflow: hidden; padding: 20px 40px 20px 20px; gap: 0; }
        .panel-wrapper { display: flex; flex-direction: column; height: 100%; background: rgba(20, 20, 30, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(167, 139, 250, 0.3); border-radius: 12px; overflow: hidden; flex: 1; }
        .panel { display: flex; flex-direction: column; height: 100%; }
        .panel h3 { color: #a78bfa; padding: 20px; display: flex; align-items: center; gap: 10px; font-size: 1rem; flex-shrink: 0; border-bottom: 1px solid rgba(167, 139, 250, 0.2); }
        .panel-content { flex: 1; overflow-y: auto; overflow-x: hidden; font-family: 'Courier New', monospace; font-size: 0.85rem; padding: 15px; }
        .resizer { width: 8px; background: rgba(167, 139, 250, 0.2); cursor: col-resize; transition: background 0.2s; flex-shrink: 0; }
        .resizer:hover { background: #a78bfa; }
        .resizer:active { background: #ec4899; }
        .log-entry { padding: 8px; margin-bottom: 5px; border-radius: 4px; animation: slideIn 0.3s ease; word-wrap: break-word; white-space: pre-wrap; }
        @keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
        .log-entry.info { color: #9ca3af; }
        .log-entry.success { color: #10b981; }
        .log-entry.error { color: #ef4444; }
        .log-entry.warning { color: #f59e0b; }
        .log-entry.recon { color: #60a5fa; background: rgba(96, 165, 250, 0.1); }
        .log-entry.agent { color: #a78bfa; background: rgba(167, 139, 250, 0.1); border-left: 3px solid #a78bfa; }
        .log-entry.ai { color: #fbbf24; }
        .log-entry.ai-response { color: #34d399; }
        .log-entry.testing { color: #f59e0b; }
        .log-entry.verification { color: #8b5cf6; }
        .log-entry.confirmed { color: #10b981; font-weight: bold; }
        .log-entry.rejected { color: #6b7280; }
        .log-entry.system { color: #a78bfa; font-weight: bold; }
        .log-entry.classification { color: #06b6d4; }
        .log-entry.payload { color: #f97316; }
        .log-entry.decision { color: #ec4899; }
        .log-timestamp { color: #6b7280; margin-right: 10px; }
        .vuln-item { background: rgba(55, 55, 78, 0.6); border-left: 4px solid; border-radius: 4px; padding: 12px; margin-bottom: 10px; animation: slideIn 0.3s ease; }
        .vuln-item.Critical { border-color: #ef4444; }
        .vuln-item.High { border-color: #f97316; }
        .vuln-item.Medium { border-color: #eab308; }
        .vuln-item.Low { border-color: #3b82f6; }
        .vuln-item.Info { border-color: #6b7280; }
        .vuln-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 600; }
        .vuln-severity { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; background: rgba(255, 255, 255, 0.1); }
        .vuln-url { font-size: 0.8rem; color: #9ca3af; word-break: break-all; margin-bottom: 8px; }
        .vuln-details { font-size: 0.75rem; color: #6b7280; }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.3); border-radius: 4px; }
        ::-webkit-scrollbar-thumb { background: #a78bfa; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #8b5cf6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="logo">Otodus</div>
            <div class="subtitle">author -IMApurbo </div>

            <!-- Updated Auth Token Section -->
            <div class="auth-section" id="authSection">
                <label>Authentication Token</label>

                <div id="authInputGroup">
                    <input type="password" class="auth-input" id="authTokenInput" placeholder="Enter your API token">
                    <button class="btn-auth" id="saveAuthBtn">Save</button>
                </div>

                <div id="authStatus" style="display: none;" class="auth-status">
                    Token saved securely
                    <span class="auth-edit" onclick="editAuthToken()"> (edit)</span>
                </div>
            </div>

            <div class="stats">
                <div class="stat-item">
                    <span class="stat-label">Subdomains</span>
                    <span class="stat-value" id="subdomainCount">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Live Domains</span>
                    <span class="stat-value" id="liveCount">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Endpoints</span>
                    <span class="stat-value" id="endpointCount">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Vulnerabilities</span>
                    <span class="stat-value" id="vulnCount">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Prompts</span>
                    <span class="stat-value" id="promptCount">0</span>
                </div>
            </div>
        </div>
      
        <!-- Rest of the page remains exactly the same -->
        <div class="main-content">
            <div class="header">
                <h1>Otodus- The Megalodon of Automated Pentesting</h1>
                <div class="tagline">Domain → Enum → Crawl → Classify → Exploit → Verify → Report</div>
                <div class="target-input-group">
                    <input type="text" class="target-input" id="domainInput" placeholder="testphp.vulnweb.com">
                    <button class="btn-scan" id="scanBtn" onclick="startScan()">Start Auto Scan</button>
                    <button class="btn-scan btn-stop" id="stopBtn" onclick="stopScan()" style="display: none;">Stop</button>
                    <button class="btn-scan btn-report" id="reportBtn" onclick="generateReport()" style="display: none;">Report</button>
                </div>
            </div>
          
            <div class="progress-section">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressBar"></div>
                </div>
                <div class="stage-info">
                    <span id="currentStage">Ready - Enter domain name</span>
                    <span id="progressPercent">0%</span>
                </div>
            </div>
          
            <div class="content-area">
                <div class="panel-wrapper">
                    <div class="panel">
                        <h3>AI Reasoning</h3>
                        <div class="panel-content" id="reasoningLog"></div>
                    </div>
                </div>
                <div class="resizer" id="resizer1"></div>
                <div class="panel-wrapper">
                    <div class="panel">
                        <h3>System Log</h3>
                        <div class="panel-content" id="consoleLog"></div>
                    </div>
                </div>
                <div class="resizer" id="resizer2"></div>
                <div class="panel-wrapper">
                    <div class="panel">
                        <h3>Vulnerabilities</h3>
                        <div class="panel-content" id="vulnPanel"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

        <script>
        let eventSource = null;

        function escapeHtml(text) {
            if (text === null || text === undefined) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

function addLog(message, type = 'info', panelId = 'consoleLog') {
    const panel = document.getElementById(panelId);
    const entry = document.createElement('div');
    
    // Apply both 'log-entry' base class AND the specific type class
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${escapeHtml(message)}`;
    
    panel.appendChild(entry);
    panel.scrollTop = panel.scrollHeight;
}

        // === AUTH TOKEN HANDLING ===
        async function loadAuthToken() {
            try {
                const response = await fetch('/get_auth_token');
                const data = await response.json();
                if (data.token && data.token.trim() !== '') {
                    document.getElementById('authInputGroup').style.display = 'none';
                    document.getElementById('authStatus').style.display = 'block';
                } else {
                    document.getElementById('authInputGroup').style.display = 'block';
                    document.getElementById('authStatus').style.display = 'none';
                }
            } catch (err) {
                document.getElementById('authInputGroup').style.display = 'block';
                document.getElementById('authStatus').style.display = 'none';
            }
        }

        function editAuthToken() {
            document.getElementById('authTokenInput').value = '';
            document.getElementById('authInputGroup').style.display = 'block';
            document.getElementById('authStatus').style.display = 'none';
        }

        document.getElementById('saveAuthBtn').addEventListener('click', async () => {
            const token = document.getElementById('authTokenInput').value.trim();
            if (!token) {
                addLog('Please enter a valid authentication token', 'error');
                return;
            }
            try {
                const response = await fetch('/save_auth_token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: token })
                });
                const result = await response.json();
                if (result.success) {
                    addLog('Authentication token saved successfully', 'success');
                    document.getElementById('authInputGroup').style.display = 'none';
                    document.getElementById('authStatus').style.display = 'block';
                } else {
                    addLog('Failed to save token: ' + (result.error || 'Unknown'), 'error');
                }
            } catch (err) {
                addLog('Error saving token: ' + err.message, 'error');
            }
        });

        // === VULNERABILITY DISPLAY - FULLY COLLAPSIBLE ===
        function displayVulnerability(vuln) {
            const panel = document.getElementById('vulnPanel');
            const card = document.createElement('div');
            const severity = vuln.severity || 'Medium';
            card.className = `vuln-card ${severity}`;

            const keywords = [...(vuln.highlight_keywords || []), vuln.payload || ''];

            function highlightText(text, keywords) {
                if (!text || keywords.length === 0) return escapeHtml(text || '');
                let html = escapeHtml(text);
                keywords.forEach(kw => {
                    if (kw && kw.trim()) {
                        const regex = new RegExp(escapeHtml(kw.trim()).replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'gi');
                        html = html.replace(regex, '<mark>$1</mark>');
                    }
                });
                return html;
            }

            const evidenceList = vuln.evidence?.length > 0
                ? vuln.evidence.map(e => `<li>${escapeHtml(e)}</li>`).join('')
                : '<li>No specific evidence provided</li>';

            card.innerHTML = `
                <div class="vuln-title" onclick="this.parentNode.classList.toggle('expanded')">
                    <div class="vuln-title-left">
                        <span class="vuln-type-name">${escapeHtml(vuln.type)}</span>
                        <span class="vuln-severity-badge ${severity}">${escapeHtml(severity)}</span>
                        <span class="vuln-method">${escapeHtml(vuln.method)}</span>
                        <span class="vuln-url-preview" title="${escapeHtml(vuln.url)}">${escapeHtml(vuln.url)}</span>
                    </div>
                    <span class="vuln-expand-icon">▶</span>
                </div>
                <div class="vuln-details">
                    <div class="vuln-details-content">
                        <div class="vuln-section">
                            <div class="vuln-section-title">📋 Description & Impact</div>
                            <div class="vuln-section-content">${escapeHtml(vuln.impact || 'No impact description')}</div>
                        </div>
                        <div class="vuln-section">
                            <div class="vuln-section-title">💉 Payload</div>
                            <div class="vuln-code-block">${escapeHtml(vuln.payload || 'N/A')}</div>
                        </div>
                        <div class="vuln-section">
                            <div class="vuln-section-title">🔍 Evidence</div>
                            <ul class="vuln-evidence-list">${evidenceList}</ul>
                        </div>
                        <div class="vuln-section">
                            <div class="vuln-section-title">📤 Raw Request</div>
                            <div class="vuln-code-block">${highlightText(vuln.raw_request || 'Not available', keywords)}</div>
                        </div>
                        <div class="vuln-section">
                            <div class="vuln-section-title">📥 Vulnerable Response</div>
                            <div class="vuln-code-block">${highlightText(vuln.raw_vulnerable_response || 'Not available', keywords)}</div>
                        </div>
                        <div class="vuln-metadata">
                            <div class="vuln-metadata-item"><span class="vuln-metadata-label">CWE:</span><span class="vuln-metadata-value">${escapeHtml(vuln.cwe || 'N/A')}</span></div>
                            <div class="vuln-metadata-item"><span class="vuln-metadata-label">Confidence:</span><span class="vuln-metadata-value">${escapeHtml(vuln.confidence || 'N/A')}</span></div>
                            <div class="vuln-metadata-item"><span class="vuln-metadata-label">Code:</span><span class="vuln-metadata-value">${escapeHtml(vuln.response_code || 'N/A')}</span></div>
                            <div class="vuln-metadata-item"><span class="vuln-metadata-label">Verified:</span><span class="vuln-metadata-value">${vuln.verified_at ? new Date(vuln.verified_at).toLocaleString() : 'N/A'}</span></div>
                        </div>
                    </div>
                </div>
            `;
            panel.appendChild(card);
            panel.scrollTop = panel.scrollHeight;
        }

        // === SCAN CONTROL & SSE ===
        async function startScan() {
            const domain = document.getElementById('domainInput').value.trim();
            if (!domain) {
                addLog('Please enter a domain', 'error');
                return;
            }

            // Clear panels
            document.getElementById('consoleLog').innerHTML = '';
            document.getElementById('reasoningLog').innerHTML = '';
            document.getElementById('vulnPanel').innerHTML = '';

            document.getElementById('scanBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('reportBtn').style.display = 'none';
            document.getElementById('domainInput').disabled = true;

            addLog(`Starting auto scan for ${domain}`, 'info');

            try {
                const response = await fetch('/start_scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ domain: domain })
                });
                const result = await response.json();
                if (!result.success) {
                    addLog(`Error: ${result.error || 'Failed to start'}`, 'error');
                    resetScanUI();
                    return;
                }

                eventSource = new EventSource('/stream');

                eventSource.addEventListener('log', (e) => {
                    const data = JSON.parse(e.data);
                    addLog(data.message, data.type, 'consoleLog');
                });

 eventSource.addEventListener('reasoning', (e) => {
    const data = JSON.parse(e.data);
    addLog(data.message, data.type, 'reasoningLog');  // This will now apply correct color
});

                eventSource.addEventListener('vulnerability', (e) => {
                    const vuln = JSON.parse(e.data);
                    displayVulnerability(vuln);
                    document.getElementById('vulnCount').textContent = parseInt(document.getElementById('vulnCount').textContent) + 1;
                });

                eventSource.addEventListener('state', (e) => {
                    const data = JSON.parse(e.data);
                    document.getElementById('subdomainCount').textContent = data.subdomains || 0;
                    document.getElementById('liveCount').textContent = data.live_domains || 0;
                    document.getElementById('endpointCount').textContent = data.endpoints || 0;
                    document.getElementById('vulnCount').textContent = data.vulnerabilities?.length || 0;

                    document.getElementById('progressBar').style.width = data.progress + '%';
                    document.getElementById('progressPercent').textContent = data.progress + '%';
                    document.getElementById('currentStage').textContent = data.stage;

                    if (data.stage === 'completed' || data.stage === 'error') {
                        scanCompleted();
                    }
                });

            } catch (error) {
                addLog(`Connection error: ${error.message}`, 'error');
                resetScanUI();
            }
        }

        function stopScan() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            fetch('/stop_scan', { method: 'POST' });
            addLog('Scan stopped by user', 'info');
            resetScanUI();
        }

        function scanCompleted() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            addLog('Scan completed!', 'success');
            document.getElementById('stopBtn').style.display = 'none';
            document.getElementById('reportBtn').style.display = 'inline-block';
            document.getElementById('domainInput').disabled = false;
        }

        function resetScanUI() {
            document.getElementById('scanBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
            document.getElementById('reportBtn').style.display = 'none';
            document.getElementById('domainInput').disabled = false;
        }

        async function generateReport() {
            addLog('Generating report...', 'info');
            try {
                const response = await fetch('/generate_report');
                const data = await response.json();
                if (data.success) {
                    const blob = new Blob([data.report], { type: 'text/markdown' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `pentest-report-${Date.now()}.md`;
                    a.click();
                    addLog('Report downloaded', 'success');
                } else {
                    addLog('Report generation failed', 'error');
                }
            } catch (error) {
                addLog('Error generating report: ' + error.message, 'error');
            }
        }

        // === PANEL RESIZING ===
        const resizers = document.querySelectorAll('.resizer');
        let currentResizer = null;
        let prevX = 0;

        resizers.forEach(resizer => {
            resizer.addEventListener('mousedown', e => {
                currentResizer = resizer;
                prevX = e.clientX;
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
                e.preventDefault();
            });
        });

        document.addEventListener('mousemove', e => {
            if (!currentResizer) return;
            const delta = e.clientX - prevX;
            prevX = e.clientX;

            const leftWrapper = currentResizer.previousElementSibling;
            const rightWrapper = currentResizer.nextElementSibling;

            if (leftWrapper && leftWrapper.classList.contains('panel-wrapper')) {
                const newWidth = leftWrapper.offsetWidth + delta;
                if (newWidth > 200) leftWrapper.style.flexBasis = newWidth + 'px';
            }
            if (rightWrapper && rightWrapper.classList.contains('panel-wrapper')) {
                const newWidth = rightWrapper.offsetWidth - delta;
                if (newWidth > 200) rightWrapper.style.flexBasis = newWidth + 'px';
            }
        });

        document.addEventListener('mouseup', () => {
            currentResizer = null;
            document.body.style.cursor = 'default';
            document.body.style.userSelect = 'auto';
        });

        // === INITIALIZATION ===
        fetch('/prompt_count')
            .then(r => r.json())
            .then(data => {
                document.getElementById('promptCount').textContent = data.count;
            });

        // Restore current scan state on load/refresh
// ADD THIS ENTIRE BLOCK - Restore state on page load/refresh
fetch('/current_scan_state')
    .then(r => r.json())
    .then(data => {
        // Restore logs
        data.logs.forEach(item => {
            addLog(item.message, item.type, 'consoleLog');
        });
        
        // Restore reasoning
        data.reasonings.forEach(item => {
            addLog(item.message, item.type, 'reasoningLog');
        });
        
        // Restore vulnerabilities
        data.vulnerabilities.forEach(vuln => {
            displayVulnerability(vuln);
        });
        
        // Restore stats
        const s = data.state;
        document.getElementById('subdomainCount').textContent = s.subdomains || 0;
        document.getElementById('liveCount').textContent = s.live_domains || 0;
        document.getElementById('endpointCount').textContent = s.endpoints || 0;
        document.getElementById('vulnCount').textContent = s.vulnerabilities?.length || 0;
        document.getElementById('progressBar').style.width = s.progress + '%';
        document.getElementById('progressPercent').textContent = s.progress + '%';
        document.getElementById('currentStage').textContent = s.stage || 'Ready';
        
        // If scan is running, reconnect SSE
        if (s.stage && s.stage !== 'idle' && s.stage !== 'completed' && s.stage !== 'error') {
            addLog('Reconnecting to ongoing scan...', 'info');
            eventSource = new EventSource('/stream');
            // Re-attach event listeners (copy from startScan function)
            eventSource.addEventListener('log', (e) => {
                const d = JSON.parse(e.data);
                addLog(d.message, d.type, 'consoleLog');
            });
            eventSource.addEventListener('reasoning', (e) => {
                const d = JSON.parse(e.data);
                addLog(d.message, d.type, 'reasoningLog');
            });
            eventSource.addEventListener('vulnerability', (e) => {
                const vuln = JSON.parse(e.data);
                displayVulnerability(vuln);
            });
            eventSource.addEventListener('state', (e) => {
                const d = JSON.parse(e.data);
                document.getElementById('subdomainCount').textContent = d.subdomains || 0;
                document.getElementById('liveCount').textContent = d.live_domains || 0;
                document.getElementById('endpointCount').textContent = d.endpoints || 0;
                document.getElementById('vulnCount').textContent = d.vulnerabilities?.length || 0;
                document.getElementById('progressBar').style.width = d.progress + '%';
                document.getElementById('progressPercent').textContent = d.progress + '%';
                document.getElementById('currentStage').textContent = d.stage;
                if (d.stage === 'completed' || d.stage === 'error') {
                    scanCompleted();
                }
            });
            
            // Show stop button if running
            document.getElementById('scanBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            document.getElementById('domainInput').disabled = true;
        }
    })
    .catch(err => console.error("Failed to restore scan state:", err));

// Existing lines below
addLog('Otodus Scanner Ready', 'success');
addLog('Enter domain and click Start Auto Scan', 'info');
        loadAuthToken();
    </script>
</body>
</html>"""

# ============================================================================
# FLASK ROUTES
# ============================================================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_scan', methods=['POST'])
def start_scan():
    try:
        if prompt_loader is None:
            return jsonify({"success": False, "error": "Prompt loader not initialized"}), 500
       
        data = request.json
        domain = data.get('domain', '').strip()
       
        if not domain:
            return jsonify({"success": False, "error": "Domain required"}), 400
       
        memory.__init__()
        memory.target = domain
       
        for q in [log_queue, vuln_queue, reasoning_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except:
                    break
                all_logs.clear()
        all_reasoning.clear()
        all_vulnerabilities.clear()
       
        with state_lock:
            state["progress"] = 0
            state["stage"] = "Starting"
            state["is_running"] = True
       
        orchestrator = AgentOrchestrator(memory, prompt_loader)
        thread = threading.Thread(target=orchestrator.run, args=(domain,))
        thread.daemon = True
        thread.start()
       
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    with state_lock:
        state["is_running"] = False
    reasoning_log("🛑 Scan stopped by user", "system")
    return jsonify({"success": True})

@app.route('/current_scan_state')
def current_scan_state():
    """Return all stored data for page refresh recovery"""
    return jsonify({
        "logs": all_logs,
        "reasonings": all_reasoning,
        "vulnerabilities": all_vulnerabilities,
        "state": get_state_copy()
    })

@app.route('/stream')
def stream():
    def generate():
        while True:
            try:
                while not log_queue.empty():
                    try:
                        log_data = log_queue.get_nowait()
                        yield f"event: log\ndata: {json.dumps(log_data)}\n\n"
                    except queue.Empty:
                        break
               
                while not reasoning_queue.empty():
                    try:
                        reasoning_data = reasoning_queue.get_nowait()
                        yield f"event: reasoning\ndata: {json.dumps(reasoning_data)}\n\n"
                    except queue.Empty:
                        break
               
                while not vuln_queue.empty():
                    try:
                        vuln_data = vuln_queue.get_nowait()
                        yield f"event: vulnerability\ndata: {json.dumps(vuln_data)}\n\n"
                    except queue.Empty:
                        break
               
                state_data = get_state_copy()
                yield f"event: state\ndata: {json.dumps(state_data)}\n\n"
               
                time.sleep(0.3)
            except GeneratorExit:
                break
            except Exception as e:
                print(f"Stream error: {e}")
                break
   
    return Response(generate(), mimetype='text/event-stream')

@app.route('/generate_report')
def generate_report():
    report = f"""# Otodus Report - Auto Scan
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Target Domain:** {memory.target}
**Selected Target:** {memory.selected_target}
**Framework:** Otodus
## Executive Summary
- **Subdomains Found:** {len(memory.subdomains)}
- **Live Domains:** {len(memory.live_domains)}
- **Endpoints Analyzed:** {len(memory.endpoints)}
- **Vulnerabilities Found:** {len(memory.vulnerabilities)}
- **Critical/High:** {sum(1 for v in memory.vulnerabilities if v.get('severity') in ['Critical', 'High'])}
## Methodology
1. **Domain Validation** - DNS resolution and reachability checks
2. **Subdomain Enumeration** - subfinder + gobuster
3. **Live Filtering** - httpx-toolkit
4. **Target Selection** - HTTP/HTTPS reachability test
5. **Crawling** - CrawlerX endpoint discovery
6. **Deduplication** - Unique endpoints by signature
7. **AI Classification** - Endpoint vulnerability type classification
8. **Exploitation** - AI-generated payload testing
9. **Verification** - AI-verified true positives
10. **Reporting** - This report
## Recon Results
### Subdomains Discovered
"""
   
    if memory.subdomains:
        for sub in memory.subdomains[:50]:
            report += f"- {sub}\n"
    else:
        report += "*No subdomains found*\n"
   
    report += f"""
### Live Domains
"""
    if memory.live_domains:
        for live in memory.live_domains[:30]:
            report += f"- {live}\n"
    else:
        report += "*No live domains filtered*\n"
   
    report += f"""
## Confirmed Vulnerabilities
"""
   
    if memory.vulnerabilities:
        for idx, vuln in enumerate(memory.vulnerabilities, 1):
            report += f"""
### {idx}. {vuln.get('type', 'Unknown')} [{vuln.get('severity', 'Unknown')}]
- **URL:** {vuln.get('url', 'N/A')}
- **Method:** {vuln.get('method', 'GET')}
- **CWE:** {vuln.get('cwe', 'N/A')}
- **Confidence:** {vuln.get('confidence', 'N/A')}
**Payload:**
```
{vuln.get('payload', 'N/A')}
```
**Impact:** {vuln.get('impact', 'Not specified')}
**Evidence:**
{chr(10).join(f"- {e}" for e in vuln.get('evidence', [])) if vuln.get('evidence') else '- No evidence'}
**Response Code:** {vuln.get('response_code', 'N/A')}
**Verified:** {vuln.get('verified_at', 'N/A')}
---
"""
    else:
        report += "\n*No vulnerabilities confirmed during this analysis.*\n\n"
   
    report += f"""
## Testing Coverage
- **Endpoints Tested:** {len(memory.tested_payloads)}
- **Total Payloads:** {sum(len(p) for p in memory.tested_payloads.values())}
## Recommendations
### Immediate Actions
- Review and remediate all Critical/High severity findings
- Implement input validation and output encoding
- Deploy Web Application Firewall (WAF)
### Long-term Strategy
- Integrate security testing in CI/CD
- Regular penetration testing
- Security training for developers
- Implement secure SDLC
---
*Report generated by Otodus*
*AI Model: GPT-4o-mini via Puter AI*
*Tools: subfinder, gobuster, httpx, CrawlerX*
"""
   
    return jsonify({"success": True, "report": report})

@app.route('/prompt_count')
def prompt_count():
    if prompt_loader is None:
        return jsonify({"count": 0})
    return jsonify({"count": len(prompt_loader.get_all_types())})

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    """Main entry point for Otodus – starts the web server with startup checks"""
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')

    print("=" * 70)
    print("🤖 Otodus - The Megalodon of Automated Pentesting")
    print("=" * 70)
    print("\nInitializing system...\n")

    # Create workspace
    setup_workspace()
    print(f"✓ Workspace created: {WORKSPACE.absolute()}")

    # Load prompts
    global prompt_loader
    prompt_loader = PromptLoader(PROMPTS_DIR)
    prompt_count = len(prompt_loader.get_all_types())
    print(f"✓ Prompts loaded: {prompt_count}")

    if prompt_count == 0:
        print("⚠️  Warning: No prompts found in './prompts/' directory!")
        print("   Create .txt files with vulnerability-specific prompts to enable AI testing.\n")

    # Check external tools
    print("🔍 Checking dependent tools...\n")
    tools = {
        "subfinder": check_tool_installed("subfinder"),
        "gobuster": check_tool_installed("gobuster"),
        "httpx": check_tool_installed("httpx"),
        "crawlerx": shutil.which("crawlerx") is not None,
    }

    for tool, available in tools.items():
        status = "✓" if available else "✗"
        print(f"  {status} {tool}")

    if not all(tools.values()):
        print("\n⚠️  Some tools are missing (optional but recommended for full features):")
        if not tools["subfinder"]:
            print("   • subfinder → go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
        if not tools["gobuster"]:
            print("   • gobuster   → sudo apt install gobuster   (or: brew install gobuster)")
        if not tools["httpx"]:
            print("   • httpx      → go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
        if not tools["crawlerx"]:
            print("   • crawlerx   → pip install crawlerx")
        print()

    print("=" * 70)
    print("🚀 Starting Otodus web dashboard...")
    print("=" * 70)
    print(f"\n📍 Dashboard: http://localhost:5000")
    print("📝 Example target: testphp.vulnweb.com")
    print("🔄 Workflow: Recon → Crawl → AI Classify → Exploit → Verify → Report")
    print("🧠 AI Agents: Planner • Classifier • Exploit • Verifier")
    print("⚠️  IMPORTANT: Only scan targets you have explicit permission to test!\n")
    print("💡 Tip: Press Ctrl+C to stop the server\n")

    # Start Flask app
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Otodus shut down gracefully. See you next hunt!")
    except Exception as e:
        print(f"\n❌ Unexpected error during startup: {e}")
        raise


# ============================================================================
# Script entry point
# ============================================================================
if __name__ == "__main__":
    main()
