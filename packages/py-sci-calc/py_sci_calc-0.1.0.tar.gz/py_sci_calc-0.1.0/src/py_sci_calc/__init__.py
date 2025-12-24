import pathlib
import subprocess
import tempfile
import textwrap


def main() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmpdir = pathlib.Path(d)
        config_file = tmpdir / "py-sci-calc-init.py"
        config_file.write_text(
            textwrap.dedent("""
        import pint
        ureg = pint.UnitRegistry()                                                   
        Q_ = ureg.Quantity

        import math as m
        """)
        )

        subprocess.run(["ptpython", "-i", config_file])
