"""Template installation for repositories."""

import shutil
from pathlib import Path

from .utils import fatal_error, print_error, print_info, print_success


def get_template_dir() -> Path:
    """Get the path to the template files.

    Returns:
        Path to templates/repo directory
    """
    # Try multiple locations
    candidates = [
        # Installed as package
        Path(__file__).parent.parent / "templates" / "repo",
        # Development layout
        Path(__file__).parent.parent / "templates" / "repo",
        # Alternate development layout
        Path(__file__).parent.parent.parent / "templates" / "repo",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    fatal_error("Template files not found. Ensure package is installed correctly.")


def init_repo(
    target_dir: str,
    force: bool = False,
    skip_workflow: bool = False,
    skip_runner: bool = False,
    skip_config: bool = False,
) -> int:
    """Install Claude-Linear templates to a repository.

    Args:
        target_dir: Path to the target repository
        force: Overwrite existing files
        skip_workflow: Don't install GitHub Actions workflow
        skip_runner: Don't install runner script
        skip_config: Don't install example config

    Returns:
        Number of files installed
    """
    target = Path(target_dir).resolve()

    if not target.exists():
        fatal_error(f"Directory does not exist: {target}")

    if not (target / ".git").exists():
        print_info("Warning: Target directory is not a git repository")

    template_dir = get_template_dir()

    print("\n" + "=" * 60)
    print("     Installing Claude-Linear Templates")
    print("=" * 60)
    print(f"\nTarget: {target}\n")

    installed = 0
    skipped = 0

    # Define files to install
    files_to_install: list[tuple[str, str, bool]] = []

    if not skip_workflow:
        files_to_install.append(
            (
                ".github/workflows/claude-linear.yml",
                ".github/workflows/claude-linear.yml",
                False,  # Create directories
            )
        )

    if not skip_runner:
        files_to_install.append(
            (
                "scripts/claude_linear_runner.py",
                "scripts/claude_linear_runner.py",
                False,
            )
        )

    if not skip_config:
        files_to_install.append(
            (
                ".claude/automation.yml",
                ".claude/automation.yml",
                True,  # This is an example config
            )
        )

    for src_rel, dst_rel, is_example in files_to_install:
        src_path = template_dir / src_rel
        dst_path = target / dst_rel

        if not src_path.exists():
            print_error(f"Template not found: {src_rel}")
            continue

        if dst_path.exists() and not force:
            print_info(f"'{dst_rel}' already exists (use --force to overwrite)")
            skipped += 1
            continue

        # Create parent directories
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(src_path, dst_path)

        if is_example:
            print_success(f"Created '{dst_rel}' (example config)")
        else:
            print_success(f"Installed '{dst_rel}'")
        installed += 1

    # Summary and next steps
    print("\n" + "=" * 60)
    if installed > 0:
        print_success(f"Installed {installed} file(s)")
    if skipped > 0:
        print_info(f"Skipped {skipped} existing file(s)")
    print("=" * 60)

    if installed > 0:
        print("""
Next steps:

1. Configure .claude/automation.yml for your project:
   - tests: Your test command (e.g., "pytest")
   - precommit: Your pre-commit command (if any)
   - browser_test: E2E test command (optional)

2. Add repository secrets in GitHub:
   Settings > Secrets > Actions:
   - ANTHROPIC_API_KEY: Your Anthropic API key
   - CLAUDE_AGENT_API_BASE: Your orchestrator URL
   - CLAUDE_AGENT_TOKEN: Your agent shared secret

3. Enable workflow permissions:
   Settings > Actions > General:
   - Enable "Allow GitHub Actions to create and approve pull requests"

4. Start automation:
   Add "Ready for Claude Code" label to any Linear issue!
""")

    return installed


def init_command(
    target_dir: str = ".",
    force: bool = False,
    skip_workflow: bool = False,
    skip_runner: bool = False,
    skip_config: bool = False,
) -> None:
    """Entry point for the init command.

    Args:
        target_dir: Path to the target repository
        force: Overwrite existing files
        skip_workflow: Don't install GitHub Actions workflow
        skip_runner: Don't install runner script
        skip_config: Don't install example config
    """
    init_repo(target_dir, force, skip_workflow, skip_runner, skip_config)
