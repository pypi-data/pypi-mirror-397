"""
Project management commands for IvyBloom CLI
"""

import click
import json
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ..utils.auth import AuthManager
from ..utils.config import Config
from ..client.api_client import IvyBloomAPIClient
from ..utils.printing import emit_json
from ..utils.colors import get_console

console = get_console()

@click.group()
def projects():
    """📁 Project organization and management
    
    Organize your computational jobs into projects for better workflow management.
    
    PROJECT BENEFITS:
      🗂️  Organization: Group related jobs together
      👥 Collaboration: Share projects with team members
      📊 Analytics: Track project-level progress and usage
      🔒 Access Control: Manage permissions per project
    
    COMMON WORKFLOWS:
    
      📋 View projects:        ivybloom projects list
      ℹ️  Project details:     ivybloom projects info <project_id>
      📊 Project jobs:         ivybloom projects jobs <project_id>
      🚀 Run job in project:   ivybloom run esmfold --project-id <id> [params...]
    
    PROJECT ORGANIZATION:
      • Drug Discovery Pipeline → esmfold, diffdock, admetlab3 jobs
      • Protein Analysis Study → blast, esmfold, structural analysis jobs  
      • Compound Optimization → reinvent, protox3, deepsol jobs
    
    💡 TIP: Use projects to keep your computational workflows organized!
    
    Run 'ivybloom projects <command> --help' for detailed help on each command.
    """
    pass

@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode with project selection')
@click.pass_context
def list(ctx, format, interactive):
    """📋 List all your projects
    
    View all projects you have access to, including job counts and activity.
    
    USAGE:
      ivybloom projects list                # Table view (default)
      ivybloom projects list --format json # JSON for automation
      ivybloom projects list --interactive  # Interactive selection mode
    
    PROJECT INFO SHOWN:
      • Project ID and name
      • Description and purpose
      • Number of jobs in project
      • Creation date
      • Last activity timestamp
    
    NEXT STEPS:
      • View project details:  ivybloom projects info <project_id>
      • See project jobs:      ivybloom projects jobs <project_id>
      • Add job to project:    ivybloom run <tool> --project-id <id>
    
    INTERACTIVE MODE:
      --interactive, -i  # Select projects with numbered selection for actions
    
    💡 TIP: Use --interactive to easily select projects and perform actions!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        # Ensure non-zero exit and stderr output so JSON consumers aren't polluted
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            projects_data = client.list_projects()
        
        if format == 'json':
            emit_json(projects_data)
        else:
            if not projects_data:
                console.print("[yellow]No projects found[/yellow]")
                return
            
            table = Table(title=f"📁 Projects ({len(projects_data)} found)")
            table.add_column("Project ID", style="cyan")
            table.add_column("Name", style="bold")
            table.add_column("Description", style="blue")
            table.add_column("Jobs", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Last Activity", style="dim")
            
            for project in projects_data:
                # Handle both project_id and id field names
                project_id = project.get('project_id') or project.get('id', '')
                description = project.get('description', '')[:30] + ('...' if len(project.get('description', '')) > 30 else '') if project.get('description') else 'No description'
                
                table.add_row(
                    str(project_id)[:8] + '...' if project_id else 'N/A',
                    project.get('name', 'Unnamed'),
                    description,
                    str(project.get('job_count', 0)),
                    project.get('created_at', '')[:10] if project.get('created_at') else 'Unknown',
                    project.get('last_activity', 'Never')[:10] if project.get('last_activity') else 'Never'
                )
            
            console.print(table)
            
            # Interactive mode - let user select a project
            if interactive:
                from ..utils.interactive import select_from_list, select_project_action
                
                # Prepare projects for selection
                project_items = []
                for project in projects_data:
                    project_id = project.get('project_id') or project.get('id', '')
                    project_name = project.get('name', 'Untitled')
                    description = project.get('description', '')
                    job_count = project.get('job_count', 0)
                    
                    desc_text = f"Jobs: {job_count}"
                    if description:
                        desc_text += f" | {description}"
                    
                    project_items.append({
                        'id': project_id,
                        'name': project_name,
                        'description': desc_text,
                        'project_data': project
                    })
                
                # Let user select a project
                selected_project_id = select_from_list(
                    items=project_items,
                    title="Select a Project",
                    display_key='name',
                    id_key='id',
                    description_key='description'
                )
                
                if selected_project_id:
                    # Find the selected project data
                    selected_project_data = None
                    for item in project_items:
                        if item['id'] == selected_project_id:
                            selected_project_data = item['project_data']
                            break
                    
                    if selected_project_data:
                        # Let user select an action
                        action = select_project_action(selected_project_data)
                        
                        if action:
                            _execute_project_action(ctx, selected_project_id, action, selected_project_data)
    
    except Exception as e:
        # Provide actionable, user-friendly error messages
        msg = str(e)
        hints = []
        if "Not authenticated" in msg or "Authentication" in msg or "401" in msg:
            hints.append("Run 'ivybloom auth status' to verify login and API key")
            hints.append("If needed, run 'ivybloom auth login --link' to relink this CLI")
        if "Unexpected response" in msg:
            hints.append("The server returned an unexpected format. Try again in a moment")
            hints.append("Run with --debug for request/response details")
        if "timeout" in msg.lower():
            hints.append("Network timeout. Check your connection and try again")
        if not hints:
            hints.append("Re-run with '--debug' to see request/response diagnostics")
        hint_text = "\n".join(f"   • {h}" for h in hints)
        raise click.ClickException(f"Error listing projects: {msg}\n\nTroubleshooting:\n{hint_text}")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def info(ctx, project_id, format):
    """ℹ️  Get detailed project information
    
    View comprehensive details about a specific project including metadata,
    job statistics, and recent activity.
    
    USAGE:
      ivybloom projects info <project_id>           # Detailed view
      ivybloom projects info <project_id> --format json  # JSON output
    
    PROJECT DETAILS SHOWN:
      • Project metadata (name, description, dates)
      • Job statistics (total, by status, by tool)
      • Recent activity and usage patterns
      • Team members and permissions (if applicable)
      • Resource usage and costs (if available)
    
    RELATED COMMANDS:
      • View project jobs:     ivybloom projects jobs <project_id>
      • Filter global jobs:    ivybloom jobs list --project-id <project_id>
    
    💡 TIP: Use this to understand project scope and activity before diving in!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            project_data = client.get_project(project_id)
        
        if format == 'json':
            emit_json(project_data)
        else:
            # Handle both project_id and id field names
            project_id = project_data.get('project_id') or project_data.get('id', 'Unknown')
            
            console.print(f"[bold cyan]📁 {project_data.get('name', 'Unnamed Project')}[/bold cyan]")
            console.print(f"   Project ID: {project_id}")
            console.print(f"   Description: {project_data.get('description', 'No description')}")
            console.print(f"   Created: {project_data.get('created_at', 'Unknown')}")
            console.print(f"   Updated: {project_data.get('updated_at', 'Unknown')}")
            console.print(f"   Jobs: {project_data.get('job_count', 0)}")
            console.print(f"   Last Activity: {project_data.get('last_activity', 'Never')}")
    
    except Exception as e:
        raise click.ClickException(f"Error getting project info: {e}")

@projects.command()
@click.argument('project_id')
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def jobs(ctx, project_id, format):
    """📊 List all jobs in a specific project
    
    View all computational jobs associated with a particular project,
    showing status, progress, and results.
    
    USAGE:
      ivybloom projects jobs <project_id>              # Project job list
      ivybloom projects jobs <project_id> --format json  # JSON output
    
    JOB INFORMATION SHOWN:
      • Job ID and title
      • Tool/algorithm used  
      • Current status and progress
      • Creation and completion times
      • Links to detailed status and results
    
    PROJECT WORKFLOW:
      1. List project jobs:    ivybloom projects jobs <project_id>
      2. Check job status:     ivybloom jobs status <job_id> --stream
      3. Get results:          ivybloom jobs results <job_id>
      4. Add more jobs:        ivybloom run <tool> --project-id <project_id>
    
    💡 TIP: This gives you a project-focused view of your computational pipeline!
    """
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        with IvyBloomAPIClient(config, auth_manager) as client:
            jobs_data = client.list_project_jobs(project_id)
        
        if format == 'json':
            emit_json(jobs_data)
        else:
            if not jobs_data:
                console.print(f"[yellow]No jobs found for project {project_id}[/yellow]")
                return
            
            table = Table(title=f"📋 Project Jobs ({len(jobs_data)} found)")
            table.add_column("Job ID", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Tool", style="green")
            table.add_column("Created", style="dim")
            
            for job in jobs_data:
                # Map database status values to display values (same as in jobs.py)
                status_display = {
                    'COMPLETED': '[green]COMPLETED[/green]',
                    'SUCCESS': '[green]SUCCESS[/green]',
                    'PROCESSING': '[blue]PROCESSING[/blue]',
                    'STARTED': '[blue]RUNNING[/blue]',
                    'FAILURE': '[red]FAILED[/red]',
                    'failed': '[red]FAILED[/red]',
                    'PENDING': '[yellow]PENDING[/yellow]',
                    'submitted': '[yellow]SUBMITTED[/yellow]',
                    'CANCELLED': '[dim]CANCELLED[/dim]',
                    'ARCHIVED': '[dim]ARCHIVED[/dim]'
                }.get(job.get('status', ''), job.get('status', ''))
                
                # Handle both job_id and id field names
                job_id = job.get('job_id') or job.get('id', '')
                
                table.add_row(
                    str(job_id)[:8] + '...' if job_id else 'N/A',
                    status_display,
                    job.get('job_type', ''),  # Use job_type instead of tool_name
                    job.get('created_at', '')[:16] if job.get('created_at') else ''
                )
            
            console.print(table)
    
    except Exception as e:
        raise click.ClickException(f"Error listing project jobs: {e}")

def _execute_project_action(ctx, project_id: str, action: str, project_data: Dict[str, Any]):
    """Execute the selected action on a project"""
    try:
        if action == 'info':
            # Show project info
            info(ctx, project_id, 'table')
            
        elif action == 'jobs':
            # Show project jobs
            jobs(ctx, project_id, 'table')
            
        elif action == 'create_job':
            # Help user create a job in this project
            from ..utils.interactive import select_from_list
            
            # Show available tools (simplified)
            console.print(f"\n[cyan]Creating a job in project {project_id}...[/cyan]")
            console.print("First, choose a computational tool:")
            console.print()
            
            # Common tools for quick selection
            common_tools = [
                {'id': 'esmfold', 'name': 'ESMFold', 'description': 'Protein structure prediction (5 min)'},
                {'id': 'diffdock', 'name': 'DiffDock', 'description': 'Molecular docking (30 min)'},
                {'id': 'reinvent', 'name': 'REINVENT', 'description': 'Drug design (1 hour)'},
                {'id': 'admetlab3', 'name': 'ADMETLab3', 'description': 'ADMET analysis (10 min)'},
                {'id': 'blast', 'name': 'BLAST', 'description': 'Sequence search (2 min)'},
                {'id': 'other', 'name': 'Other Tool', 'description': 'See all available tools'}
            ]
            
            selected_tool = select_from_list(
                items=common_tools,
                title="Select a Tool",
                display_key='name',
                id_key='id',
                description_key='description'
            )
            
            if selected_tool:
                if selected_tool == 'other':
                    console.print("\n[cyan]💡 To see all available tools:[/cyan]")
                    console.print("   ivybloom tools list")
                    console.print("\n[cyan]💡 To run any tool in this project:[/cyan]")
                    console.print(f"   ivybloom run <tool_name> --project-id {project_id} [parameters...]")
                else:
                    console.print(f"\n[cyan]💡 To run {selected_tool} in this project:[/cyan]")
                    console.print(f"   ivybloom run {selected_tool} --project-id {project_id} [parameters...]")
                    console.print(f"\n[cyan]💡 To see {selected_tool} parameters:[/cyan]")
                    console.print(f"   ivybloom tools schema {selected_tool} --examples")
                
    except Exception as e:
        console.print(f"[red]❌ Error executing action '{action}': {e}[/red]")


@projects.command()
@click.option('--project-id', help='Project ID (skip prompts if provided)')
@click.option('--directory', '-d', help='Local directory path')
@click.option('--interactive', '-i', is_flag=True, default=True, help='Interactive mode')
@click.option('--ui-mode', type=click.Choice(['auto', 'basic', 'enhanced', 'charm']), 
              help='Override UI mode for this command')
@click.pass_context
def init(ctx, project_id, directory, interactive, ui_mode):
    """🔗 Initialize project linking for local sync
    
    Link a remote IvyBloom project to a local directory for seamless syncing.
    
    USAGE:
      ivybloom projects init                    # Interactive setup (recommended)
      ivybloom projects init --project-id <id> --directory /path  # Non-interactive
      ivybloom projects init --ui-mode basic    # Override UI mode
    
    INTERACTIVE SETUP:
      • Choose to link existing project or create new
      • Select project from your available projects
      • Choose local directory
      • Configure sync settings (jobs, artifacts, auto-sync frequency)
    
    UI MODES:
      • basic: Traditional Click prompts (backward compatible)
      • enhanced: Beautiful Clack prompts (requires: pip install clack)
      • charm: Advanced Charm tools (requires: gum CLI)
      • auto: Auto-detect (default)
    
    WHAT GETS CREATED:
      • .ivybloom/ directory (project manifest and metadata)
      • .ivybloom/manifest.json (link configuration)
      • .ivybloom/cache/ (local job and artifact cache)
      • .ivybloom/sync_log.jsonl (sync history)
    
    NEXT STEPS:
      • Sync from cloud:  ivybloom projects pull
      • Sync to cloud:    ivybloom projects push
      • Check status:     ivybloom projects status
      • View changes:     ivybloom projects diff
    
    💡 TIP: Run 'ivybloom projects init' to get started with interactive setup!
    """
    from pathlib import Path
    from datetime import datetime
    from ..utils.project_linking import LocalProjectManifest
    from ..utils.colors import print_success, print_error
    from ..utils.ui_mode import UIContextManager, UIModeDetector
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        # Initialize UI context with override if provided
        ui_context = UIContextManager()
        if ui_mode:
            from ..utils.ui_mode import UIMode
            ui_context.mode = UIModeDetector.get_effective_mode(UIMode(ui_mode))
        
        with IvyBloomAPIClient(config, auth_manager) as client:
            # Non-interactive mode: use provided parameters
            if project_id and directory:
                project_path = Path(directory).resolve()
                
                # Create manifest
                manifest = LocalProjectManifest(
                    version="1.0.0",
                    project_id=project_id,
                    project_name=f"Project {project_id}",
                    linked_at=datetime.now().isoformat(),
                    linked_path=str(project_path),
                    include_jobs=True,
                    include_artifacts=True,
                    auto_sync="manual"
                )
                
                # Save manifest
                ivybloom_dir = project_path / ".ivybloom"
                manifest.save(ivybloom_dir)
                
                print_success(f"✅ Project linked: {manifest.project_name}")
                console.print(f"   Location: {project_path}")
                console.print(f"   Manifest: {ivybloom_dir / 'manifest.json'}")
            
            elif interactive:
                # Show UI mode info
                ui_context.show_mode_info()
                console.print("\n[bold cyan]🔗 Project Linking Setup[/bold cyan]")
                console.print()
                
                # Fetch projects
                projects_list = client.list_projects()
                if not projects_list:
                    print_error("No projects found. Create one in the web app first.")
                    return
                
                # Step 1: Select project (with UI mode support)
                selected_project = _select_project_interactive(
                    console, projects_list, ui_context
                )
                if not selected_project:
                    return
                
                # Step 2: Select directory
                project_path = _select_directory_interactive(console, ui_context)
                if not project_path:
                    return
                
                # Step 3: Configure options
                config_opts = _configure_options_interactive(console, ui_context)
                
                # Step 4: Create manifest
                manifest = LocalProjectManifest(
                    version="1.0.0",
                    project_id=selected_project.get('id'),
                    project_name=selected_project.get('name', 'Unnamed'),
                    linked_at=datetime.now().isoformat(),
                    linked_path=str(project_path),
                    include_jobs=config_opts.get('include_jobs', True),
                    include_artifacts=config_opts.get('include_artifacts', True),
                    auto_sync=config_opts.get('auto_sync', 'manual')
                )
                
                # Save manifest
                ivybloom_dir = project_path / ".ivybloom"
                manifest.save(ivybloom_dir)
                
                # Create cache directories
                (ivybloom_dir / "cache").mkdir(exist_ok=True)
                
                print_success(f"\n✅ Project linked successfully!")
                console.print(f"   Project: {manifest.project_name}")
                console.print(f"   Location: {project_path}")
                console.print(f"   Manifest: {ivybloom_dir / 'manifest.json'}")
                console.print()
                console.print("[cyan]Next steps:[/cyan]")
                console.print(f"  1. cd {project_path}")
                console.print("  2. ivybloom projects pull    # Sync from cloud")
                console.print("  3. ivybloom projects status   # Check sync state")
            else:
                print_error("Use --interactive or provide --project-id and --directory")
    
    except FileNotFoundError as e:
        raise click.ClickException(f"Invalid directory: {e}")
    except Exception as e:
        raise click.ClickException(f"Error initializing project: {e}")


def _select_project_interactive(console: Console, projects_list, ui_context) -> Optional[Dict]:
    """Select project using appropriate UI mode.

    Args:
        console: Rich Console instance
        projects_list: List of projects
        ui_context: UI context manager

    Returns:
        Selected project dict or None
    """
    if ui_context.use_clack():
        # Use Clack for beautiful prompts
        from ..utils.ui_styling import ClackPromptBuilder
        
        try:
            builder = ClackPromptBuilder(console)
            choices = [
                {
                    "name": f"{p.get('name', 'Unnamed')} ({p.get('job_count', 0)} jobs)",
                    "value": p.get('id', '')
                }
                for p in projects_list
            ]
            selected_id = builder.build_select_prompt(
                "Select a project to link",
                choices
            )
            return next((p for p in projects_list if p.get('id') == selected_id), None)
        except ImportError:
            # Fallback to basic mode
            console.print("[yellow]Clack not available, using basic prompts[/yellow]")
            return _select_project_basic(console, projects_list)
    else:
        # Use basic Click prompts
        return _select_project_basic(console, projects_list)


def _select_project_basic(console: Console, projects_list) -> Optional[Dict]:
    """Select project using basic Click prompts.

    Args:
        console: Rich Console instance
        projects_list: List of projects

    Returns:
        Selected project dict or None
    """
    from ..utils.interactive import select_from_list
    
    project_items = []
    for proj in projects_list:
        proj_id = proj.get('project_id') or proj.get('id', '')
        proj_name = proj.get('name', 'Unnamed')
        proj_desc = proj.get('description', '')
        job_count = proj.get('job_count', 0)
        
        desc_text = f"Jobs: {job_count}"
        if proj_desc:
            desc_text += f" | {proj_desc}"
        
        project_items.append({
            'id': proj_id,
            'name': proj_name,
            'description': desc_text,
            'project': proj
        })
    
    selected_id = select_from_list(
        items=project_items,
        title="Select a Project to Link",
        display_key='name',
        id_key='id',
        description_key='description'
    )
    
    if not selected_id:
        return None
    
    return next((p['project'] for p in project_items if p['id'] == selected_id), None)


def _select_directory_interactive(console: Console, ui_context) -> Optional[Path]:
    """Select directory using appropriate UI mode.

    Args:
        console: Rich Console instance
        ui_context: UI context manager

    Returns:
        Selected directory Path or None
    """
    from pathlib import Path as PathlibPath
    
    console.print("\n[cyan]Where should this project be linked?[/cyan]")
    default_dir = str(PathlibPath.cwd())
    
    if ui_context.use_clack():
        # Use Clack for text input
        from ..utils.ui_styling import ClackPromptBuilder
        
        try:
            builder = ClackPromptBuilder(console)
            # Note: build_text_prompt is a stub, so we'll use basic for now
            directory = click.prompt("Enter directory path", default=default_dir)
        except Exception:
            directory = click.prompt("Enter directory path", default=default_dir)
    else:
        directory = click.prompt("Enter directory path", default=default_dir)
    
    project_path = PathlibPath(directory).expanduser().resolve()
    
    # Create directory if needed
    try:
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Check if directory is empty
        if project_path.exists() and list(project_path.iterdir()):
            if not click.confirm("Directory is not empty. Continue anyway?"):
                return None
        
        return project_path
    except Exception as e:
        print_error(f"Invalid directory: {e}")
        return None


def _configure_options_interactive(console: Console, ui_context) -> Dict[str, Any]:
    """Configure sync options using appropriate UI mode.

    Args:
        console: Rich Console instance
        ui_context: UI context manager

    Returns:
        Configuration options dict
    """
    console.print("\n[cyan]Configure sync options[/cyan]")
    
    config = {}
    
    if ui_context.use_clack():
        # Use Clack for confirmations
        from ..utils.ui_styling import ClackPromptBuilder
        
        try:
            builder = ClackPromptBuilder(console)
            config["include_jobs"] = builder.build_confirm_prompt(
                "Include job histories in sync?",
                default=True
            )
            config["include_artifacts"] = builder.build_confirm_prompt(
                "Include artifacts in sync?",
                default=True
            )
        except ImportError:
            # Fallback to basic
            config["include_jobs"] = click.confirm("Include job histories?", default=True)
            config["include_artifacts"] = click.confirm("Include artifacts?", default=True)
    else:
        # Use basic Click prompts
        config["include_jobs"] = click.confirm("Include job histories?", default=True)
        config["include_artifacts"] = click.confirm("Include artifacts?", default=True)
    
    # Auto-sync frequency (basic for now)
    auto_sync_options = ["manual", "15min", "hourly"]
    console.print("\n[cyan]Auto-sync frequency:[/cyan]")
    for i, option in enumerate(auto_sync_options, 1):
        console.print(f"  [{i}] {option}")
    
    choice = click.prompt("Select frequency", type=int, default=1)
    config["auto_sync"] = auto_sync_options[choice - 1] if 1 <= choice <= 3 else "manual"
    
    return config


@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def pull(ctx, format):
    """⬇️  Sync from cloud to local
    
    Download the latest jobs, artifacts, and metadata from the cloud.
    
    USAGE:
      ivybloom projects pull              # Interactive (prompts for directory)
      ivybloom projects pull --format json  # JSON output for automation
    
    WHAT HAPPENS:
      • Compares local .ivybloom manifest with remote state
      • Downloads new jobs and artifacts
      • Updates local manifest
      • Detects conflicts if both sides changed
    
    CONFLICTS:
      If changes conflict, you'll be prompted to:
      • Keep local version
      • Use remote version
      • Abort and resolve manually
    
    PERFORMANCE:
      • Fast for small projects (<1GB)
      • Uses smart caching (only downloads what's new)
      • Bandwidth aware (can throttle if needed)
    
    RELATED COMMANDS:
      • Check status:     ivybloom projects status
      • View changes:     ivybloom projects diff
      • Sync to cloud:    ivybloom projects push
    
    💡 TIP: Run this regularly to stay in sync with your team!
    """
    from pathlib import Path
    from ..utils.project_linking import LocalProjectManifest, LocalProjectSync
    from ..utils.colors import print_success, print_warning, print_error
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        # Find .ivybloom manifest in current directory
        manifest_path = Path(".ivybloom")
        if not manifest_path.exists():
            raise FileNotFoundError(
                "No .ivybloom directory found. "
                "Run 'ivybloom projects init' to link a project."
            )
        
        # Load manifest
        manifest = LocalProjectManifest.load(manifest_path)
        
        # Create sync manager
        with IvyBloomAPIClient(config, auth_manager) as client:
            sync = LocalProjectSync(manifest, client, config, console)
            
            # Perform pull
            console.print("[cyan]⏳ Syncing from cloud...[/cyan]")
            import asyncio
            result = asyncio.run(sync.pull())
            
            if result.success:
                print_success(f"✅ {result.summary}")
                
                if result.changes:
                    console.print("\n[cyan]Changes synced:[/cyan]")
                    for change in result.changes:
                        emoji = {
                            "added": "✨",
                            "modified": "🔄",
                            "deleted": "🗑️ "
                        }.get(change.change_type, "•")
                        console.print(
                            f"  {emoji} {change.resource_type}: "
                            f"{change.resource_id[:20]}..."
                        )
            else:
                print_warning(f"⚠️  {result.summary}")
                for error in result.errors:
                    console.print(f"  [red]Error: {error}[/red]")
            
            if format == 'json':
                emit_json(result.__dict__)
    
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error during pull: {e}")


@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def push(ctx, format):
    """⬆️  Sync from local to cloud
    
    Upload local changes to the cloud.
    
    USAGE:
      ivybloom projects push              # Interactive confirmation
      ivybloom projects push --format json  # JSON output
    
    WHAT HAPPENS:
      • Uploads modified/new artifacts
      • Updates remote metadata
      • Records changes in audit log
      • Updates local manifest
    
    SAFETY FEATURES:
      • Preview changes first with 'ivybloom projects diff'
      • Conflict detection prevents data loss
      • Automatic backups on remote
      • Audit trail of all changes
    
    RELATED COMMANDS:
      • Preview changes: ivybloom projects diff
      • Sync from cloud: ivybloom projects pull
      • Check status:    ivybloom projects status
    
    💡 TIP: Always run 'pull' first to avoid conflicts!
    """
    from pathlib import Path
    from ..utils.project_linking import LocalProjectManifest, LocalProjectSync
    from ..utils.colors import print_success, print_warning, print_error
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        # Find .ivybloom manifest
        manifest_path = Path(".ivybloom")
        if not manifest_path.exists():
            raise FileNotFoundError(
                "No .ivybloom directory found. "
                "Run 'ivybloom projects init' to link a project."
            )
        
        # Load manifest
        manifest = LocalProjectManifest.load(manifest_path)
        
        # Create sync manager
        with IvyBloomAPIClient(config, auth_manager) as client:
            sync = LocalProjectSync(manifest, client, config, console)
            
            # Preview changes
            import asyncio
            diff = asyncio.run(sync.compute_diff())
            
            if not diff.get("modified") and not diff.get("added"):
                console.print("[yellow]ℹ️  No changes to push[/yellow]")
                return
            
            # Show preview
            console.print("[cyan]Changes to push:[/cyan]")
            for item in diff.get("added", []) + diff.get("modified", []):
                emoji = "✨" if item.get("type") == "added" else "🔄"
                console.print(f"  {emoji} {item.get('type')}: {item.get('id')[:20]}...")
            
            # Ask for confirmation
            if not click.confirm("\nProceed with push?", default=True):
                console.print("[yellow]Push cancelled[/yellow]")
                return
            
            # Perform push
            console.print("[cyan]⏳ Uploading to cloud...[/cyan]")
            result = asyncio.run(sync.push())
            
            if result.success:
                print_success(f"✅ {result.summary}")
            else:
                print_warning(f"⚠️  {result.summary}")
                for error in result.errors:
                    console.print(f"  [red]Error: {error}[/red]")
            
            if format == 'json':
                emit_json(result.__dict__)
    
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error during push: {e}")


@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def status(ctx, format):
    """📊 Check project sync status
    
    View the current sync state and history.
    
    USAGE:
      ivybloom projects status              # Detailed status
      ivybloom projects status --format json  # JSON output
    
    DISPLAYS:
      • Current sync state (new, synced, dirty, error)
      • Last sync time and type
      • Job and artifact counts
      • Recent sync history (last 5 operations)
      • Any pending conflicts
    
    STATES EXPLAINED:
      • new: Never synced
      • synced: In sync with remote
      • dirty: Local changes not synced
      • error: Last sync failed
    
    RELATED COMMANDS:
      • Sync from cloud: ivybloom projects pull
      • Sync to cloud:   ivybloom projects push
      • View changes:    ivybloom projects diff
    
    💡 TIP: Use status to monitor your project's sync state!
    """
    from pathlib import Path
    from ..utils.project_linking import LocalProjectManifest
    from ..utils.colors import print_success, print_warning, print_error
    from rich.table import Table
    
    try:
        # Find .ivybloom manifest
        manifest_path = Path(".ivybloom")
        if not manifest_path.exists():
            raise FileNotFoundError(
                "No .ivybloom directory found. "
                "Run 'ivybloom projects init' to link a project."
            )
        
        # Load manifest
        manifest = LocalProjectManifest.load(manifest_path)
        
        if format == 'json':
            emit_json(manifest.to_dict())
        else:
            # Display status
            status_emoji = {
                "new": "✨",
                "synced": "✅",
                "dirty": "🔄",
                "error": "❌"
            }.get(manifest.sync_status, "❓")
            
            console.print(f"[bold cyan]📊 Project Sync Status[/bold cyan]")
            console.print(f"   Status: {status_emoji} {manifest.sync_status.upper()}")
            console.print(f"   Project: {manifest.project_name}")
            console.print(f"   Directory: {manifest.linked_path}")
            
            if manifest.last_sync_time:
                console.print(f"   Last sync: {manifest.last_sync_time} ({manifest.last_sync_type})")
            
            console.print(f"   Include jobs: {manifest.include_jobs}")
            console.print(f"   Include artifacts: {manifest.include_artifacts}")
            
            if manifest.last_error:
                console.print(f"   [red]Last error: {manifest.last_error}[/red]")
            
            # Show sync history
            sync_log = manifest_path / "sync_log.jsonl"
            if sync_log.exists():
                console.print(f"\n[cyan]Recent syncs:[/cyan]")
                with open(sync_log) as f:
                    lines = f.readlines()[-5:]  # Last 5 syncs
                    for line in reversed(lines):
                        import json as json_module
                        try:
                            entry = json_module.loads(line)
                            console.print(
                                f"  • {entry.get('timestamp', 'N/A')}: "
                                f"{entry.get('type', 'unknown').upper()} "
                                f"({entry.get('status', 'unknown')})"
                            )
                        except:
                            pass
    
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error getting status: {e}")


@projects.command()
@click.option('--format', default='table', type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def diff(ctx, format):
    """🔍 Preview changes to sync
    
    Show what would be synced without actually syncing.
    
    USAGE:
      ivybloom projects diff              # Show pending changes
      ivybloom projects diff --format json  # JSON output
    
    DISPLAYS:
      • New items (not yet downloaded/uploaded)
      • Modified items (changed locally or remotely)
      • Deleted items (removed from local or remote)
    
    USE CASES:
      • Review before pushing changes
      • Diagnose sync conflicts
      • Understand data flow
      • Plan sync strategy
    
    RELATED COMMANDS:
      • Sync from cloud: ivybloom projects pull
      • Sync to cloud:   ivybloom projects push
      • Check status:    ivybloom projects status
    
    💡 TIP: Always check diff before push!
    """
    from pathlib import Path
    from ..utils.project_linking import LocalProjectManifest, LocalProjectSync
    from ..utils.colors import print_success, print_warning
    from rich.table import Table
    
    config = ctx.obj['config']
    auth_manager = AuthManager(config)
    
    if not auth_manager.is_authenticated():
        raise click.ClickException("Not authenticated. Run 'ivybloom auth login' first.")
    
    try:
        # Find .ivybloom manifest
        manifest_path = Path(".ivybloom")
        if not manifest_path.exists():
            raise FileNotFoundError(
                "No .ivybloom directory found. "
                "Run 'ivybloom projects init' to link a project."
            )
        
        # Load manifest
        manifest = LocalProjectManifest.load(manifest_path)
        
        # Create sync manager
        with IvyBloomAPIClient(config, auth_manager) as client:
            sync = LocalProjectSync(manifest, client, config, console)
            
            # Compute diff
            import asyncio
            diff = asyncio.run(sync.compute_diff())
            
            if format == 'json':
                emit_json(diff)
            else:
                # Display diff
                if not diff.get("added") and not diff.get("modified") and not diff.get("deleted"):
                    console.print("[green]✅ Everything is synced![/green]")
                    return
                
                console.print("[bold cyan]🔍 Changes to Sync[/bold cyan]\n")
                
                if diff.get("added"):
                    console.print("[cyan]New (will be added):[/cyan]")
                    for item in diff["added"]:
                        console.print(f"  ✨ {item.get('type')}: {item.get('id')}")
                
                if diff.get("modified"):
                    console.print("\n[cyan]Modified (will be updated):[/cyan]")
                    for item in diff["modified"]:
                        console.print(f"  🔄 {item.get('type')}: {item.get('id')}")
                
                if diff.get("deleted"):
                    console.print("\n[cyan]Deleted (will be removed):[/cyan]")
                    for item in diff["deleted"]:
                        console.print(f"  🗑️  {item.get('type')}: {item.get('id')}")
    
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error computing diff: {e}")