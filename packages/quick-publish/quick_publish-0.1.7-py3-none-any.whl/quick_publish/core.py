"""Core publishing functionality."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .changelog import ChangelogGenerator
from .exceptions import QuickPublishError
from .git import GitManager
from .version import VersionManager

console = Console()


class Publisher:
    """Main publisher class that orchestrates the release process."""

    def __init__(self, working_dir: Path, verbose: bool = False) -> None:
        self.working_dir = working_dir
        self.verbose = verbose
        self.console = Console()

        # Initialize managers
        self.version_manager = VersionManager(working_dir)
        self.git_manager = GitManager(working_dir)
        self.changelog_generator = ChangelogGenerator(working_dir)

    def publish(
        self,
        generate_depcost: bool = False,
        push_to_remote: bool = True,
        dry_run: bool = False,
        version_override: str | None = None,
    ) -> None:
        """Execute the complete publishing workflow."""
        self._print_header("🚀 Quick Publish - Python Package Release Tool")
        
        if dry_run:
            self._print_warning("🧪 DRY RUN MODE - No actual changes will be made")

        # Step 1: Ensure clean git state
        self._step_1_check_git_state(dry_run)

        # Step 2: Get and select version
        current_version, new_version = self._step_2_handle_version(version_override, dry_run)

        # Step 3: Check for existing tag
        self._step_3_check_tag(new_version, dry_run)

        if not dry_run:
            # Step 4: Update version and changelog
            self._step_4_update_files(new_version)

            # Step 5: Commit changes
            self._step_5_commit_changes(new_version)

            # Step 6: Create git tag
            self._step_6_create_tag(new_version)

            # Step 7: Push to remote
            if push_to_remote:
                self._step_7_push_to_remote()

            # Step 8: Build package
            self._step_8_build_package()

            # Step 9: Upload to PyPI
            self._step_9_upload_to_pypi(new_version)

            self._print_success(f"✅ Successfully released v{new_version} to PyPI!")
        else:
            self._print_dry_run_summary(current_version, new_version, push_to_remote)

    def _step_1_check_git_state(self, dry_run: bool) -> None:
        """Step 1: Check git repository state."""
        self._print_step(1, "Checking Git Repository State")
        
        if not dry_run:
            try:
                self.git_manager.ensure_clean_working_tree()
                self._print_success("✓ Clean working tree")
            except QuickPublishError as e:
                self._print_error(f"✗ Git state check failed: {e}")
                raise
        else:
            self._print_info("[DRY RUN] Would check working tree is clean")

    def _step_2_handle_version(self, version_override: str | None, dry_run: bool) -> tuple[str, str]:
        """Step 2: Handle version selection."""
        self._print_step(2, "Version Management")
        
        # Get current version
        current_version = self.version_manager.get_current_version()
        self._print_info(f"Current version: {current_version}")

        # Select new version
        new_version = self.version_manager.select_version(
            current_version, version_override
        )
        self._print_info(f"Selected version: {new_version}")

        if new_version <= current_version:
            raise QuickPublishError(
                f"New version {new_version} must be greater than current {current_version}"
            )

        return current_version, new_version

    def _step_3_check_tag(self, new_version: str, dry_run: bool) -> None:
        """Step 3: Check if tag already exists."""
        self._print_step(3, "Checking Git Tag")
        
        tag_name = f"v{new_version}"
        if self.git_manager.tag_exists(tag_name):
            raise QuickPublishError(f"Tag {tag_name} already exists")
        
        self._print_success(f"✓ Tag {tag_name} is available")

    def _step_4_update_files(self, new_version: str) -> None:
        """Step 4: Update version and changelog files."""
        self._print_step(4, "Updating Project Files")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Update version in pyproject.toml
            task1 = progress.add_task("Updating pyproject.toml...", total=1)
            self.version_manager.update_version(new_version)
            progress.update(task1, advance=1)
            
            # Update changelog
            task2 = progress.add_task("Updating CHANGELOG.md...", total=1)
            self.changelog_generator.update_changelog(str(new_version))
            progress.update(task2, advance=1)

        self._print_success("✓ Project files updated")

    def _step_5_commit_changes(self, new_version: str) -> None:
        """Step 5: Commit version and changelog changes."""
        self._print_step(5, "Committing Changes")
        
        commit_message = f"chore: release v{new_version}"
        files_to_commit = ["pyproject.toml", "CHANGELOG.md"]
        
        try:
            self.git_manager.add_and_commit(files_to_commit, commit_message)
            self._print_success(f"✓ Committed: {commit_message}")
        except QuickPublishError as e:
            self._print_error(f"✗ Commit failed: {e}")
            raise

    def _step_6_create_tag(self, new_version: str) -> None:
        """Step 6: Create git tag."""
        self._print_step(6, "Creating Git Tag")
        
        tag_name = f"v{new_version}"
        tag_message = f"Release {new_version}"
        
        try:
            self.git_manager.create_tag(tag_name, tag_message)
            self._print_success(f"✓ Created tag: {tag_name}")
        except QuickPublishError as e:
            self._print_error(f"✗ Tag creation failed: {e}")
            raise

    def _step_7_push_to_remote(self) -> None:
        """Step 7: Push commits and tags to remote."""
        self._print_step(7, "Pushing to Remote Repository")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Pushing commits and tags...", total=1)
                self.git_manager.push_to_remote(push_tags=True)
                progress.update(task, advance=1)
            
            self._print_success("✓ Pushed to remote repository")
        except QuickPublishError as e:
            self._print_error(f"✗ Push failed: {e}")
            raise

    def _step_8_build_package(self) -> None:
        """Step 8: Build the package for distribution using uv build."""
        self._print_step(8, "Building Package")
        
        try:
            # Check for uv command
            try:
                subprocess.run(["uv", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise QuickPublishError(
                    "uv not found. Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
                )

            # Clean dist directory first
            dist_dir = self.working_dir / "dist"
            if dist_dir.exists():
                import shutil
                shutil.rmtree(dist_dir)
                self._print_info("Cleaned existing dist/ directory")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Building wheel and source distribution...", total=1)
                
                result = subprocess.run(
                    ["uv", "build"],
                    cwd=self.working_dir,
                    capture_output=False,  # Show real-time output
                    text=True,
                )

                if result.returncode != 0:
                    self._print_error("Build failed")
                    raise QuickPublishError("Build failed")

                progress.update(task, advance=1)

            # List built files (only include actual package files)
            if dist_dir.exists():
                built_files = [f for f in dist_dir.glob("*") if f.suffix in ['.whl', '.tar.gz']]
                self._print_success(f"✓ Built {len(built_files)} files:")
                for file in built_files:
                    file_size = file.stat().st_size
                    self._print_info(f"  📦 {file.name} ({file_size:,} bytes)")

        except subprocess.SubprocessError as e:
            raise QuickPublishError(f"Build process failed: {e}")

    def _step_9_upload_to_pypi(self, new_version: str) -> None:
        """Step 9: Upload package to PyPI using uv publish."""
        self._print_step(9, "Uploading to PyPI")
        
        try:
            dist_dir = self.working_dir / "dist"
            package_files = [f for f in dist_dir.glob("*") if f.suffix in ['.whl', '.tar.gz']]
            
            if not package_files:
                raise QuickPublishError("No package files found to upload")

            self._print_info(f"Found {len(package_files)} package files to upload")
            for file in package_files:
                file_size = file.stat().st_size
                self._print_info(f"  📦 {file.name} ({file_size:,} bytes)")

            # Check for uv command
            try:
                subprocess.run(["uv", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise QuickPublishError(
                    "uv not found. Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
                )

            # Check for PyPI authentication
            self._print_info("Checking PyPI authentication...")
            
            has_test_token = "UV_TEST_PUBLISH_TOKEN" in __import__("os").environ or "UV_TEST_PUBLISH_PASSWORD" in __import__("os").environ
            has_prod_token = "UV_PUBLISH_TOKEN" in __import__("os").environ or "UV_PUBLISH_PASSWORD" in __import__("os").environ
            
            if not has_prod_token and not has_test_token:
                self._print_warning("No PyPI tokens found in environment variables")
                self._print_info("Expected environment variables:")
                self._print_info("  UV_PUBLISH_TOKEN - for production PyPI")
                self._print_info("  UV_TEST_PUBLISH_TOKEN - for test PyPI")
                self._print_info("Will attempt upload with interactive authentication")

            # Try to upload to production PyPI first if token is available
            if has_prod_token:
                self._print_info("Attempting upload to production PyPI...")
                
                publish_cmd = ["uv", "publish"] + [str(f) for f in package_files]
                
                try:
                    result = subprocess.run(
                        publish_cmd,
                        cwd=self.working_dir,
                        capture_output=False,  # Show real-time output
                        text=True,
                        timeout=300,  # 5 minute timeout
                    )

                    if result.returncode == 0:
                        self._print_success("✓ Uploaded to PyPI")
                        self._print_info(f"🔗 PyPI: https://pypi.org/project/quick-publish/{new_version}/")
                        return
                    else:
                        self._print_warning("Production PyPI upload failed")

                except subprocess.TimeoutExpired:
                    self._print_warning("Production PyPI upload timed out")
                except Exception as e:
                    self._print_warning(f"Production PyPI upload error: {e}")

            # Try Test PyPI if available or if production failed
            if has_test_token:
                self._print_info("Attempting upload to Test PyPI...")
                
                test_cmd = ["uv", "publish", "--publish-url", "https://test.pypi.org/legacy/"] + [str(f) for f in package_files]
                
                try:
                    result = subprocess.run(
                        test_cmd,
                        cwd=self.working_dir,
                        capture_output=False,  # Show real-time output
                        text=True,
                        timeout=300,  # 5 minute timeout
                    )

                    if result.returncode == 0:
                        self._print_success("✓ Uploaded to Test PyPI")
                        self._print_info(f"🔗 Test PyPI: https://test.pypi.org/project/quick-publish/{new_version}/")
                        self._print_info("To install from Test PyPI:")
                        self._print_info(f"  pip install --index-url https://test.pypi.org/simple/ quick-publish=={new_version}")
                        return
                    else:
                        self._print_error("Test PyPI upload failed")

                except subprocess.TimeoutExpired:
                    self._print_error("Test PyPI upload timed out")
                    raise QuickPublishError("PyPI upload timed out")
                except Exception as e:
                    self._print_error(f"Test PyPI upload error: {e}")
                    raise QuickPublishError(f"PyPI upload failed: {e}")
            else:
                self._print_warning("No test PyPI token available")

            # If we reach here, both uploads failed
            self._print_error("Both production and test PyPI uploads failed")
            self._print_info("Please check your PyPI authentication configuration")
            self._print_info("Set up environment variables:")
            self._print_info("  export UV_PUBLISH_TOKEN='your-production-token'")
            self._print_info("  export UV_TEST_PUBLISH_TOKEN='your-test-token'")
            raise QuickPublishError("PyPI upload failed")

        except Exception as e:
            if "PyPI upload failed" in str(e):
                raise
            raise QuickPublishError(f"Upload process failed: {e}")

    def _print_dry_run_summary(self, current_version: str, new_version: str, push_to_remote: bool) -> None:
        """Print dry run summary."""
        self._print_step("📋", "Dry Run Summary")
        
        table = Table(title="Actions that would be performed")
        table.add_column("Action", style="cyan")
        table.add_column("Details", style="white")
        
        table.add_row("Version Update", f"{current_version} → {new_version}")
        table.add_row("Update Files", "pyproject.toml, CHANGELOG.md")
        table.add_row("Git Commit", f"chore: release v{new_version}")
        table.add_row("Git Tag", f"v{new_version}")
        table.add_row("Push to Remote", "Yes" if push_to_remote else "No")
        table.add_row("Build Package", "Wheel + Source distribution")
        table.add_row("Upload to PyPI", "Yes")
        
        self.console.print(table)

    def _print_header(self, title: str) -> None:
        """Print application header."""
        panel = Panel(
            f"[bold blue]{title}[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

    def _print_step(self, step_num: int | str, description: str) -> None:
        """Print step header."""
        self.console.print(f"[bold green]Step {step_num}:[/bold green] {description}")

    def _print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[green]✓ {message}[/green]")

    def _print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red]✗ {message}[/red]")

    def _print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[yellow]⚠ {message}[/yellow]")

    def _print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[blue]ℹ {message}[/blue]")