"""Execute the saved Notebook 1 in a new kernel using this Python environment.

Run from the project root: .venv/Scripts/python.exe src/run_notebook.py
Does not regenerate the notebook or erase manual edits.
"""
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

path = Path(__file__).resolve().parents[1] / 'notebooks/01_build_dataset.ipynb'
notebook = nbformat.read(path, as_version=4)
for cell in notebook.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None
manager = KernelManager(kernel_name='python3')
manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
client = NotebookClient(notebook, km=manager, timeout=300,
                        resources={'metadata': {'path': str(path.parent)}})
try:
    client.execute()
finally:
    nbformat.write(notebook, path)
nbformat.validate(notebook)
assert all(cell.execution_count is not None for cell in notebook.cells if cell.cell_type == 'code')
assert not any(output.output_type == 'error' for cell in notebook.cells
               if cell.cell_type == 'code' for output in cell.outputs)
print('Notebook 1: all cells executed in order in a fresh kernel; outputs saved and validated.')
