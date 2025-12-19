from fastmcp import FastMCP, Context
from fastmcp.prompts.prompt import PromptMessage, TextContent
from mcts_gen.services.ai_gp_simulator import AiGpSimulator

# 1. Create the core FastMCP server instance
mcp = FastMCP(
    name="mcts_gen_simulator_server"
)

# 2. Create an instance of our stateful simulator class.
#    The simulator's __init__ method will register its own methods as tools.
simulator = AiGpSimulator(mcp)

# 3. Define the built-in agent prompt using a decorator
@mcp.prompt(
    name="mcts_autonomous_search",
    description="Autonomous MCTS strategist workflow that emulates AGENTS.md content",
)
def mcts_autonomous_search(goal: str, ctx: Context) -> list[PromptMessage]:
    """
    Provides the AI with the standard workflow for running an MCTS search.
    This is the code-based version of the old AGENTS.md file.
    """
    intro = f"You are an autonomous MCTS strategist. Your goal is to find the optimal move. Task: {goal}"
    workflow = [
        "**Phase 1: Investigation**",
        "1. **Identify the Game Module**: Based on the user's request (e.g., 'ligand', 'chess'), determine the target game module file path (e.g., `src/mcts_gen/games/ligand_mcts.py`).",
        "2. **Analyze the Game Module**: Read the contents of the identified file.",
        "3. **Find the GameState Class**: Scan the file to find the class that inherits from `GameStateBase`.",
        "4. **Analyze the Constructor**: Examine the `__init__` method signature and docstring of the `GameStateBase` subclass to identify all required constructor arguments, their types, and descriptions.",

        "\n**Phase 2: Initialization**",
        "5. **Gather Arguments**: If the constructor requires arguments (like `pocket_path` for `ligand_mcts`), ask the user to provide the necessary information. If no arguments are needed, proceed directly.",
        "6. **Initialize Simulation**: Call the `reinitialize_mcts` tool. You must provide `state_module` (e.g., 'mcts_gen.games.ligand_mcts') and `state_class` (e.g., 'LigandMCTSGameState'). If the game requires constructor arguments, pass them in the `state_kwargs` dictionary (e.g., `{'pocket_path': '/path/to/file.pdb'}`).",

        "\n**Phase 3: Execution (The MCTS/GP Cycle)**",
        "Your goal is to find the best move by intelligently guiding the MCTS search. You will act like a Genetic Programming (GP) algorithm, making decisions after each round.",
        "Follow this cycle **strictly**:",
        "",
        "1. **EXECUTE Round**: Call `run_mcts_round(exploration_constant=..., actions_to_expand=...)`.",
        "   - On the first round, you can omit `actions_to_expand`.",
        "   - On subsequent rounds, use `actions_to_expand` to focus the search on promising branches. You can get a list of all possible branches by calling `get_possible_actions`.",
        "",
        "2. **ANALYZE Results**: Call `get_simulation_stats()` to see the result of the last round. Pay close attention to the `improvement` value.",
        "",
        "3. **DECIDE Next Step**: Based on the stats, decide your next move:",
        "   - **If `improvement` is low or zero** for several rounds, the search has likely converged. Proceed to Step 4.",
        "   - **If `improvement` is good**, continue the search cycle (go back to Step 1).",
        "",
        "4. **FINALIZE**: Once the search has converged, you have two options to get the result:",
        "   - **Option A (simple):** Call `get_best_move()` to get only the best immediate next action.",
        "   - **Option B (complete):** Call `get_principal_variation()` to get the entire best sequence of moves and a detailed summary of the final state (which may include a path to a PDB file for certain games).",
        "   Choose the option that best fits the request. For a full analysis, Option B is preferred.",
        "",
        "**CRITICAL RULE: You MUST alternate between `run_mcts_round` and another tool (like `get_simulation_stats` or `get_possible_actions`). NEVER call the same tool twice in a row.**",
    ]
    detail = "\n".join(workflow)
    return [
        PromptMessage(role="user", content=TextContent(type="text", text=intro)),
        PromptMessage(role="user", content=TextContent(type="text", text=detail)),
    ]

# 4. Run the server
if __name__ == "__main__":
    mcp.run()