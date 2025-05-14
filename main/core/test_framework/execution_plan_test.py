import random
import statistics
import time
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import text

from main.core.test_framework.base_test import BaseTest
from main.core.schema_analysis.table_profiler import get_rowcounts
from locust import User, task, between
from locust.env import Environment

from locust import events


class ExecutionPlanTest(BaseTest):
    queries = []

    def __init__(self, execution_plan: list, db_type: str, schema: str, test_name: str = "unknown"):
        super().__init__()
        self.plan = execution_plan  # תכנית הבדיקה (raw)
        self.db_type = db_type.upper()
        self.schema = schema
        self.test_name = test_name  # שם הבדיקה (לוגי)
        self._dur = defaultdict(list)  # label → רשימת זמני הריצה
        self._sels = {}  # label → selector
        self._sqls = {}  # label → השאילתה המקורית
        self.built_plan = {}  # נבנה בפונקציית build

    def build(self, engine, metadata) -> dict[int, dict]:
        """
        בונה תכנית בדיקה בפורמט שטוח:
        {
            1: {"query": "...", "query_type": "...", "repeat": N},
            2: {...},
            ...
        }
        """
        self.built_plan = {}

        for idx, step in enumerate(self.plan, 1):
            generator = step["generator"]
            repeat = step["repeat"]
            selector = step.get("selector")
            query_type = type(generator).__name__.replace("QueryStrategy", "").lower()
            sql = generator.generate_query(metadata, self.db_type.lower(), selector=selector)

            self.built_plan[idx] = {
                "query": sql,
                "query_type": query_type,
                "repeat": repeat,
                "selector": selector
            }
            self.queries.append(sql)  # Add the query to the shared list
        return self.built_plan

    def run(self, engine, metadata, locust_config=None):
        """
        Run the benchmark according to the built plan.
        """
        if not self.built_plan:
            raise RuntimeError("You must call build() before run().")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─" * 60)

        # If locust_config is provided, run with Locust
        if locust_config:
            self.run_with_locust(engine, metadata, locust_config)
        else:
            self.run_without_locust(engine, metadata)

    def run_without_locust(self, engine, metadata):
        """
        Run the benchmark normally without Locust simulation.
        """
        for idx, step in self.built_plan.items():
            sql = step["query"]
            label = f"Step {idx}"
            repeat = step["repeat"]
            selector = step.get("selector")

            self._sqls[label] = sql
            self._sels[label] = selector

            for _ in range(repeat):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                self._dur[label].append(time.perf_counter() - t0)

    def run_with_locust(self, engine, metadata, locust_config):
        """
        Run the benchmark with Locust simulated users.
        """

        class DatabaseUser(User):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.queries = None

            def on_start(self):
                # Initialize the queries list from the BenchmarkTest instance
                self.queries = ExecutionPlanTest.queries  # Access the queries from BenchmarkTest

            @task
            def perform_random_query(self):
                # Pick a random query and execute it
                query = random.choice(self.queries)
                t0 = time.perf_counter()
                try:
                    with engine.connect() as conn:
                        conn.execute(text(query))  # ✅ wrap the raw SQL
                except Exception as e:
                    print(f"❌ Query failed: {e}")

                query_duration = time.perf_counter() - t0
                print(f"Executed query: {query} in {query_duration:.4f} seconds.")

        # Now run Locust with the configured number of users and hatch rate

        environment = Environment(user_classes=[DatabaseUser])

        # Define the number of users and hatch rate (simultaneous users)
        environment.create_local_runner()
        environment.runner.start(locust_config["num_users"], locust_config["hatch_rate"])
        environment.runner.greenlet.join()

        # To stop Locust after the test run
        events.quitting.fire()

        print(f"Locust simulation completed for {locust_config['num_users']} users.")

    def get_built_plan_with_durations(self) -> dict[int, dict]:
        result = {}
        for idx, step in self.built_plan.items():
            label = f"Step {idx}"
            durations = [Decimal(f"{d:.8f}") for d in self._dur.get(label, [])]
            stddev = Decimal(f"{statistics.stdev(durations):.8f}") if len(durations) > 1 else Decimal("0.0")

            result[idx] = {
                **step,
                "durations": durations,
                "stddev": stddev
            }
        return result

    def print_summary(self, metadata):
        """
        מדפיסה את סיכום תוצאות הבדיקה לפי הנתונים השמורים בלבד
        """
        print(f"\n📊 Summary for {self.db_type}")
        print("─" * 52)

        total_q, total_t = 0, 0.0
        table_keys = sorted(metadata.tables.keys())

        for label, samples in self._dur.items():
            n = len(samples)
            avg = statistics.mean(samples)
            sd = statistics.stdev(samples) if n > 1 else 0.0
            sel = self._sels[label]
            sql = self._sqls[label]
            tbl = table_keys[sel % len(table_keys)].split(".")[-1] if sel is not None else "?"

            print(f"{label:<32} runs={n:>3}   avg={avg:.4f}s ±{sd:.4f}s   table={tbl}")
            print(f"  SQL: {sql}")

            total_q += n
            total_t += sum(samples)

        print("─" * 52)
        print(f"TOTAL: {total_q} queries   overall avg={total_t / total_q:.4f}s\n")
