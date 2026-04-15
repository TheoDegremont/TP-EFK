#!/usr/bin/env python3
import os
import sys
import json
import random
import time
import threading
from datetime import datetime, timedelta
from faker import Faker
import uuid
import signal

fake = Faker()


class LogGenerator:
    def __init__(self, log_type, log_file, rate_per_second):
        self.log_type = log_type
        self.log_file = log_file
        self.rate_per_second = rate_per_second
        self.running = True
        self.total_logs = 0

        # Statistiques
        self.error_rate = 0.05  # 5% d'erreurs
        self.warning_rate = 0.15  # 15% de warnings

        # Listes pour variation
        self.services = [
            "auth-service",
            "payment-service",
            "user-service",
            "inventory-service",
            "notification-service",
            "api-gateway",
        ]
        self.endpoints = [
            "/api/users",
            "/api/products",
            "/api/orders",
            "/api/auth/login",
            "/api/payments",
            "/api/search",
        ]
        self.methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
            "curl/7.68.0",
            "PostmanRuntime/7.28.4",
        ]

    def generate_application_log(self):
        """Génère un log d'application au format JSON"""
        level_rand = random.random()
        if level_rand < self.error_rate:
            level = random.choice(["ERROR", "CRITICAL", "FATAL"])
        elif level_rand < self.error_rate + self.warning_rate:
            level = "WARN"
        else:
            level = random.choice(["INFO", "DEBUG"])

        # Génération du message selon le niveau
        if level in ["ERROR", "CRITICAL", "FATAL"]:
            messages = [
                f"Database connection failed: {fake.sentence()}",
                f"Failed to process payment: {fake.credit_card_number()}",
                f"Service timeout after 30s: {random.choice(self.services)}",
                f"NullPointerException at line {random.randint(100, 500)}",
                f"Authentication failed for user: {fake.user_name()}",
                f"Out of memory error: heap size {random.randint(80, 99)}%",
            ]
            message = random.choice(messages)
            stack_trace = (
                self.generate_stack_trace() if level in ["ERROR", "CRITICAL"] else None
            )
        elif level == "WARN":
            messages = [
                f"High latency detected: {random.randint(1000, 5000)}ms",
                f"Cache miss rate above threshold: {random.randint(60, 90)}%",
                f"Deprecated API called: {random.choice(self.endpoints)}",
                f"Connection pool exhausted: {random.randint(90, 100)}% used",
                f"Slow query detected: {random.randint(2000, 10000)}ms",
            ]
            message = random.choice(messages)
            stack_trace = None
        else:
            messages = [
                f"Processing request for user: {fake.user_name()}",
                f"Successfully processed order: {fake.uuid4()}",
                f"Cache hit for key: {fake.word()}_{random.randint(1, 1000)}",
                f"Health check passed for {random.choice(self.services)}",
                f"Request completed in {random.randint(10, 500)}ms",
            ]
            message = random.choice(messages)
            stack_trace = None

        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": level,
            "service": random.choice(self.services),
            "message": message,
            "correlation_id": str(uuid.uuid4()),
            "user_id": fake.uuid4() if random.random() > 0.3 else None,
            "request_id": fake.uuid4(),
            "duration_ms": random.randint(10, 5000),
            "metadata": {
                "host": fake.hostname(),
                "environment": random.choice(["production", "staging"]),
                "version": f"{random.randint(1, 3)}.{random.randint(0, 10)}.{random.randint(0, 20)}",
                "region": random.choice(["us-east-1", "eu-west-1", "ap-southeast-1"]),
            },
        }
        if stack_trace:
            log_entry["stack_trace"] = stack_trace

        return json.dumps(log_entry)

    def generate_nginx_log(self):
        """Génère un log Nginx au format access log"""
        # Déterminer le status code
        status_rand = random.random()
        if status_rand < self.error_rate:
            status = random.choice([500, 502, 503, 504])
        elif status_rand < self.error_rate + 0.02:  # 2% de 404
            status = 404
        elif status_rand < self.error_rate + 0.05:  # 3% de redirections
            status = random.choice([301, 302, 304])
        else:
            status = 200

        # Génération de l'IP (avec possibilité de bot/crawler)
        if random.random() < 0.1:  # 10% de bots
            ip = random.choice(
                ["66.249.79.118", "40.77.167.129", "157.55.39.123"]
            )  # Googlebot, Bingbot
            user_agent = random.choice(["Googlebot/2.1", "bingbot/2.0", "YandexBot/3.0"])
        else:
            ip = fake.ipv4()
            user_agent = random.choice(self.user_agents)

        # Calcul des temps de réponse
        if status >= 500:
            request_time = round(random.uniform(5.0, 30.0), 3)
        elif status == 404:
            request_time = round(random.uniform(0.001, 0.1), 3)
        else:
            request_time = round(random.uniform(0.01, 2.0), 3)

        # Taille de la réponse
        if status == 304:
            body_bytes = 0
        elif status >= 400:
            body_bytes = random.randint(100, 500)
        else:
            body_bytes = random.randint(200, 50000)

        # Construction du log
        timestamp = datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")
        method = random.choice(self.methods)
        path = random.choice(self.endpoints) + (
            f"?id={random.randint(1, 10000)}" if random.random() > 0.7 else ""
        )
        referer = fake.url() if random.random() > 0.3 else "-"

        log_line = (
            f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {body_bytes} '
            f'"{referer}" "{user_agent}" {request_time}'
        )
        return log_line

    def generate_system_log(self):
        """Génère un log système au format syslog"""
        facilities = ["kern", "user", "mail", "daemon", "auth", "syslog", "cron"]
        severities = ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]
        processes = ["systemd", "kernel", "sshd", "cron", "nginx", "docker", "kubelet"]

        # Pondération des sévérités
        severity_weights = [0.001, 0.002, 0.005, 0.05, 0.15, 0.3, 0.4, 0.092]
        severity = random.choices(severities, weights=severity_weights)[0]
        process = random.choice(processes)
        pid = random.randint(1, 65535)

        # Messages selon le processus
        if process == "kernel":
            messages = [
                f"Out of memory: Kill process {random.randint(1000, 30000)}",
                f"CPU{random.randint(0, 7)}: Core temperature above threshold",
                "EXT4-fs error: unable to read superblock",
                f"Memory pressure level: {random.choice(['low', 'medium', 'critical'])}",
                f"Network interface eth0: link up, speed {random.choice([100, 1000, 10000])} Mbps",
            ]
        elif process == "sshd":
            messages = [
                f"Accepted publickey for {fake.user_name()} from {fake.ipv4()}",
                f"Failed password for invalid user {fake.user_name()} from {fake.ipv4()}",
                f"Connection closed by {fake.ipv4()} port {random.randint(10000, 65535)}",
                "Server listening on 0.0.0.0 port 22",
            ]
        elif process == "docker":
            container_id = fake.sha256()[:12]
            messages = [
                f"Container {container_id} started",
                f"Container {container_id} stopped",
                f"Health check failed for container {container_id}",
                f"Pulling image {fake.word()}:latest",
            ]
        else:
            messages = [
                "Service started successfully",
                "Configuration reloaded",
                "Scheduled task completed",
                f"Connection established to {fake.ipv4()}",
            ]

        message = random.choice(messages)
        hostname = fake.hostname()
        timestamp = datetime.utcnow().strftime("%b %d %H:%M:%S")

        # Format syslog
        log_line = f"{timestamp} {hostname} {process}[{pid}]: {message}"
        return log_line

    def generate_stack_trace(self):
        """Génère une stack trace réaliste"""
        frameworks = ["java", "python", "nodejs"]
        framework = random.choice(frameworks)

        if framework == "java":
            trace = f"""java.lang.NullPointerException
at com.example.service.{fake.word().capitalize()}Service.process({fake.word().capitalize()}.java:{random.randint(50, 250)})
at com.example.controller.{fake.word().capitalize()}Controller.handle({fake.word().capitalize()}.java:{random.randint(20, 120)})
at org.springframework.web.servlet.DispatcherServlet.doDispatch(DispatcherServlet.java:{random.randint(900, 1100)})
at javax.servlet.http.HttpServlet.service(HttpServlet.java:{random.randint(600, 800)})"""
        elif framework == "python":
            trace = f"""Traceback (most recent call last):
  File "/app/{fake.word()}.py", line {random.randint(100, 500)}, in {fake.word()}
    result = process_{fake.word()}(data)
  File "/app/services/{fake.word()}.py", line {random.randint(50, 150)}, in process_{fake.word()}
    return data['{fake.word()}']
KeyError: '{fake.word()}'"""
        else:
            trace = f"""Error: Cannot read property '{fake.word()}' of undefined
at {fake.word()}.js:{random.randint(50, 200)}:{random.randint(10, 50)}
at processTicksAndRejections (internal/process/task_queues.js:{random.randint(80, 100)}:{random.randint(5, 20)})
at async /{fake.word()}/routes/{fake.word()}.js:{random.randint(30, 80)}:{random.randint(5, 30)}"""

        return trace

    def write_logs(self):
        """Thread pour écrire les logs"""
        with open(self.log_file, "a") as f:
            while self.running:
                try:
                    # Génération du log selon le type
                    if self.log_type == "application":
                        log_line = self.generate_application_log()
                    elif self.log_type == "nginx":
                        log_line = self.generate_nginx_log()
                    elif self.log_type == "system":
                        log_line = self.generate_system_log()
                    else:
                        log_line = self.generate_application_log()

                    f.write(log_line + "\n")
                    f.flush()
                    self.total_logs += 1

                    # Affichage périodique des stats
                    if self.total_logs % 1000 == 0:
                        print(f"[{self.log_type}] Generated {self.total_logs} logs", flush=True)

                    # Attente pour respecter le rate
                    time.sleep(1.0 / self.rate_per_second)

                except Exception as e:
                    print(f"Error generating log: {e}", flush=True)
                    time.sleep(1)

    def run(self):
        """Lance la génération de logs"""
        print(
            f"Starting {self.log_type} log generator at {self.rate_per_second} logs/sec to {self.log_file}",
            flush=True,
        )

        # Création de plusieurs threads pour augmenter le débit
        num_threads = min(10, max(1, self.rate_per_second // 100))
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self.write_logs, daemon=True)
            t.start()
            threads.append(t)

        # Attendre les threads
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print(f"\nStopping... Generated {self.total_logs} logs total", flush=True)


def signal_handler(signum, frame):
    sys.exit(0)


if __name__ == "__main__":
    # Configuration depuis les variables d'environnement
    log_type = os.getenv("LOG_TYPE", "application")
    log_file = os.getenv("LOG_FILE", "/logs/output.log")
    rate = int(os.getenv("LOG_RATE", "100"))

    # Gestion du signal d'arrêt
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Lancement du générateur
    generator = LogGenerator(log_type, log_file, rate)
    generator.run()
