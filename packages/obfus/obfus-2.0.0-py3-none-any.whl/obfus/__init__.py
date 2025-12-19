"""
obfus - A comprehensive Python code obfuscation engine.

This library provides powerful code obfuscation capabilities including:
- String obfuscation (multiple encoding methods)
- Name mangling (locals, arguments, code names, attributes)
- Code object obfuscation with encryption
- Module-level obfuscation
- Wrap mode (dynamic deobfuscation)
- Refactoring (RFT - complete identifier renaming)
- Import obfuscation
- Control flow obfuscation
- Dead code injection
- Opaque predicates

Basic usage:

    from obfus import ObfuscationConfig, ObfuscationEngine

    # Use preset configurations
    config = ObfuscationConfig.minimal()   # Light obfuscation
    config = ObfuscationConfig.standard()  # Balanced obfuscation
    config = ObfuscationConfig.aggressive()  # Heavy obfuscation

    # Or customize
    config = ObfuscationConfig(
        mix_localnames=True,
        mix_str=True,
        enable_rft=True,
    )

    # Create engine and obfuscate
    engine = ObfuscationEngine(config)
    obfuscated_code = engine.obfuscate_source(source_code)

    # Or use convenience functions
    from obfus import obfuscate, obfuscate_file, obfuscate_directory

    result = obfuscate(source_code)
    obfuscate_file("input.py", "output.py")
    obfuscate_directory("src/", "dist/")
"""

__version__ = "1.0.0"
__author__ = "Farshid Ashouri"
__email__ = "farsheed.ashouri@gmail.com"

from .engine import (
    # Enums
    ControlFlowMethod,
    ObfuscationLevel,
    RestrictionLevel,
    StringEncodingMethod,
    WrapMode,
    # Configuration
    ObfuscationConfig,
    # Engine
    ObfuscationEngine,
    # Convenience functions
    main,
    obfuscate,
    obfuscate_directory,
    obfuscate_file,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Enums
    "ObfuscationLevel",
    "WrapMode",
    "RestrictionLevel",
    "StringEncodingMethod",
    "ControlFlowMethod",
    # Configuration
    "ObfuscationConfig",
    # Engine
    "ObfuscationEngine",
    # Convenience functions
    "obfuscate",
    "obfuscate_file",
    "obfuscate_directory",
    "main",
]
