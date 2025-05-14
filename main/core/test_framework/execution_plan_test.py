# main/core/test_framework/execution_plan_test.py
import random, time, statistics, gevent
from collections import defaultdict
from decimal import Decimal
from sqlalchemy import text
from locust import User, task, between, events
from locust.env import Environment

from main.core.test_framework.base_test import BaseTest


class ExecutionPlanTest(BaseTest):
    """
    • build()  – בונה self.built_plan בדיוק כמו קודם
    • run_without_locust() – לא השתנה
    • run_with_locust() – *חדש*: דוחף את המדידות חזרה ל‑_dur / _sqls / _sels
      › כך ה‑UI מקבל שוב durations + stddev + query_type
    """

    def __init__(self, execution_plan, db_type, schema, test_name="unknown"):
        super().__init__()
        self.plan       = execution_plan
        self.db_type    = db_type.upper()
        self.schema     = schema
        self.test_name  = test_name

        self._dur, self._sels, self._sqls = defaultdict(list), {}, {}
        self.built_plan: dict[int, dict]  = {}

        # טבלה הפוכה: sql → label  (ייתכן כמה sqlים זהים – הכול תחת אותו label)
        self._sql_to_label: dict[str, str] = {}

    # ---------- build --------------------------------------------------------
    def build(self, engine, metadata):
        self.built_plan = {}
        for idx, step in enumerate(self.plan, 1):
            gen      = step["generator"]
            repeat   = step["repeat"]
            selector = step.get("selector")
            qtype    = type(gen).__name__.replace("QueryStrategy", "").lower()
            sql      = gen.generate_query(metadata, self.db_type.lower(), selector)

            label = f"Step {idx}"
            self.built_plan[idx] = {
                "query"      : sql,
                "query_type" : qtype,
                "repeat"     : repeat,
                "selector"   : selector,
            }
            self._sql_to_label[sql] = label   # קישור לטבלה ההפוכה
        return self.built_plan

    # ---------- public run ---------------------------------------------------
    def run(self, engine, metadata, locust_config: dict | None = None):
        if not self.built_plan:
            raise RuntimeError("build() must run first")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─"*60)

        if locust_config:
            self._run_with_locust(engine, locust_config)
        else:
            self._run_without_locust(engine)

    # ---------- single‑thread run (כמו בעבר) --------------------------------
    def _run_without_locust(self, engine):
        for idx, step in self.built_plan.items():
            sql, label = step["query"], f"Step {idx}"
            self._sqls[label] = sql
            self._sels[label] = step.get("selector")

            for _ in range(step["repeat"]):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                self._dur[label].append(time.perf_counter() - t0)

    # ---------- locust multi‑user run ---------------------------------------
    def _run_with_locust(self, engine, cfg):
        """
        cfg example:
        {
          "wait_time_min": 1,
          "wait_time_max": 3,
          "users"       : 10,
          "spawn_rate"  : 2,
          "run_time"    : 20          # שניות
        }
        """

        # 1. הכנת רשימה שטוחה של כל השאילתות (כולל repeat)
        flat_queries: list[str] = []
        for step in self.built_plan.values():
            flat_queries.extend([step["query"]] * step["repeat"])

        # 2. מחלקת‑Locust פנימית
        parent = self               # סגירה עבור DatabaseUser

        class DatabaseUser(User):
            wait_time = between(cfg["wait_time_min"], cfg["wait_time_max"])

            @task
            def random_query(self):
                sql = random.choice(flat_queries)
                t0  = time.perf_counter()
                try:
                    with engine.connect() as conn:
                        conn.execute(text(sql))
                except Exception as e:
                    print("❌", e)

                duration = time.perf_counter() - t0
                label    = parent._sql_to_label[sql]          # "Step X"

                parent._sqls[label] = sql
                parent._sels[label] = parent.built_plan[int(label.split()[1])]["selector"]
                parent._dur[label].append(duration)

                print(f"Executed query in {duration:.4f}s")

        # 3. הפעלת Locust (headless)
        env = Environment(user_classes=[DatabaseUser])
        env.create_local_runner()
        env.runner.start(cfg["users"], spawn_rate=cfg["spawn_rate"])

        # סיום אוטומטי אחרי run_time שניות
        gevent.spawn_later(cfg["run_time"], lambda: env.runner.quit())
        env.runner.greenlet.join()

        print(f"Locust run finished after {cfg['run_time']} s")

    # ---------- תוצרים ל‑UI ---------------------------------------------------
    def get_built_plan_with_durations(self):
        res = {}
        for idx, step in self.built_plan.items():
            label      = f"Step {idx}"
            durations  = [Decimal(f"{d:.8f}") for d in self._dur.get(label, [])]
            stddev     = Decimal(f"{statistics.stdev(durations):.8f}") if len(durations) > 1 else Decimal("0.0")
            res[idx]   = {**step, "durations": durations, "stddev": stddev}
        return res
