# import time
#
# from main.core.test_framework.base_test import BaseTest
#
# #TODO: MODULER TO FUNCTIONS , ADD MORE FUNCRTILITY TO EXCUTION PLAN LIE (BOOLEAN IF WE WANT TO USE INDEXS OR NOT )
# # TODO : WE NEED TO MAKE DEFAULT VALUES FOR A PLAN
# class ExecutionPlanTest(BaseTest):
#     def __init__(self, execution_plan: list, db_type: str):
#         super().__init__()
#         self.execution_plan = execution_plan
#         self.results = []
#         self.db_type = db_type
#
#     def run(self,engine, metadata):
#         print("🚀 Starting Execution Plan...\n")
#         for step_index, step in enumerate(self.execution_plan):
#             gen = step["generator"]
#             repeat = step["repeat"]
#             delay = step.get("delay", 0)
#             label = step.get("label", f"Step {step_index + 1}")
#
#             print(f"\n▶️ {label} — {repeat} runs")
#
#             query = gen.generate_query(metadata,self.db_type,selector=step.get("selector"))
#             print(f"  ↪ Query: {query}")
#             for i in range(repeat):
#                 start = time.perf_counter()
#                 self.execute_query(engine, query)
#                 duration = time.perf_counter() - start
#
#                 self.results.append({
#                     "step": label,
#                     "query": query[:60],
#                     "duration": duration
#                 })
#
#                 print(f"  Run {i + 1}/{repeat} took {duration:.4f}s")
#
#                 if delay:
#                     time.sleep(delay)
#
#         return self._summarize()
#
#     def _summarize(self):
#         durations = [r["duration"] for r in self.results]
#         print("\n📊 Test Summary:")
#         print(f"Total runs: {len(durations)}")
#         print(f"Average time: {sum(durations) / len(durations):.4f}s")
#         print(f"DB Type: {self.db_type}")
#         return self.results
#
#     def preview(self, metadata):
#         print("👁️  Previewing Execution Plan...\n")
#         for step_index, step in enumerate(self.execution_plan):
#             gen = step["generator"]
#             repeat = step["repeat"]
#             label = step.get("label", f"Step {step_index + 1}")
#
#             query = gen.generate_query(metadata)
#
#             print(f"🔸 {label}")
#             print(f"  ↪ Will repeat: {repeat} times")
#             print(f"  ↪ Query: {query}\n")

# main/core/test_framework/execution_plan_test.py
import statistics, time
from collections import defaultdict
from main.core.test_framework.base_test import BaseTest
from main.core.schema_analysis.table_profiler import get_rowcounts

class ExecutionPlanTest(BaseTest):
    def __init__(self, execution_plan: list, db_type: str, schema: str):
        super().__init__()
        self.plan      = execution_plan
        self.db_type   = db_type.upper()
        self.schema    = schema
        self._dur     = defaultdict(list)
        self._sels    = {}   # label → selector

    def run(self, engine, metadata):
        hdr = f"\n🚀  Benchmark for **{self.db_type}** against schema **{self.schema}**"
        print(hdr, "\n" + "─" * len(hdr))

        # 1) pull all row‑counts once
        rowcounts = dict(get_rowcounts(engine, self.schema))

        # 2) run every step, record durations and selectors
        for idx, step in enumerate(self.plan, 1):
            label    = step.get("label", f"Step {idx}")
            generator= step["generator"]
            repeat   = step["repeat"]
            selector = step.get("selector")
            self._sels[label] = selector

            sql = generator.generate_query(metadata, self.db_type.lower(), selector=selector)
            for _ in range(repeat):
                t0 = time.perf_counter()
                self.execute_query(engine, sql)
                self._dur[label].append(time.perf_counter() - t0)

        # 3) final summary
        print("\n📊  Summary for", self.db_type)
        print("─" * 52)
        total_q, total_t = 0, 0.0
        table_keys = sorted(metadata.tables.keys())

        for label, samples in self._dur.items():
            n   = len(samples)
            avg = statistics.mean(samples)
            sd  = statistics.stdev(samples) if n>1 else 0.0
            sel = self._sels[label]
            tbl = table_keys[sel % len(table_keys)].split(".")[-1]
            print(f"{label:<32} runs={n:>3}   avg={avg:.4f}s ±{sd:.4f}s   table={tbl}")
            total_q += n
            total_t += sum(samples)

        print("─" * 52)
        print(f"TOTAL: {total_q} queries   overall avg={total_t/total_q:.4f}s\n")
