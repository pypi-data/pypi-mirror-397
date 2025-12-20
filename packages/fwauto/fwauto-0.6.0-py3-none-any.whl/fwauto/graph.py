"""LangGraph workflow definition for firmware development."""

from langgraph.graph import END, START, StateGraph

from .langsmith_config import init_langsmith
from .logging_config import get_logger
from .nodes.ai_brain import ai_brain_node
from .nodes.build import build_node
from .nodes.chat import chat_node
from .nodes.deploy import deploy_node
from .nodes.init import init_project_node
from .nodes.log import log_node
from .state import FirmwareState


def create_firmware_graph():
    """Create the firmware development workflow graph."""
    # Initialize LangSmith if configured
    init_langsmith()

    workflow = StateGraph(FirmwareState)

    # Add nodes
    workflow.add_node("init_project", init_project_node)
    workflow.add_node("ai_brain", ai_brain_node)
    workflow.add_node("build", build_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("deploy", deploy_node)
    workflow.add_node("log", log_node)

    # Define routing functions
    def route_from_start(state: FirmwareState) -> str:
        """Route from START based on execution mode set by Typer CLI."""
        mode = state.get("execution_mode")

        # Validate state from CLI
        if not mode or not state.get("command"):
            return "end"

        # Display mode
        print(f"🎯 Mode: {mode}")

        # Check for error/help modes - end immediately
        if mode in ["error", "help", "verify"]:
            return "end"

        # Check if project initialization is needed
        if not state.get("project_initialized", False):
            return "init_project"

        # Route based on mode
        routing_map = {
            "build": "build",
            "run": "build",
            "deploy": "deploy",
            "log": "log",
            "feat": "ai_brain",
            "rag": "ai_brain",
            "chat": "chat",
        }

        # Output project_root if initialized
        if state.get("project_initialized") and state.get("project_root"):
            print(f"📁 專案路徑: {state['project_root']}")

        return routing_map.get(mode, "end")

    def route_after_init(state: FirmwareState) -> str:
        """Route after project initialization."""
        mode = state.get("execution_mode")

        # Output project root after initialization
        if state.get("project_root"):
            print(f"📁 專案路徑: {state['project_root']}")

        # Route based on mode
        routing_map = {
            "build": "build",
            "run": "build",
            "deploy": "deploy",
            "log": "log",
            "feat": "ai_brain",
            "rag": "ai_brain",
            "chat": "chat",
        }

        if mode is None:
            return "end"
        return routing_map.get(mode, "end")

    def route_after_build(state: FirmwareState) -> str:
        """Route after build based on build status and mode."""
        if state["build_status"] == "success":
            # Check if this is run mode (should deploy after build)
            mode_metadata = state["mode_metadata"] or {}
            if mode_metadata.get("deploy_after_build") or state["execution_mode"] == "run":
                return "deploy"
            return "end"  # Build-only mode ends here
        else:
            # Build failed - check if we can retry with AI fix
            current_iteration = state.get("iteration", 0)
            max_retries = state.get("max_retries", 3)

            if current_iteration < max_retries:
                logger = get_logger("workflow")
                logger.debug(f"🔄 Build failed (iteration {current_iteration}/{max_retries}), routing to AI fix...")
                return "ai_brain"  # Route to AI for code fixing
            else:
                logger = get_logger("workflow")
                logger.debug(f"❌ Max retries ({max_retries}) reached, ending workflow")
                return "end"  # Max retries reached, end workflow

    def route_after_ai_brain(state: FirmwareState) -> str:
        """Route after ai_brain node."""
        mode = state.get("execution_mode")

        # RAG mode ends directly (no build needed)
        if mode == "rag":
            return "end"

        # feat mode with deploy_after_build enabled should go to build then deploy
        mode_metadata = state.get("mode_metadata") or {}
        if mode == "feat" and mode_metadata.get("deploy_after_build"):
            return "build"

        # AI Brain 成功處理後，無論狀態如何都應該回到 build 重新編譯驗證修復
        # After AI fix attempt, always route back to build to verify the fix
        return "build"

    def route_after_deploy(state: FirmwareState) -> str:
        """Route after deploy based on deploy status."""
        if state["deploy_status"] == "success":
            # All successful deploy operations end here
            return "end"
        else:
            # Deploy failed - end workflow (user needs to fix hardware/connection)
            return "end"

    # Set up edges - START routes directly based on mode
    workflow.add_conditional_edges(
        START,
        route_from_start,
        {
            "init_project": "init_project",
            "build": "build",
            "deploy": "deploy",
            "log": "log",
            "ai_brain": "ai_brain",
            "chat": "chat",
            "end": END,
        },
    )

    # After init, route based on mode
    workflow.add_conditional_edges(
        "init_project",
        route_after_init,
        {
            "build": "build",
            "deploy": "deploy",
            "log": "log",
            "ai_brain": "ai_brain",
            "chat": "chat",
            "end": END,
        },
    )

    # Build node routing (for direct build without codegen)
    workflow.add_conditional_edges(
        "build",
        route_after_build,
        {
            "deploy": "deploy",
            "ai_brain": "ai_brain",  # AI fix retry loop
            "end": END,
        },
    )

    # AI Brain node routing
    workflow.add_conditional_edges(
        "ai_brain",
        route_after_ai_brain,
        {
            "deploy": "deploy",
            "build": "build",  # Route back to build after AI fix
            "end": END,
        },
    )

    # Deploy routing
    workflow.add_conditional_edges(
        "deploy",
        route_after_deploy,
        {"end": END},
    )

    # Log analysis routing - always ends after analysis
    workflow.add_edge("log", END)

    # Chat routing - always ends after chat session
    workflow.add_edge("chat", END)

    return workflow.compile()


def visualize_workflow():
    """Generate and export workflow visualization."""
    app = create_firmware_graph()

    # Generate Mermaid diagram
    print("\n📊 Workflow Diagram (Mermaid format):")
    print("=" * 50)
    mermaid_diagram = app.get_graph().draw_mermaid()
    print(mermaid_diagram)
    print("=" * 50)

    # Try to export as PNG
    try:
        png_data = app.get_graph().draw_mermaid_png()
        with open("docs/assets/langgraph.png", "wb") as f:
            f.write(png_data)
        print("\n✅ Graph exported to docs/assets/langgraph.png")
    except Exception as e:
        print(f"\n⚠️ PNG export not available: {e}")
        print("💡 You can copy the Mermaid diagram above to visualize online")

    return app
