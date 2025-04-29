# # main/core/test_framework/execution_plan_test.py
# import statistics, time
# from collections import defaultdict
# from main.core.test_framework.base_test import BaseTest
# from main.core.schema_analysis.table_profiler import get_rowcounts
#
# class ExecutionPlanTest(BaseTest):
#     def __init__(self, execution_plan: list, db_type: str, schema: str):
#         super().__init__()
#         self.plan    = execution_plan
#         self.db_type = db_type.upper()
#         self.schema  = schema
#         self._dur    = defaultdict(list)
#         self._sels   = {}   # label → selector
#         self._sqls   = {}   # label → SQL string ← חשוב
#
#
#     def build(self, engine, metadata) -> dict[int, dict]:
#         """
#         Builds a flat structured test plan:
#         {
#             1: {"query": "...", "query_type": "...", "repeat": N},
#             2: {...},
#             ...
#         }
#         """
#         plan_dict = {}
#
#         for idx, step in enumerate(self.plan, 1):
#             generator = step["generator"]
#             repeat = step["repeat"]
#             selector = step.get("selector")
#
#             # סוג השאילתה
#             query_type = type(generator).__name__.replace("QueryStrategy", "").lower()
#
#             # הפקת השאילתה בפועל
#             sql = generator.generate_query(metadata, self.db_type.lower(), selector=selector)
#
#             # הוספה למילון
#             plan_dict[idx] = {
#                 "query": sql,
#                 "query_type": query_type,
#                 "repeat": repeat
#                 # בעתיד: "delay": step.get("delay", 0), וכו'
#             }
#
#         return plan_dict
#
#
#
#     def run(self, engine, metadata):
#         hdr = f"\n🚀  Benchmark for **{self.db_type}** against schema **{self.schema}**"
#         print(hdr, "\n" + "─" * len(hdr))
#
#         rowcounts = dict(get_rowcounts(engine, self.schema))
#
#         for idx, step in enumerate(self.plan, 1):
#             label     = step.get("label", f"Step {idx}")
#             generator = step["generator"]
#             repeat    = step["repeat"]
#             selector  = step.get("selector")
#
#             sql = generator.generate_query(metadata, self.db_type.lower(), selector=selector)
#
#             self._sels[label] = selector
#             self._sqls[label] = sql
#
#             for _ in range(repeat):
#                 t0 = time.perf_counter()
#                 self.execute_query(engine, sql)
#                 self._dur[label].append(time.perf_counter() - t0)
#
#         # Summary
#         print("\n📊  Summary for", self.db_type)
#         print("─" * 52)
#         total_q, total_t = 0, 0.0
#         table_keys = sorted(metadata.tables.keys())
#
#         for label, samples in self._dur.items():
#             n     = len(samples)
#             avg   = statistics.mean(samples)
#             sd    = statistics.stdev(samples) if n > 1 else 0.0
#             sel   = self._sels[label]
#             tbl   = table_keys[sel % len(table_keys)].split(".")[-1]
#             sql   = self._sqls[label]
#
#             print(f"{label:<32} runs={n:>3}   avg={avg:.4f}s ±{sd:.4f}s   table={tbl}")
#             print(f"  SQL: {sql}")
#
#             total_q += n
#             total_t += sum(samples)
#
#         print("─" * 52)
#         print(f"TOTAL: {total_q} queries   overall avg={total_t/total_q:.4f}s\n")



import statistics
import time
from collections import defaultdict
from main.core.test_framework.base_test import BaseTest
from main.core.schema_analysis.table_profiler import get_rowcounts

class ExecutionPlanTest(BaseTest):
    def __init__(self, execution_plan: list, db_type: str, schema: str, test_name: str = "unknown"):
        super().__init__()
        self.plan       = execution_plan         # תכנית הבדיקה (raw)
        self.db_type    = db_type.upper()
        self.schema     = schema
        self.test_name  = test_name              # שם הבדיקה (לוגי)
        self._dur       = defaultdict(list)      # label → רשימת זמני הריצה
        self._sels      = {}                     # label → selector
        self._sqls      = {}                     # label → השאילתה המקורית
        self.built_plan = {}                     # נבנה בפונקציית build

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
            generator   = step["generator"]
            repeat      = step["repeat"]
            selector    = step.get("selector")
            query_type  = type(generator).__name__.replace("QueryStrategy", "").lower()
            sql         = generator.generate_query(metadata, self.db_type.lower(), selector=selector)

            self.built_plan[idx] = {
                "query": sql,
                "query_type": query_type,
                "repeat": repeat,
                "selector": selector
            }

        return self.built_plan

    def run(self, engine, metadata):
        """
        מריץ את הבדיקה בפועל לפי הנתונים שנבנו ע״י build()
        """
        if not self.built_plan:
            raise RuntimeError("You must call build() before run().")

        print(f"\n🚀 Benchmark for {self.db_type} against schema {self.schema}")
        print("─" * 60)

        for idx, step in self.built_plan.items():
            sql        = step["query"]
            label      = f"Step {idx}"
            repeat     = step["repeat"]
            selector   = step.get("selector")

            self._sqls[label] = sql
            self._sels[label] = selector

            for _ in range(repeat):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                self._dur[label].append(time.perf_counter() - t0)

    def print_summary(self, metadata):
        """
        מדפיסה את סיכום תוצאות הבדיקה לפי הנתונים השמורים בלבד
        """
        print(f"\n📊 Summary for {self.db_type}")
        print("─" * 52)

        total_q, total_t = 0, 0.0
        table_keys = sorted(metadata.tables.keys())

        for label, samples in self._dur.items():
            n   = len(samples)
            avg = statistics.mean(samples)
            sd  = statistics.stdev(samples) if n > 1 else 0.0
            sel = self._sels[label]
            sql = self._sqls[label]
            tbl = table_keys[sel % len(table_keys)].split(".")[-1] if sel is not None else "?"

            print(f"{label:<32} runs={n:>3}   avg={avg:.4f}s ±{sd:.4f}s   table={tbl}")
            print(f"  SQL: {sql}")

            total_q += n
            total_t += sum(samples)

        print("─" * 52)
        print(f"TOTAL: {total_q} queries   overall avg={total_t/total_q:.4f}s\n")
