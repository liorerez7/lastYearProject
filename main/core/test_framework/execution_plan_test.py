import random
import statistics
import time
from collections import defaultdict
from decimal import Decimal

import gevent                                   # תוספת
from locust import User, task, between, events
from locust.env import Environment
from sqlalchemy import text

from main.core.test_framework.base_test import BaseTest


class ExecutionPlanTest(BaseTest):
    """
    מריץ תכנית ביצועים על־פי steps שנבנים ע״י build().
    תומך בשני מצבים:
      • run_without_locust  – ריצה סינכרונית (repeat קבוע לכל שלב)
      • run_with_locust     – הדמיית משתמשים מקבילים עם Locust
    """

    def __init__(self, execution_plan: list, db_type: str, schema: str,
                 test_name: str = "unknown"):
        super().__init__()
        self.plan        = execution_plan
        self.db_type     = db_type.upper()
        self.schema      = schema
        self.test_name   = test_name

        self._dur        = defaultdict(list)     # label → זמני ריצה
        self._sels       = {}                    # label → selector
        self._sqls       = {}                    # label → sql
        self.built_plan  = {}
        self.queries     = []                    # רשימת כל‑ה‑SQL לריצה במקביל

    # ------------------------------------------------------------------ build
    def build(self, engine, metadata) -> dict[int, dict]:
        """בונה תכנית שטוחה וממלא self.queries."""
        self.built_plan = {}
        self.queries.clear()                     # איפוס למקרה של ריצה חוזרת

        for idx, step in enumerate(self.plan, 1):
            gen       = step["generator"]
            repeat    = step["repeat"]
            selector  = step.get("selector")
            q_type    = type(gen).__name__.replace("QueryStrategy", "").lower()
            sql       = gen.generate_query(metadata, self.db_type.lower(),
                                           selector=selector)

            self.built_plan[idx] = {
                "query":      sql,
                "query_type": q_type,
                "repeat":     repeat,
                "selector":   selector
            }
            self.queries.append(sql)             # לשימוש Locust

        return self.built_plan

    # ------------------------------------------------------------------- run
    def run(self, engine, metadata, locust_config: dict | None = None):
        if not self.built_plan:
            raise RuntimeError("build() must be called before run().")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─" * 60)

        if locust_config:
            self._run_with_locust(engine, locust_config)
        else:
            self._run_without_locust(engine)

    # ----------------------------------------------------------- sync runner
    def _run_without_locust(self, engine):
        for idx, step in self.built_plan.items():
            sql     = step["query"]
            label   = f"Step {idx}"
            repeat  = step["repeat"]
            selector = step.get("selector")

            self._sqls[label] = sql
            self._sels[label] = selector

            for _ in range(repeat):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                self._dur[label].append(time.perf_counter() - t0)

    # ---------------------------------------------------------- locust runner
    def _run_with_locust(self, engine, cfg: dict):
        """cfg = {'wait_time_min':1,'wait_time_max':3,'users':10,
                  'spawn_rate':2,'run_time':20}"""

        class DatabaseUser(User):
            wait_time = between(cfg["wait_time_min"], cfg["wait_time_max"])

            def on_start(self):
                # environment.test_queries הוגדר למטה
                self.queries = self.environment.test_queries

            @task
            def run_random_query(self):
                sql = random.choice(self.queries)
                t0  = time.perf_counter()
                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                except Exception as err:
                    print("❌", err)
                print(f"Executed query in {time.perf_counter()-t0:.4f}s")

        # הקמת סביבה והרצה
        env = Environment(user_classes=[DatabaseUser])
        env.test_queries = self.queries          # רשימת שאילתות רלוונטית
        env.create_local_runner()

        env.runner.start(cfg["users"], cfg["spawn_rate"])
        gevent.sleep(cfg["run_time"])            # מגביל אורך טסט
        env.runner.quit()
        env.runner.greenlet.join()

        time.sleep(5)                            # מנוחה בין DB‑ים
        print(f"Locust run finished after {cfg['run_time']} s")

    # -------------------------------------------------------- results helper
    def get_built_plan_with_durations(self) -> dict[int, dict]:
        result = {}
        for idx, step in self.built_plan.items():
            label     = f"Step {idx}"
            durations = [Decimal(f"{d:.8f}") for d in self._dur.get(label, [])]
            stdev     = (Decimal(f"{statistics.stdev(durations):.8f}")
                         if len(durations) > 1 else Decimal("0.0"))
            result[idx] = {**step, "durations": durations, "stddev": stdev}
        return result
