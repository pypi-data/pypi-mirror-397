import shutil
from pathlib import Path
from subprocess import run

from hatchling.builders.hooks.plugin.interface import (
    BuildHookInterface,  # type: ignore[import-untyped]
)


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        project_root = Path(self.root)

        studio_ui_dir = project_root / "studio-ui"
        dist_dir = studio_ui_dir / "dist"
        ui_dir = project_root / "src" / "autreach" / "ui"

        ui_already_exists = ui_dir.exists() and (ui_dir / "index.html").exists()
        node_modules_exists = (
            (studio_ui_dir / "node_modules").exists()
            if studio_ui_dir.exists()
            else False
        )

        if ui_already_exists and not node_modules_exists:
            if not (ui_dir / "__init__.py").exists():
                (ui_dir / "__init__.py").touch()
            if "force_include" not in build_data:
                build_data["force_include"] = {}
            build_data["force_include"][str(ui_dir.relative_to(project_root))] = (
                "autreach/ui"
            )
            return

        if not studio_ui_dir.exists():
            raise FileNotFoundError(f"studio-ui directory not found at {studio_ui_dir}")

        if not node_modules_exists:
            run(
                ["pnpm", "install", "--frozen-lockfile"],
                cwd=str(studio_ui_dir),
                check=True,
            )

        run(
            ["pnpm", "build"],
            cwd=str(studio_ui_dir),
            check=True,
        )

        if not dist_dir.exists():
            raise RuntimeError(f"Build output directory {dist_dir} was not created")

        if not (dist_dir / "index.html").exists():
            raise RuntimeError(
                f"Build output {dist_dir / 'index.html'} was not created"
            )

        if ui_dir.exists():
            shutil.rmtree(ui_dir)

        shutil.copytree(dist_dir, ui_dir)

        (ui_dir / "__init__.py").touch()

        if "force_include" not in build_data:
            build_data["force_include"] = {}
        build_data["force_include"][str(ui_dir.relative_to(project_root))] = (
            "autreach/ui"
        )
