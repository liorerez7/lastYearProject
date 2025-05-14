import random
import time
import statistics
from statistics import quantiles
import gevent
from collections import defaultdict
from sqlalchemy import text
from locust import User, task, between
from locust.env import Environment
from prometheus_client import start_http_server, Gauge, Counter

from main.core.test_framework.base_test import BaseTest


class ExecutionPlanTest(BaseTest):
    """
    • build()  – unchanged
    • run()   – unchanged signature but now warms‑up and supports longer runs
    • _run_with_locust() – adds warm‑up call
    • get_built_plan_with_durations() – returns avg / p95 / stddev, dropping first sample
    """
    # Prometheus Metrics
    SQL_QUERY_DURATION = Gauge('sql_query_duration_seconds', 'Time taken to execute a SQL query', ['query'])
    SQL_QUERY_ERROR_COUNT = Counter('sql_query_error_count_total', 'Number of SQL query errors', ['query'])

    # Start Prometheus HTTP server
    start_http_server(8000)

    def __init__(self, execution_plan, db_type, schema, test_name: str = "unknown"):
        super().__init__()
        self.plan = execution_plan
        self.db_type = db_type.upper()
        self.schema = schema
        self.test_name = test_name

        self._dur, self._sels, self._sqls = defaultdict(list), {}, {}
        self.built_plan: dict[int, dict] = {}
        self._sql_to_label: dict[str, str] = {}

    def build(self, engine, metadata):
        self.built_plan = {}
        for idx, step in enumerate(self.plan, 1):
            gen = step["generator"]
            repeat = step["repeat"]
            selector = step.get("selector")
            qtype = type(gen).__name__.replace("QueryStrategy", "").lower()
            sql = gen.generate_query(metadata, self.db_type.lower(), selector)

            label = f"Step {idx}"
            self.built_plan[idx] = {
                "query": sql,
                "query_type": qtype,
                "repeat": repeat,
                "selector": selector,
            }
            self._sql_to_label[sql] = label
        return self.built_plan

    def _warm_up(self, engine, rounds: int = 2):
        """Run each unique SQL a few times to prime caches before measurement."""
        unique_sql = {step["query"] for step in self.built_plan.values()}
        for _ in range(rounds):
            for sql in unique_sql:
                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                except Exception:
                    pass  # ignore warm‑up errors – they will surface in real run

    def run(self, engine, metadata, locust_config: dict | None = None):
        if not self.built_plan:
            raise RuntimeError("build() must run first")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─" * 60)

        # warm‑up before every run
        self._warm_up(engine)

        if locust_config:
            self._run_with_locust(engine, locust_config)
        else:
            self._run_without_locust(engine)

    def _run_without_locust(self, engine):
        for idx, step in self.built_plan.items():
            sql, label = step["query"], f"Step {idx}"
            self._sqls[label] = sql
            self._sels[label] = step.get("selector")

            for _ in range(step["repeat"]):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                duration = time.perf_counter() - t0
                self._dur[label].append(duration)

                # Record query execution time in Prometheus for this specific query
                ExecutionPlanTest.SQL_QUERY_DURATION.labels(query=sql).set(duration)

    def _run_with_locust(self, engine, cfg: dict):
        # 1. flat list of queries (respecting repeat)
        flat_queries = [step["query"] for step in self.built_plan.values() for _ in range(step["repeat"])]

        parent = self

        class DatabaseUser(User):
            wait_time = between(cfg["wait_time_min"], cfg["wait_time_max"])

            @task
            def random_query(self):
                sql = random.choice(flat_queries)
                t0 = time.perf_counter()

                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                except Exception as e:
                    print("❌", e)
                    ExecutionPlanTest.SQL_QUERY_ERROR_COUNT.labels(
                        query=sql).inc()  # Increment error count for Prometheus

                duration = time.perf_counter() - t0
                label = parent._sql_to_label[sql]
                parent._sqls[label] = sql
                parent._sels[label] = parent.built_plan[int(label.split()[1])]["selector"]
                parent._dur[label].append(duration)

                # Record query execution time in Prometheus for this specific query
                ExecutionPlanTest.SQL_QUERY_DURATION.labels(query=sql).set(duration)

        env = Environment(user_classes=[DatabaseUser])
        env.create_local_runner()
        env.runner.start(cfg["users"], spawn_rate=cfg["spawn_rate"])

        # auto‑stop
        gevent.spawn_later(cfg["run_time"], lambda: env.runner.quit())
        env.runner.greenlet.join()
        print(f"Locust run finished after {cfg['run_time']} s")

    def get_built_plan_with_durations(self):
        results = {}
        for idx, step in self.built_plan.items():
            label = f"Step {idx}"
            durs = self._dur.get(label, [])
            # drop first measurement (already warmed‑up, but extra safety)
            if durs:
                durs = durs[1:]

            if durs:
                avg = statistics.mean(durs)
                p95 = quantiles(durs, n=20)[-1]  # 95th percentile
                std = statistics.stdev(durs) if len(durs) > 1 else 0.0
            else:
                avg = p95 = std = 0.0

            results[idx] = {
                **step,
                "durations": [round(d, 6) for d in durs],
                "avg": round(avg, 6),
                "p95": round(p95, 6),
                "stddev": round(std, 6),
            }
        return results
