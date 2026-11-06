import pathlib
import sys

# Permite `import tools`, `import agent`, `import cliente` desde los tests sin instalar el paquete
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
