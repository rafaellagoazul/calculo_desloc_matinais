from tools.backup.backup_manager_ui import mount_backup_ui
from tools.runner.main_runner_tool import mount_main_runner
from tools.code_fixer import mount_code_fixer_tool
from tools.explorer.project_explorer import ProjectExplorer
from tools.explorer.explorer_state import ExplorerState
from tools.explorer.explorer_actions import ExplorerActions
from pathlib import Path
from pathlib import Path
from tools.explorer.explorer_state import ExplorerState
from tools.analyzer.analyzer_adapter import AnalyzerAdapter
from tools.analyzer.analyzer_ui import AnalyzerUI


ROOT = Path(__file__).resolve().parents[1]

def mount_explorer(parent):
    state = ExplorerState()
    actions = ExplorerActions(ROOT, state)

    ui = ProjectExplorer(parent, state=state, actions=actions)
    ui.pack(fill="both", expand=True)
    return ui

def _mount_analyzer(parent):
    state = ExplorerState()
    actions = AnalyzerAdapter(Path.cwd(), state)

    ui = AnalyzerUI(parent, actions)
    ui.pack(fill="both", expand=True)



TOOLS = [
    {
        "name": "▶ Executar Sistema",
        "mount": mount_main_runner
    },
    {
        "name": "💾 Backup Manager",
        "mount": mount_backup_ui
    },
    {
        "name": "🛠 Code Fixer",
        "group": "Manutenção",
        "mount": mount_code_fixer_tool,
    },
    {
        "id": "explorer",
        "name": "📁 Explorer",
        "mount": mount_explorer
    },
    {
        "name": "Analyzer",
        "mount": lambda parent: _mount_analyzer(parent)
    }

]
