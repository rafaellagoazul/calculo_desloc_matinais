from pathlib import Path
import shutil
from .call_graph import CallGraphAnalyzer

from tools.analyzer.import_graph import ImportGraph
from tools.analyzer.unused_files import classify
from tools.explorer.explorer_state import ExplorerState
from tools.analyzer.dependency_graph import DependencyGraph
from tools.analyzer.dynamic_imports import DynamicImportDetector
from tools.analyzer.call_graph import CallGraphAnalyzer

class AnalyzerActions:
    def __init__(self, root: Path, explorer_state: ExplorerState):
        self.root = root
        self.explorer_state = explorer_state

    def scan_unused(self, mode: str = "all") -> list[tuple[str, str]]:
        """
        mode:
            - "all" (padrão)
            - reservado para futuros modos (active, suspects, etc)
        """

        frozen = {
            k for k, v in self.explorer_state.state.get("frozen", {}).items()
            if v
        }

        graph = ImportGraph(self.root, frozen=frozen)
        graph.build()

        result = []
        for f in graph.unused_files():
            risk = classify(f, graph.reverse)
            result.append((f, risk))

        return result


    def freeze_safe(self) -> int:
        count = 0
        results = self.scan_unused()

        for file, risk in results:
            if risk == "safe":
                self.explorer_state.freeze(file)
                count += 1

        self.explorer_state.save()
        return count

    def quarantine_safe(self) -> int:
        quarantine = self.root / ".quarantine"
        quarantine.mkdir(exist_ok=True)

        count = 0
        results = self.scan_unused()

        for file, risk in results:
            if risk == "safe":
                src = self.root / file
                if src.exists():
                    dst = quarantine / src.name
                    shutil.move(str(src), str(dst))
                    count += 1

        return count

    def diff_modes(self):
        # modos não existem mais → mantido por compatibilidade
        return []

    def build_dependency_graph(self):
        graph = DependencyGraph(self.root)
        return graph.build()
    
    def scan_dynamic_imports(self):
        detector = DynamicImportDetector(self.root)
        return detector.scan()

    def risk_scores(self):
        graph = self.build_dependency_graph()
        dynamic = self.scan_dynamic_imports()

        quarantined = {
            p.name for p in (self.root / ".quarantine").glob("*.py")
        } if (self.root / ".quarantine").exists() else set()

        from tools.analyzer.risk_score import score_files
        return score_files(graph, dynamic, quarantined)

    def scan_plugins(self):
        from tools.analyzer.plugin_detector import PluginDetector
        return PluginDetector(self.root).scan()

    def simulate_removal(self, file):
        graph = self.build_dependency_graph()
        from tools.analyzer.impact_simulator import invert_graph

        inv = invert_graph(graph)
        return sorted(inv.get(file, []))
    
    def scan_call_graph(self):
        analyzer = CallGraphAnalyzer(self.root)
        return analyzer.analyze()

    def quarantine_dead_functions(self):
        report = self.scan_call_graph()

        # somente código realmente morto
        dead = set(report["dead"])

        modified_files = set()

        for fn in dead:
            # precisa ser função qualificada
            if "." not in fn:
                continue

            module, name = fn.rsplit(".", 1)

            # segurança extra
            if any(x in fn for x in ("test_", "Analyzer", "call_graph")):
                continue

            for py in self.root.rglob("*.py"):
                if "tests" in py.parts or "tools" in py.parts:
                    continue

                try:
                    text = py.read_text(encoding="utf-8")
                except Exception:
                    continue

                marker = f"def {name}("
                if marker in text:
                    new_text = text.replace(
                        marker,
                        f"# DEAD_CODE_CONFIRMED: {marker}"
                    )
                    py.write_text(new_text, encoding="utf-8")
                    modified_files.add(py.name)

        return sorted(modified_files)


    def build_call_graph(self):
        from tools.analyzer.call_graph import CallGraphAnalyzer
        analyzer = CallGraphAnalyzer(self.root)
        report = analyzer.analyze()
        return report["graph"], report


    def export_callgraph_report(self, output: str = "callgraph_report.json"):
        report = self.scan_call_graph()

        data = {
            "summary": {
                "entry_points": len(report["entry_points"]),
                "callbacks": len(report.get("callbacks", [])),
                "reachable": len(report["reachable"]),
                "orphans": len(report["orphan"]),
                "dead": len(report["dead"]),
            },
            "details": report,
        }

        path = self.root / output
        path.write_text(
            __import__("json").dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        return path

    def get_routes(self):
        """
        Retorna rotas de execução reais (entry → chamadas)
        para consumo do AnalyzerUI.
        """
        analyzer = CallGraphAnalyzer(self.root)

        report = analyzer.analyze()

        # se o CallGraphAnalyzer ainda não gera rotas,
        # criamos aqui a visão de rota a partir do grafo
        graph = report["graph"]
        entry_points = report["entry_points"]

        routes = []

        for entry in entry_points:
            stack = [(entry, [entry])]

            while stack:
                node, path = stack.pop()
                calls = graph.get(node, [])

                if not calls:
                    routes.append([
                        {
                            "name": p,
                            "layer": self._infer_layer(p),
                            "role": "function",
                            "decision": None,
                        }
                        for p in path
                    ])
                    continue

                for c in calls:
                    if c not in path:  # evita loop
                        stack.append((c, path + [c]))

        return routes

