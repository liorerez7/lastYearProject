import random
import time
import statistics
from statistics import quantiles  # NEW: for P95 calculation
import gevent
from collections import defaultdict
from sqlalchemy import text
from locust import User, task, between
from locust.env import Environment
from main.core.test_framework.base_test import BaseTest


TIMEOUT_MS = 30_000  # 30 seconds
TIMEOUT_SQL = {
    "MYSQL": lambda ms: f"SET SESSION max_execution_time = {ms}",
    "POSTGRES": lambda ms: f"SET statement_timeout = {ms}"
}

class ExecutionPlanTest(BaseTest):


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
        unique_sql = {step["query"] for step in self.built_plan.values()}
        for _ in range(rounds):
            for sql in unique_sql:
                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                except Exception:
                    pass

    def run(self, engine, metadata, locust_config: dict | None = None):
        if not self.built_plan:
            raise RuntimeError("build() must run first")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─" * 60)

        self._warm_up(engine)

        if locust_config:
            self._run_with_locust(engine, locust_config)
        else:
            self._run_without_locust(engine)

        # NEW: Dispose engine after test to clean up connections
        engine.dispose()

    def _run_without_locust(self, engine):
        timeout_stmt = TIMEOUT_SQL[self.db_type](TIMEOUT_MS)
        for idx, step in self.built_plan.items():
            sql, label = step["query"], f"Step {idx}"
            self._sqls[label] = sql
            self._sels[label] = step.get("selector")

            for _ in range(step["repeat"]):
                t0 = time.perf_counter()
                try:
                    with engine.connect() as conn:
                        conn.execute(text(timeout_stmt))
                        conn.execute(text(sql))
                    self._dur[label].append(time.perf_counter() - t0)
                except Exception as e:
                    self._dur[label].append(30.0)
                    print("⏱️ 30-sec limit hit:", e)

    def _run_with_locust(self, engine, cfg: dict):
        flat_queries = [step["query"] for step in self.built_plan.values() for _ in range(step["repeat"])]
        timeout_stmt = TIMEOUT_SQL[self.db_type](TIMEOUT_MS)
        parent = self

        class DatabaseUser(User):
            wait_time = between(cfg["wait_time_min"], cfg["wait_time_max"])

            @task
            def random_query(self):
                sql = random.choice(flat_queries)
                t0 = time.perf_counter()
                try:
                    with engine.connect() as conn:
                        conn.execute(text(timeout_stmt))
                        conn.execute(text(sql))
                    duration = time.perf_counter() - t0
                except Exception as e:
                    duration = 30.0
                    print("⏱️ 30-sec limit hit:", e)

                label = parent._sql_to_label[sql]
                parent._sqls[label] = sql
                parent._sels[label] = parent.built_plan[int(label.split()[1])]["selector"]
                parent._dur[label].append(duration)

        env = Environment(user_classes=[DatabaseUser])
        env.create_local_runner()
        env.runner.start(cfg["users"], spawn_rate=cfg["spawn_rate"])

        gevent.spawn_later(cfg["run_time"], lambda: env.runner.quit())
        env.runner.greenlet.join()
        print(f"Locust run finished after {cfg['run_time']} s")

    def get_built_plan_with_durations(self):
        results = {}
        for idx, step in self.built_plan.items():
            label = f"Step {idx}"
            durs = self._dur.get(label, [])
            if durs:
                durs = durs[1:]

            if durs:
                avg = statistics.mean(durs)
                p95 = quantiles(durs, n=20)[-1]
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