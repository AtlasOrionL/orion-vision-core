"""
🔬 Experimental Features - Orion Vision Core

This package contains experimental and research modules that explore
advanced AI concepts and prototype implementations.

⚠️ WARNING: Experimental code - not for production use!

Modules:
- quantum_consciousness: Quantum-inspired AI consciousness simulation
"""

# Experimental features version
__version__ = "0.1.0-experimental"
__author__ = "Orion Research Team"
__status__ = "Experimental"

# Experimental modules
__all__ = [
    "quantum_consciousness"
]

# Safety warning
import warnings

warnings.warn(
    "🔬 EXPERIMENTAL FEATURES: These modules are research prototypes. "
    "Not intended for production use. Use at your own risk.",
    UserWarning,
    stacklevel=2
)

# Experimental disclaimer
EXPERIMENTAL_DISCLAIMER = """
🔬 EXPERIMENTAL FEATURES DISCLAIMER

These modules are experimental prototypes designed for:
- Research and development
- Educational purposes  
- Proof of concept implementations
- Advanced AI exploration

NOT intended for:
- Production deployment
- Critical systems
- Commercial applications (without explicit permission)
- Safety-critical environments

Use responsibly and contribute to AI research advancement!
"""

def show_disclaimer():
    """Display experimental features disclaimer"""
    print(EXPERIMENTAL_DISCLAIMER)

# Auto-show disclaimer on import
show_disclaimer()
