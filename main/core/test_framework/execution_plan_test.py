import time

from main.core.test_framework.base_test import BaseTest


class ExecutionPlanTest(BaseTest):
    def __init__(self, execution_plan: list):
        super().__init__()
        self.execution_plan = execution_plan
        self.results = []

    def run(self, engine, metadata):
        print("🚀 Starting Execution Plan...\n")
        for step_index, step in enumerate(self.execution_plan):
            gen = step["generator"]
            repeat = step["repeat"]
            delay = step.get("delay", 0)
            label = step.get("label", f"Step {step_index + 1}")

            print(f"\n▶️ {label} — {repeat} runs")

            query = gen.generate_query(metadata)

            for i in range(repeat):
                start = time.perf_counter()
                self.execute_query(engine, query)
                duration = time.perf_counter() - start

                self.results.append({
                    "step": label,
                    "query": query[:60],
                    "duration": duration
                })

                print(f"  Run {i + 1}/{repeat} took {duration:.4f}s")

                if delay:
                    time.sleep(delay)

        return self._summarize()

    def _summarize(self):
        durations = [r["duration"] for r in self.results]
        print("\n📊 Test Summary:")
        print(f"Total runs: {len(durations)}")
        print(f"Average time: {sum(durations) / len(durations):.4f}s")
        return self.results

    def preview(self, metadata):
        print("👁️  Previewing Execution Plan...\n")
        for step_index, step in enumerate(self.execution_plan):
            gen = step["generator"]
            repeat = step["repeat"]
            label = step.get("label", f"Step {step_index + 1}")

            query = gen.generate_query(metadata)

            print(f"🔸 {label}")
            print(f"  ↪ Will repeat: {repeat} times")
            print(f"  ↪ Query: {query}\n")
