"""
Smart Command Wrapper for KaliRoot CLI (kr-cli)
Executes commands and analyzes output for vulnerabilities/next steps.
Includes Reporting capabilities.
"""

import sys
import subprocess
import shutil
import logging
from .ai_handler import AIHandler, get_ai_response
from .ui.display import console, print_info, print_success, print_error, show_loading
from .database_manager import get_chat_history, get_user_profile
from .reporting import ReportGenerator

# Setup logging
logger = logging.getLogger(__name__)

from .api_client import api_client

TABLE_HEADER = "[bold cyan]KaliRoot CLI[/bold cyan]"

# Tools that trigger AI analysis
ANALYSIS_TARGETS = ['nmap', 'gobuster', 'sqlmap', 'nikto', 'wfuzz', 'hydra', 'metasploit', 'msfconsole']

def execute_and_analyze(args):
    """Execute command and analyze key outputs."""
    command = args[0]
    full_cmd = " ".join(args)
    
    # 1. Execute Command
    console.print(f"[dim]⚡ Executing: {full_cmd}[/dim]")
    
    try:
        # Run command and stream output
        # using subprocess.run for simplicity in capturing everything
        process = subprocess.run(
            args, 
            capture_output=True, 
            text=True
        )
        
        stdout = process.stdout
        stderr = process.stderr
        
        # Print output to user
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
            
        # 2. Analyze if relevant
        if command in ANALYSIS_TARGETS or any(t in command for t in ANALYSIS_TARGETS):
            # Interactive Confirmation
            console.print("\n[bold yellow]✨ Análisis de IA disponible (Costo: 1 crédito)[/bold yellow]")
            if not console.input("[dim]¿Analizar salida con IA? [Y/n]: [/dim]").lower().startswith('y'):
                return

            # Fetch real user ID from session
            if not api_client.is_logged_in() or not api_client.user_id:
                print_info("ℹ️ Inicia sesión para análisis AI: kr-cli login")
                return
                
            user_id = api_client.user_id 
            
            output_to_analyze = stdout + "\n" + stderr
            output_to_analyze = output_to_analyze[-1500:] # Strict limit for free tier tokens
            
            query = f"CMD: {full_cmd}\nOUTPUT:\n{output_to_analyze}\n\nAnalyze output. Verify user request."
            
            with show_loading("🧠 Analyzing results (RAG & AI)..."):
                # AI Handler will manage RAG internally
                response = get_ai_response(user_id, query)
                
            console.print("\n[bold cyan]🧠 AI ANALYSIS[/bold cyan]")
            console.print(response)
            
    except FileNotFoundError:
        print_error(f"Command not found: {command}")
    except KeyboardInterrupt:
        print_error("\nExecution interrupted.")
        sys.exit(130)
    except Exception as e:
        print_error(f"Execution error: {e}")

def handle_report():
    """Generate PDF report from recent session."""
    if not api_client.is_logged_in() or not api_client.user_id:
        print_error("❌ Debes iniciar sesión para generar reportes: kr-cli login")
        return
        
    user_id = api_client.user_id
    
    with show_loading("Generando reporte ejecutivo..."):
        # 1. Fetch History
        history = get_chat_history(user_id, limit=20)
        if not history:
            print_error("No hay historial suficiente para generar un reporte.")
            return

        # 2. AI Summarization
        ai = AIHandler(user_id)
        session_data = ai.analyze_session_for_report(history)
        
        # Add raw log for appendix
        session_data['raw_log'] = history
        
        # 3. Generate PDF
        gen = ReportGenerator()
        pdf_path = gen.generate_report(session_data)
        
    print_success(f"Reporte generado exitosamente: {pdf_path}")
    # Try to open it
    # shutil.which('xdg-open') and subprocess.run(['xdg-open', pdf_path])

from .autonomous import run_autonomous_mode
from .audio import listen_and_execute

# ... (existing imports)

def main():
    """Entry point for kr-cli."""
    if len(sys.argv) < 2:
        print_info("Usage: kr-cli <command> [args...]")
        print_info("         kr-cli report")
        print_info("         kr-cli auto <target>")
        print_info("         kr-cli listen")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "report":
        handle_report()
    elif cmd == "auto":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        if not target:
            print_error("Target required: kr-cli auto <target>")
            return
        run_autonomous_mode(target)
    elif cmd == "listen":
        transcript = listen_and_execute()
        if transcript:
            print_info(f"⚡ Ejecutando comando de voz: {transcript}")
            # Simple assumption: transcript is a valid command string
            execute_and_analyze(transcript.split())
    else:
        execute_and_analyze(sys.argv[1:])

if __name__ == "__main__":
    main()
