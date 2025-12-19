"""PyPI push command."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from sindri.commands.command import Command
from sindri.runner import AsyncExecutionEngine, CommandResult


class PyPIPushCommand(Command):
    """Build and upload package to PyPI."""

    def __init__(self):
        super().__init__(
            command_id="pypi-push",
            title="Push",
            description="Build and upload package to PyPI",
        )

    async def execute(
        self,
        engine: AsyncExecutionEngine,
        cwd: Path,
        env: Dict[str, str],
        repository: Optional[str] = None,
        test: bool = False,
        **kwargs: Any,
    ) -> CommandResult:
        """Execute build and upload."""
        results = []
        
        # Check if build tools are installed
        try:
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "pip", "show", "build", "twine",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            if process.returncode != 0:
                results.append("⚠ Installing build and twine...")
                install_process = await asyncio.create_subprocess_exec(
                    "python", "-m", "pip", "install", "build", "twine",
                    cwd=str(cwd),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await install_process.communicate()
                if install_process.returncode != 0:
                    return CommandResult(
                        command_id=self.command_id,
                        exit_code=1,
                        error="Failed to install build tools",
                    )
                results.append("✓ Build tools installed")
        except Exception as e:
            return CommandResult(
                command_id=self.command_id,
                exit_code=1,
                error=f"Error checking build tools: {e}",
            )

        # Check pyproject.toml exists
        pyproject_path = cwd / "pyproject.toml"
        if not pyproject_path.exists():
            return CommandResult(
                command_id=self.command_id,
                exit_code=1,
                error="pyproject.toml not found",
            )

        # Clean dist directory
        dist_path = cwd / "dist"
        if dist_path.exists():
            import shutil
            shutil.rmtree(dist_path)
            results.append("✓ Cleaned dist directory")

        # Build package
        try:
            results.append("📦 Building package...")
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "build",
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return CommandResult(
                    command_id=self.command_id,
                    exit_code=process.returncode,
                    stdout=stdout.decode(),
                    stderr=stderr.decode(),
                    error="Package build failed",
                )
            
            results.append("✓ Package built successfully")
        except Exception as e:
            return CommandResult(
                command_id=self.command_id,
                exit_code=1,
                error=f"Error building package: {e}",
            )

        # Upload to PyPI
        try:
            results.append(f"📤 Uploading to {'Test PyPI' if test else 'PyPI'}...")
            
            upload_cmd = ["python", "-m", "twine", "upload"]
            if test:
                upload_cmd.extend(["--repository", "testpypi"])
            elif repository:
                upload_cmd.extend(["--repository", repository])
            
            upload_cmd.append("dist/*")
            
            process = await asyncio.create_subprocess_exec(
                *upload_cmd,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return CommandResult(
                    command_id=self.command_id,
                    exit_code=process.returncode,
                    stdout=stdout.decode(),
                    stderr=stderr.decode(),
                    error=f"Upload to {'Test PyPI' if test else 'PyPI'} failed",
                )
            
            results.append(f"✓ Uploaded to {'Test PyPI' if test else 'PyPI'}")
            
            return CommandResult(
                command_id=self.command_id,
                exit_code=0,
                stdout="\n".join(results) + "\n" + stdout.decode(),
            )
        except Exception as e:
            return CommandResult(
                command_id=self.command_id,
                exit_code=1,
                error=f"Error uploading package: {e}",
            )

