"""
Python Code Obfuscator - Complete Rewrite

A comprehensive Python obfuscation engine supporting:
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
- Bootstrap and runtime generation

Author: Rewrite for rodarm project
"""

from __future__ import annotations

import ast
import base64
import codecs
import copy
import hashlib
import hmac
import marshal
import os
import random
import secrets
import string
import struct
import sys
import types
import zlib
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

# =============================================================================
# CONFIGURATION SYSTEM
# =============================================================================


class ObfuscationLevel(IntEnum):
    """Obfuscation intensity levels."""
    NONE = 0
    MINIMAL = 1
    STANDARD = 2
    AGGRESSIVE = 3
    MAXIMUM = 4


class WrapMode(IntEnum):
    """Wrap mode for dynamic deobfuscation."""
    DISABLED = 0
    SIMPLE = 1
    FULL = 2


class RestrictionLevel(IntEnum):
    """Module restriction levels."""
    NONE = 0
    BASIC = 1       # Can't be modified
    PRIVATE = 2     # Can't be imported by plain scripts
    RESTRICTED = 3  # Module attributes hidden


class StringEncodingMethod(Enum):
    """Methods for encoding obfuscated strings."""
    BASE64 = auto()
    HEX = auto()
    ROT13 = auto()
    XOR = auto()
    CAESAR = auto()
    REVERSE = auto()
    UNICODE_ESCAPE = auto()
    COMPRESSION = auto()
    MULTI_LAYER = auto()


class ControlFlowMethod(Enum):
    """Control flow obfuscation methods."""
    OPAQUE_PREDICATES = auto()
    DEAD_CODE = auto()
    LOOP_UNROLLING = auto()
    CONDITION_FLATTENING = auto()
    DISPATCHER = auto()


@dataclass
class ObfuscationConfig:
    """
    Comprehensive configuration for the obfuscation engine.

    This dataclass holds all configuration options for controlling
    the obfuscation process.
    """

    # === Module-level options ===
    obf_module: bool = True              # Obfuscate module bytecode
    obf_code: int = 1                    # Code object obfuscation (0-2)
    wrap_mode: WrapMode = WrapMode.SIMPLE
    restrict_module: RestrictionLevel = RestrictionLevel.BASIC
    readonly_module: bool = False

    # === Name obfuscation options ===
    mix_localnames: bool = True          # Obfuscate local variable names
    mix_argnames: bool = False           # Obfuscate function argument names
    mix_coname: int = 0                  # Hide code object names (0-2)
    mix_attr: bool = False               # Obfuscate attribute names
    mix_str: bool = False                # Obfuscate string constants
    mix_str_threshold: int = 8           # Min string length to obfuscate

    # === Advanced features ===
    enable_rft: bool = False             # Enable refactoring (full rename)
    enable_jit: bool = False             # JIT compilation simulation
    enable_control_flow: bool = False    # Control flow obfuscation
    enable_dead_code: bool = False       # Dead code injection
    enable_opaque_predicates: bool = False  # Opaque predicates

    # === RFT options ===
    rft_excludes: Set[str] = field(default_factory=set)  # Names to exclude
    rft_auto_exclude: int = 1            # Auto-exclude unknown (0-2)
    rft_preserve_exports: bool = True    # Preserve __all__ names
    rft_simple_import: bool = False      # Simple import handling
    rft_mix_import_name: bool = False    # Encrypt import names

    # === Runtime options ===
    clear_module_co: bool = True         # Clear module code after import
    clear_frame_locals: bool = False     # Clear locals in wrap mode
    import_check_license: bool = False   # Check license per import

    # === Encryption options ===
    encryption_key: Optional[bytes] = None  # Custom encryption key
    key_derivation_rounds: int = 10000   # Key derivation iterations
    use_compression: bool = True         # Compress before encrypting

    # === Output options ===
    add_bootstrap: bool = True           # Add runtime bootstrap
    include_runtime: bool = True         # Include runtime in output
    output_format: str = 'pyc'           # Output format (py, pyc, pye)

    # === Code object exclusions ===
    exclude_co_names: Set[str] = field(default_factory=lambda: {
        '<lambda>', '<listcomp>', '<setcomp>', '<dictcomp>', '<genexpr>'
    })
    exclude_modules: Set[str] = field(default_factory=lambda: {'__init__'})

    # === String encoding ===
    string_encoding_methods: List[StringEncodingMethod] = field(
        default_factory=lambda: [
            StringEncodingMethod.XOR,
            StringEncodingMethod.BASE64,
        ]
    )

    # === Control flow options ===
    control_flow_methods: List[ControlFlowMethod] = field(
        default_factory=lambda: [
            ControlFlowMethod.OPAQUE_PREDICATES,
            ControlFlowMethod.DEAD_CODE,
        ]
    )
    control_flow_intensity: float = 0.3  # Probability of applying CF obfuscation

    # === Name generation ===
    name_prefix: str = '_'               # Prefix for generated names
    use_unicode_names: bool = False      # Use unicode chars in names
    name_min_length: int = 8             # Minimum generated name length
    name_max_length: int = 16            # Maximum generated name length

    # === Debug/Development ===
    debug_mode: bool = False             # Enable debug output
    trace_rft: bool = False              # Trace refactoring
    preserve_docstrings: bool = False    # Keep docstrings
    preserve_comments: bool = False      # Keep comments (AST doesn't preserve)

    def __post_init__(self):
        """Validate and adjust configuration."""
        if self.encryption_key is None:
            self.encryption_key = secrets.token_bytes(32)
        if isinstance(self.wrap_mode, int):
            self.wrap_mode = WrapMode(self.wrap_mode)
        if isinstance(self.restrict_module, int):
            self.restrict_module = RestrictionLevel(self.restrict_module)

    @classmethod
    def minimal(cls) -> 'ObfuscationConfig':
        """Create minimal obfuscation config."""
        return cls(
            obf_module=True,
            obf_code=1,
            wrap_mode=WrapMode.DISABLED,
            mix_localnames=True,
            mix_str=False,
            enable_control_flow=False,
        )

    @classmethod
    def standard(cls) -> 'ObfuscationConfig':
        """Create standard obfuscation config."""
        return cls(
            obf_module=True,
            obf_code=1,
            wrap_mode=WrapMode.SIMPLE,
            mix_localnames=True,
            mix_str=True,
            mix_str_threshold=4,
            enable_control_flow=True,
            control_flow_intensity=0.2,
        )

    @classmethod
    def aggressive(cls) -> 'ObfuscationConfig':
        """Create aggressive obfuscation config."""
        return cls(
            obf_module=True,
            obf_code=2,
            wrap_mode=WrapMode.FULL,
            mix_localnames=True,
            mix_argnames=False,  # Disabled: breaks keyword arguments (e.g., partial(func, exp=2))
            mix_coname=1,
            mix_attr=True,
            mix_str=True,
            mix_str_threshold=2,
            enable_rft=True,
            enable_control_flow=True,
            enable_dead_code=True,
            enable_opaque_predicates=True,
            control_flow_intensity=0.5,
            use_unicode_names=True,
        )

    @classmethod
    def maximum(cls) -> 'ObfuscationConfig':
        """Create maximum obfuscation config."""
        return cls(
            obf_module=True,
            obf_code=2,
            wrap_mode=WrapMode.FULL,
            restrict_module=RestrictionLevel.RESTRICTED,
            readonly_module=True,
            mix_localnames=True,
            mix_argnames=False,  # Disabled: breaks keyword arguments (e.g., partial(func, exp=2))
            mix_coname=2,
            mix_attr=True,
            mix_str=True,
            mix_str_threshold=1,
            enable_rft=True,
            rft_mix_import_name=True,
            enable_control_flow=True,
            enable_dead_code=True,
            enable_opaque_predicates=True,
            control_flow_intensity=0.7,
            use_unicode_names=True,
            clear_module_co=True,
            clear_frame_locals=True,
        )


# =============================================================================
# NAME GENERATION UTILITIES
# =============================================================================


class NameGenerator:
    """
    Generates obfuscated names for variables, functions, classes, etc.

    Supports multiple naming strategies:
    - Random alphanumeric
    - Unicode (using various scripts)
    - Sequential with prefix
    - Hash-based (deterministic)
    """

    # Valid Unicode characters for Python identifiers
    # Using only verified valid ranges to avoid invalid code points
    UNICODE_CHARS = (
        # Greek uppercase (excluding unassigned 0x03A2)
        list(range(0x0391, 0x03A2)) + list(range(0x03A3, 0x03AA)) +
        # Greek lowercase
        list(range(0x03B1, 0x03CA)) +
        # Cyrillic uppercase
        list(range(0x0410, 0x0430)) +
        # Cyrillic lowercase
        list(range(0x0430, 0x0450))
    )

    # Characters that are valid in Python identifiers
    IDENT_START = string.ascii_letters + '_'
    IDENT_CONTINUE = string.ascii_letters + string.digits + '_'

    def __init__(
        self,
        config: ObfuscationConfig,
        seed: Optional[int] = None
    ):
        self.config = config
        self.rng = random.Random(seed)
        self._used_names: Set[str] = set()
        self._name_counter = 0
        self._name_cache: Dict[str, str] = {}

    def _generate_random_name(self, length: int) -> str:
        """Generate a random identifier name."""
        if length < 1:
            length = 1

        if self.config.use_unicode_names:
            return self._generate_unicode_name(length)

        # Start with letter or underscore
        name = self.rng.choice(self.IDENT_START)

        # Continue with alphanumeric
        for _ in range(length - 1):
            name += self.rng.choice(self.IDENT_CONTINUE)

        return name

    def _generate_unicode_name(self, length: int) -> str:
        """Generate a name using unicode characters."""
        # Don't start with underscore - the prefix will be added by caller
        # This avoids creating __ prefixed names that trigger Python's name mangling
        name = ''

        # Add unicode characters from validated list
        for _ in range(length):
            char = chr(self.rng.choice(self.UNICODE_CHARS))
            name += char

        return name

    def _generate_hash_name(self, original: str) -> str:
        """Generate deterministic name based on hash."""
        h = hashlib.sha256(original.encode()).hexdigest()
        prefix = self.config.name_prefix
        return f"{prefix}{h[:self.config.name_min_length]}"

    def generate(self, original: Optional[str] = None) -> str:
        """
        Generate a new unique obfuscated name.

        Args:
            original: Original name (for deterministic generation)

        Returns:
            A unique obfuscated name
        """
        # Check cache for deterministic naming
        if original and original in self._name_cache:
            return self._name_cache[original]

        # Generate new name
        attempts = 0
        max_attempts = 1000

        while attempts < max_attempts:
            length = self.rng.randint(
                self.config.name_min_length,
                self.config.name_max_length
            )

            name = self.config.name_prefix + self._generate_random_name(length)

            if name not in self._used_names and not self._is_builtin(name):
                self._used_names.add(name)
                if original:
                    self._name_cache[original] = name
                return name

            attempts += 1

        # Fallback to counter-based name
        self._name_counter += 1
        name = f"{self.config.name_prefix}v{self._name_counter}"
        self._used_names.add(name)
        if original:
            self._name_cache[original] = name
        return name

    def generate_consistent(self, original: str) -> str:
        """Generate a consistent name for the same original."""
        if original in self._name_cache:
            return self._name_cache[original]
        return self.generate(original)

    def _is_builtin(self, name: str) -> bool:
        """Check if name conflicts with builtins."""
        return name in dir(__builtins__) if isinstance(__builtins__, dict) else name in dir(__builtins__)

    def reserve(self, name: str) -> None:
        """Reserve a name so it won't be generated."""
        self._used_names.add(name)

    def clear_cache(self) -> None:
        """Clear the name cache."""
        self._name_cache.clear()


# =============================================================================
# STRING OBFUSCATION
# =============================================================================


class StringObfuscator:
    """
    Handles string constant obfuscation using various encoding methods.

    Supports multiple encoding strategies that can be layered:
    - Base64 encoding
    - Hex encoding
    - ROT13
    - XOR with key
    - Caesar cipher
    - String reversal
    - Unicode escape sequences
    - Compression
    - Multi-layer (combination)
    """

    def __init__(self, config: ObfuscationConfig):
        self.config = config
        self.rng = random.Random()
        self._xor_key = secrets.token_bytes(16)

    def should_obfuscate(self, s: str) -> bool:
        """Determine if a string should be obfuscated."""
        if not self.config.mix_str:
            return False
        if len(s) < self.config.mix_str_threshold:
            return False
        # Skip docstrings if preserving
        if self.config.preserve_docstrings and s.startswith('"""') or s.startswith("'''"):
            return False
        return True

    def obfuscate(self, s: str) -> Tuple[str, str]:
        """
        Obfuscate a string and return the obfuscated form with decoder.

        Returns:
            Tuple of (obfuscated_expression, decoder_function_name)
        """
        methods = self.config.string_encoding_methods

        if StringEncodingMethod.MULTI_LAYER in methods:
            return self._multi_layer_encode(s)

        method = self.rng.choice(methods)
        return self._encode_with_method(s, method)

    def _encode_with_method(
        self,
        s: str,
        method: StringEncodingMethod
    ) -> Tuple[str, str]:
        """Encode string with specific method."""

        if method == StringEncodingMethod.BASE64:
            return self._base64_encode(s)
        elif method == StringEncodingMethod.HEX:
            return self._hex_encode(s)
        elif method == StringEncodingMethod.ROT13:
            return self._rot13_encode(s)
        elif method == StringEncodingMethod.XOR:
            return self._xor_encode(s)
        elif method == StringEncodingMethod.CAESAR:
            return self._caesar_encode(s)
        elif method == StringEncodingMethod.REVERSE:
            return self._reverse_encode(s)
        elif method == StringEncodingMethod.UNICODE_ESCAPE:
            return self._unicode_escape_encode(s)
        elif method == StringEncodingMethod.COMPRESSION:
            return self._compression_encode(s)
        else:
            return self._base64_encode(s)

    def _base64_encode(self, s: str) -> Tuple[str, str]:
        """Base64 encoding."""
        encoded = base64.b64encode(s.encode('utf-8')).decode('ascii')
        decoder = f"__import__('base64').b64decode('{encoded}').decode('utf-8')"
        return decoder, 'base64'

    def _hex_encode(self, s: str) -> Tuple[str, str]:
        """Hex encoding."""
        encoded = s.encode('utf-8').hex()
        decoder = f"bytes.fromhex('{encoded}').decode('utf-8')"
        return decoder, 'hex'

    def _rot13_encode(self, s: str) -> Tuple[str, str]:
        """ROT13 encoding."""
        encoded = codecs.encode(s, 'rot_13')
        decoder = f"__import__('codecs').decode('{encoded}', 'rot_13')"
        return decoder, 'rot13'

    def _xor_encode(self, s: str) -> Tuple[str, str]:
        """XOR encoding with random key."""
        key = self._xor_key
        data = s.encode('utf-8')
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        encoded_data = base64.b64encode(encrypted).decode('ascii')
        encoded_key = base64.b64encode(key).decode('ascii')

        decoder = (
            f"(lambda d,k: bytes(b^k[i%len(k)] for i,b in enumerate(d)).decode('utf-8'))"
            f"(__import__('base64').b64decode('{encoded_data}'),"
            f"__import__('base64').b64decode('{encoded_key}'))"
        )
        return decoder, 'xor'

    def _caesar_encode(self, s: str, shift: int = 13) -> Tuple[str, str]:
        """Caesar cipher encoding."""
        result = []
        for c in s:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        encoded = ''.join(result)

        decoder = (
            f"''.join(chr((ord(c)-ord('A' if c.isupper() else 'a')-{shift})%26+"
            f"ord('A' if c.isupper() else 'a')) if c.isalpha() else c "
            f"for c in '{encoded}')"
        )
        return decoder, 'caesar'

    def _reverse_encode(self, s: str) -> Tuple[str, str]:
        """String reversal encoding."""
        encoded = s[::-1]
        # Escape the string properly
        escaped = encoded.replace('\\', '\\\\').replace("'", "\\'")
        decoder = f"'{escaped}'[::-1]"
        return decoder, 'reverse'

    def _unicode_escape_encode(self, s: str) -> Tuple[str, str]:
        """Unicode escape sequence encoding."""
        encoded = ''.join(f'\\u{ord(c):04x}' for c in s)
        decoder = f"'{encoded}'"
        return decoder, 'unicode'

    def _compression_encode(self, s: str) -> Tuple[str, str]:
        """Compression-based encoding."""
        compressed = zlib.compress(s.encode('utf-8'), level=9)
        encoded = base64.b64encode(compressed).decode('ascii')
        decoder = (
            f"__import__('zlib').decompress("
            f"__import__('base64').b64decode('{encoded}')).decode('utf-8')"
        )
        return decoder, 'compress'

    def _multi_layer_encode(self, s: str) -> Tuple[str, str]:
        """Multi-layer encoding (multiple methods stacked)."""
        # Apply compression first
        compressed = zlib.compress(s.encode('utf-8'), level=9)

        # XOR with key
        key = self._xor_key
        xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(compressed))

        # Base64 encode
        encoded = base64.b64encode(xored).decode('ascii')
        encoded_key = base64.b64encode(key).decode('ascii')

        decoder = (
            f"__import__('zlib').decompress("
            f"bytes(b^__import__('base64').b64decode('{encoded_key}')[i%len("
            f"__import__('base64').b64decode('{encoded_key}'))] "
            f"for i,b in enumerate(__import__('base64').b64decode('{encoded}')))"
            f").decode('utf-8')"
        )
        return decoder, 'multi'

    def generate_decoder_function(self, method: str) -> str:
        """Generate a decoder function for embedding in output."""
        # This generates reusable decoder functions
        if method == 'xor':
            return '''
def _d(d, k):
    import base64
    d = base64.b64decode(d)
    k = base64.b64decode(k)
    return bytes(b ^ k[i % len(k)] for i, b in enumerate(d)).decode('utf-8')
'''
        return ''


# =============================================================================
# AST TRANSFORMERS
# =============================================================================


class BaseTransformer(ast.NodeTransformer):
    """Base class for AST transformers."""

    def __init__(self, config: ObfuscationConfig):
        self.config = config
        self.changes_made = 0

    def report(self) -> str:
        """Report transformation statistics."""
        return f"{self.__class__.__name__}: {self.changes_made} changes"


class NameManglingTransformer(BaseTransformer):
    """
    Transforms names (variables, functions, classes) into obfuscated forms.

    Handles:
    - Local variable names
    - Function argument names
    - Function/method names
    - Class names
    - Comprehension variables
    """

    # Names that should never be mangled
    RESERVED_NAMES = frozenset({
        # Python keywords and builtins
        'True', 'False', 'None', 'self', 'cls',
        '__init__', '__new__', '__del__', '__repr__', '__str__',
        '__bytes__', '__format__', '__lt__', '__le__', '__eq__',
        '__ne__', '__gt__', '__ge__', '__hash__', '__bool__',
        '__getattr__', '__getattribute__', '__setattr__', '__delattr__',
        '__dir__', '__get__', '__set__', '__delete__', '__set_name__',
        '__init_subclass__', '__class_getitem__', '__call__',
        '__len__', '__length_hint__', '__getitem__', '__setitem__',
        '__delitem__', '__missing__', '__iter__', '__reversed__',
        '__contains__', '__add__', '__sub__', '__mul__', '__matmul__',
        '__truediv__', '__floordiv__', '__mod__', '__divmod__', '__pow__',
        '__lshift__', '__rshift__', '__and__', '__xor__', '__or__',
        '__neg__', '__pos__', '__abs__', '__invert__', '__complex__',
        '__int__', '__float__', '__index__', '__round__', '__trunc__',
        '__floor__', '__ceil__', '__enter__', '__exit__', '__await__',
        '__aiter__', '__anext__', '__aenter__', '__aexit__',
        '__name__', '__module__', '__qualname__', '__doc__', '__dict__',
        '__slots__', '__weakref__', '__class__', '__bases__', '__mro__',
        '__subclasses__', '__all__', '__file__', '__loader__', '__spec__',
        '__path__', '__cached__', '__package__', '__builtins__',
        '__annotations__', '__globals__', '__locals__', '__code__',
        '__closure__', '__defaults__', '__kwdefaults__',
        # Common exception handling
        'Exception', 'BaseException', 'args', 'message',
        # Async
        'async', 'await',
    })

    def __init__(
        self,
        config: ObfuscationConfig,
        name_generator: NameGenerator
    ):
        super().__init__(config)
        self.name_gen = name_generator
        self._scope_stack: List[Dict[str, str]] = []
        self._global_names: Set[str] = set()
        self._nonlocal_names: Set[str] = set()
        self._class_attrs: Set[str] = set()  # Class-level attributes (can't be renamed)
        self._imported_names: Set[str] = set()
        self._class_methods: Set[str] = set()  # Method names (can't be renamed)
        self._in_class_body: bool = False  # Track if we're directly in a class body
        self._comprehension_targets: Set[str] = set()  # Comprehension loop variables

    def _collect_class_methods(self, node: ast.AST) -> None:
        """Collect all method names defined in classes."""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._class_methods.add(item.name)

    def _collect_class_attrs(self, node: ast.AST) -> None:
        """Collect all class-level attributes (enum members, dataclass fields, etc.)."""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    # Simple assignments like DATA = 0 (enum members)
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                self._class_attrs.add(target.id)
                    # Annotated assignments like name: str (dataclass fields)
                    elif isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name):
                            self._class_attrs.add(item.target.id)

    def _should_mangle(self, name: str, is_method: bool = False) -> bool:
        """Determine if a name should be mangled."""
        if name in self.RESERVED_NAMES:
            return False
        if name.startswith('__') and name.endswith('__'):
            return False
        if name in self._global_names:
            return False
        if name in self._nonlocal_names:
            return False
        if name in self._imported_names:
            return False
        if name in self.config.rft_excludes:
            return False
        # Don't mangle method names - they're accessed via attributes
        if is_method or name in self._class_methods:
            return False
        # Don't mangle class attributes (enum members, dataclass fields, etc.)
        if name in self._class_attrs:
            return False
        # Don't mangle comprehension loop variables
        if name in self._comprehension_targets:
            return False
        return True

    def _push_scope(self) -> None:
        """Push a new scope onto the stack."""
        self._scope_stack.append({})

    def _pop_scope(self) -> None:
        """Pop the current scope."""
        if self._scope_stack:
            self._scope_stack.pop()

    def _get_mangled_name(self, name: str) -> str:
        """Get or create a mangled name for the current scope."""
        if not self._should_mangle(name):
            return name

        # Check current scope first
        for scope in reversed(self._scope_stack):
            if name in scope:
                return scope[name]

        # Create new mangled name
        mangled = self.name_gen.generate(name)
        if self._scope_stack:
            self._scope_stack[-1][name] = mangled
        self.changes_made += 1
        return mangled

    def _collect_global_nonlocal(self, node: ast.AST) -> None:
        """Collect global and nonlocal declarations."""
        for child in ast.walk(node):
            if isinstance(child, ast.Global):
                self._global_names.update(child.names)
            elif isinstance(child, ast.Nonlocal):
                self._nonlocal_names.update(child.names)

    def _collect_imports(self, node: ast.AST) -> None:
        """Collect imported names."""
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    self._imported_names.add(name)
            elif isinstance(child, ast.ImportFrom):
                for alias in child.names:
                    name = alias.asname if alias.asname else alias.name
                    self._imported_names.add(name)

    def _collect_comprehension_targets(self, node: ast.AST) -> None:
        """Collect all comprehension loop variable names."""
        for child in ast.walk(node):
            if isinstance(child, ast.comprehension):
                if isinstance(child.target, ast.Name):
                    self._comprehension_targets.add(child.target.id)
                elif isinstance(child.target, ast.Tuple):
                    for elt in child.target.elts:
                        if isinstance(elt, ast.Name):
                            self._comprehension_targets.add(elt.id)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Visit module and initialize scope."""
        self._collect_global_nonlocal(node)
        self._collect_imports(node)
        self._collect_class_methods(node)  # Collect methods to exclude
        self._collect_class_attrs(node)    # Collect class attributes to exclude
        self._collect_comprehension_targets(node)  # Collect comprehension targets
        self._push_scope()
        self.generic_visit(node)
        self._pop_scope()
        return node

    def _add_param_names_to_scope(self, args: ast.arguments) -> None:
        """Add all parameter names to current scope (mapping to themselves).

        This prevents parameters from being renamed when they're reassigned
        in the function body.
        """
        if not self._scope_stack:
            return

        # Add all argument names to current scope mapping to themselves
        for arg in args.args + args.posonlyargs + args.kwonlyargs:
            self._scope_stack[-1][arg.arg] = arg.arg
        if args.vararg:
            self._scope_stack[-1][args.vararg.arg] = args.vararg.arg
        if args.kwarg:
            self._scope_stack[-1][args.kwarg.arg] = args.kwarg.arg

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Transform function definition."""
        self._collect_global_nonlocal(node)
        self._push_scope()

        # Handle function name (but not methods - they're accessed via attributes)
        is_method = node.name in self._class_methods
        if self.config.mix_coname > 0 and self._should_mangle(node.name, is_method=is_method):
            node.name = self._get_mangled_name(node.name)

        # Handle arguments
        if self.config.mix_argnames:
            node.args = self._transform_arguments(node.args)

        # Add parameter names to scope AFTER potential renaming
        # This ensures reassigned params use the same name
        self._add_param_names_to_scope(node.args)

        # Visit body
        self.generic_visit(node)

        self._pop_scope()
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Transform async function definition."""
        self._collect_global_nonlocal(node)
        self._push_scope()

        is_method = node.name in self._class_methods
        if self.config.mix_coname > 0 and self._should_mangle(node.name, is_method=is_method):
            node.name = self._get_mangled_name(node.name)

        if self.config.mix_argnames:
            node.args = self._transform_arguments(node.args)

        # Add parameter names to scope
        self._add_param_names_to_scope(node.args)

        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Transform class definition."""
        self._push_scope()

        # Collect class attributes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._class_attrs.add(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        self._class_attrs.add(target.id)

        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        """Transform lambda expression."""
        self._push_scope()

        if self.config.mix_argnames:
            node.args = self._transform_arguments(node.args)

        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_comprehension(self, node: ast.comprehension) -> ast.comprehension:
        """Transform comprehension variable.

        Note: We do NOT rename comprehension variables because:
        1. Comprehensions have implicit scopes in Python 3
        2. The variable is used in the inline expression
        3. Proper scope tracking for comprehensions is complex
        """
        # Don't rename comprehension variables - just visit children
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Transform name reference."""
        if not self.config.mix_localnames:
            return node

        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            # First check if this name has an explicit mapping (e.g., from exception handlers)
            for scope in reversed(self._scope_stack):
                if node.id in scope:
                    node.id = scope[node.id]
                    return node

            # Only create new manglings inside functions (not module-level names)
            # Module-level names are potential exports and shouldn't be mangled
            if len(self._scope_stack) <= 1:
                return node

            if self._should_mangle(node.id):
                # If storing, create new mapping
                if isinstance(node.ctx, ast.Store):
                    node.id = self._get_mangled_name(node.id)

        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Transform function argument."""
        if self.config.mix_argnames and self._should_mangle(node.arg):
            node.arg = self._get_mangled_name(node.arg)
            # Clear annotation if mixing args
            node.annotation = None
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        """Transform exception handler name."""
        if node.name and self.config.mix_localnames:
            if self._should_mangle(node.name):
                old_name = node.name
                new_name = self._get_mangled_name(node.name)
                node.name = new_name
                # Add the mapping to scope so references in body are renamed
                if self._scope_stack:
                    self._scope_stack[-1][old_name] = new_name
        self.generic_visit(node)
        return node

    def _transform_arguments(self, args: ast.arguments) -> ast.arguments:
        """Transform function arguments."""
        # Transform regular args
        for arg in args.args:
            self.visit_arg(arg)

        # Transform positional-only args
        for arg in args.posonlyargs:
            self.visit_arg(arg)

        # Transform keyword-only args
        for arg in args.kwonlyargs:
            self.visit_arg(arg)

        # Transform *args and **kwargs
        if args.vararg:
            self.visit_arg(args.vararg)
        if args.kwarg:
            self.visit_arg(args.kwarg)

        return args


class StringObfuscationTransformer(BaseTransformer):
    """
    Transforms string constants into obfuscated expressions.
    """

    def __init__(
        self,
        config: ObfuscationConfig,
        string_obfuscator: StringObfuscator
    ):
        super().__init__(config)
        self.str_obf = string_obfuscator

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        """Transform string constants."""
        if not isinstance(node.value, str):
            return node

        if not self.str_obf.should_obfuscate(node.value):
            return node

        # Get obfuscated expression
        decoder_expr, _ = self.str_obf.obfuscate(node.value)
        self.changes_made += 1

        # Parse the expression and return the AST
        try:
            expr_ast = ast.parse(decoder_expr, mode='eval')
            return expr_ast.body
        except SyntaxError:
            # Fallback to original if parsing fails
            return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> ast.JoinedStr:
        """Handle f-strings (transform string parts only)."""
        new_values = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                # Don't obfuscate f-string parts (complex)
                new_values.append(value)
            else:
                new_values.append(self.visit(value))
        node.values = new_values
        return node


class AttributeObfuscationTransformer(BaseTransformer):
    """
    Transforms attribute access into obfuscated forms.

    Converts x.attr to getattr(x, 'attr') with obfuscated attribute name.
    Note: Method names are NOT obfuscated as they need to match definitions.
    """

    # Attributes that should never be obfuscated
    RESERVED_ATTRS = frozenset({
        '__init__', '__new__', '__del__', '__repr__', '__str__',
        '__class__', '__dict__', '__doc__', '__module__', '__name__',
        # Common methods that must be preserved
        'append', 'extend', 'insert', 'remove', 'pop', 'clear',
        'copy', 'sort', 'reverse', 'count', 'index',
        'keys', 'values', 'items', 'get', 'update', 'setdefault',
        'add', 'discard', 'union', 'intersection', 'difference',
        'read', 'write', 'close', 'seek', 'tell', 'flush',
        'encode', 'decode', 'split', 'join', 'strip', 'replace',
        'format', 'upper', 'lower', 'title', 'capitalize',
        'startswith', 'endswith', 'find', 'rfind',
    })

    def __init__(
        self,
        config: ObfuscationConfig,
        string_obfuscator: StringObfuscator
    ):
        super().__init__(config)
        self.str_obf = string_obfuscator
        self._attr_mapping: Dict[str, str] = {}
        self._method_names: Set[str] = set()
        self._in_call_func = False  # Track if we're visiting a Call's func

    def _collect_method_names(self, node: ast.AST) -> None:
        """Collect all method names defined in classes."""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._method_names.add(item.name)

    def _should_obfuscate_attr(self, attr: str, is_call: bool = False) -> bool:
        """Determine if attribute should be obfuscated."""
        if not self.config.mix_attr:
            return False
        if attr in self.RESERVED_ATTRS:
            return False
        if attr.startswith('_'):
            return False
        # Don't obfuscate method calls - they must match definitions
        if is_call or attr in self._method_names:
            return False
        return True

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Collect method names before transforming."""
        self._collect_method_names(node)
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Handle function calls specially to detect method calls."""
        # Mark that we're visiting a call's function
        old_in_call = self._in_call_func
        self._in_call_func = True
        node.func = self.visit(node.func)
        self._in_call_func = old_in_call

        # Visit arguments normally
        node.args = [self.visit(arg) for arg in node.args]
        node.keywords = [self.visit(kw) for kw in node.keywords]
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Transform attribute access."""
        # First visit the value
        node.value = self.visit(node.value)

        # Check if this is a method call (being used as a Call's func)
        is_call = self._in_call_func

        if not self._should_obfuscate_attr(node.attr, is_call):
            return node

        # Convert to getattr/setattr call
        if isinstance(node.ctx, ast.Load):
            # x.attr -> getattr(x, 'obfuscated_attr')
            obf_attr, _ = self.str_obf.obfuscate(node.attr)
            try:
                attr_expr = ast.parse(obf_attr, mode='eval').body
            except SyntaxError:
                return node

            self.changes_made += 1
            return ast.Call(
                func=ast.Name(id='getattr', ctx=ast.Load()),
                args=[node.value, attr_expr],
                keywords=[]
            )

        # For store/del contexts, more complex transformation needed
        return node


class ControlFlowObfuscationTransformer(BaseTransformer):
    """
    Transforms control flow to make analysis harder.

    Techniques:
    - Opaque predicates (always true/false conditions)
    - Dead code injection
    - Condition flattening
    - Control flow dispatcher pattern
    """

    def __init__(self, config: ObfuscationConfig):
        super().__init__(config)
        self.rng = random.Random()

    def _make_opaque_true(self) -> ast.expr:
        """Create an opaque predicate that's always True."""
        predicates = [
            # (x * x) >= 0 is always True for real numbers
            lambda: ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(value=self.rng.randint(1, 100)),
                    op=ast.Mult(),
                    right=ast.Constant(value=self.rng.randint(1, 100))
                ),
                ops=[ast.GtE()],
                comparators=[ast.Constant(value=0)]
            ),
            # (x | 1) > 0 is always True for positive x
            lambda: ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(value=self.rng.randint(1, 100)),
                    op=ast.BitOr(),
                    right=ast.Constant(value=1)
                ),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=0)]
            ),
            # len('x') > 0
            lambda: ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant(value='x' * self.rng.randint(1, 5))],
                    keywords=[]
                ),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=0)]
            ),
            # True or False is True
            lambda: ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Constant(value=True),
                    ast.Constant(value=False)
                ]
            ),
        ]
        return self.rng.choice(predicates)()

    def _make_opaque_false(self) -> ast.expr:
        """Create an opaque predicate that's always False."""
        predicates = [
            # x * x < 0 is always False for real numbers
            lambda: ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(value=self.rng.randint(1, 100)),
                    op=ast.Mult(),
                    right=ast.Constant(value=self.rng.randint(1, 100))
                ),
                ops=[ast.Lt()],
                comparators=[ast.Constant(value=0)]
            ),
            # len('') > 0 is False
            lambda: ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant(value='')],
                    keywords=[]
                ),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=0)]
            ),
            # False and True is False
            lambda: ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Constant(value=False),
                    ast.Constant(value=True)
                ]
            ),
        ]
        return self.rng.choice(predicates)()

    def _generate_dead_code(self) -> List[ast.stmt]:
        """Generate dead code statements."""
        dead_code_templates = [
            # Unused assignment
            lambda: ast.Assign(
                targets=[ast.Name(
                    id=f'_dead_{self.rng.randint(1000, 9999)}',
                    ctx=ast.Store()
                )],
                value=ast.Constant(value=self.rng.randint(0, 1000))
            ),
            # Pass statement
            lambda: ast.Pass(),
            # Unused expression
            lambda: ast.Expr(
                value=ast.Constant(value=self.rng.randint(0, 1000))
            ),
        ]

        count = self.rng.randint(1, 3)
        return [self.rng.choice(dead_code_templates)() for _ in range(count)]

    def visit_If(self, node: ast.If) -> ast.If:
        """Add opaque predicates to if statements."""
        self.generic_visit(node)

        if not self.config.enable_opaque_predicates:
            return node

        if self.rng.random() > self.config.control_flow_intensity:
            return node

        # Wrap condition with opaque predicate
        # (opaque_true and original_condition) preserves behavior
        node.test = ast.BoolOp(
            op=ast.And(),
            values=[self._make_opaque_true(), node.test]
        )

        # Optionally add dead code branch
        if self.config.enable_dead_code and self.rng.random() < 0.5:
            dead_branch = ast.If(
                test=self._make_opaque_false(),
                body=self._generate_dead_code(),
                orelse=[]
            )
            if node.orelse:
                node.orelse.insert(0, dead_branch)
            else:
                node.orelse = [dead_branch]

        self.changes_made += 1
        return node

    def visit_While(self, node: ast.While) -> ast.While:
        """Add complexity to while loops."""
        self.generic_visit(node)

        if not self.config.enable_opaque_predicates:
            return node

        if self.rng.random() > self.config.control_flow_intensity:
            return node

        # Add opaque predicate to condition
        node.test = ast.BoolOp(
            op=ast.And(),
            values=[self._make_opaque_true(), node.test]
        )

        self.changes_made += 1
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Inject dead code into functions."""
        self.generic_visit(node)

        if not self.config.enable_dead_code:
            return node

        if self.rng.random() > self.config.control_flow_intensity:
            return node

        # Insert dead code at random positions
        new_body = []
        for stmt in node.body:
            if self.rng.random() < 0.3:
                # Insert dead code before this statement
                dead_if = ast.If(
                    test=self._make_opaque_false(),
                    body=self._generate_dead_code(),
                    orelse=[]
                )
                new_body.append(dead_if)
            new_body.append(stmt)

        node.body = new_body
        self.changes_made += 1
        return node


class ImportObfuscationTransformer(BaseTransformer):
    """
    Transforms import statements into obfuscated forms.

    Converts:
    - import x -> x = __import__('x')
    - from x import y -> y = getattr(__import__('x'), 'y')
    """

    def __init__(
        self,
        config: ObfuscationConfig,
        string_obfuscator: StringObfuscator
    ):
        super().__init__(config)
        self.str_obf = string_obfuscator

    def visit_Import(self, node: ast.Import) -> Union[ast.Import, ast.Assign]:
        """Transform import statement."""
        if not self.config.rft_mix_import_name:
            return node

        # Convert: import x -> x = __import__('x')
        # For multiple imports, we need to create multiple assignments
        if len(node.names) == 1:
            alias = node.names[0]
            module_name = alias.name
            as_name = alias.asname or module_name.split('.')[0]

            # Obfuscate module name string
            obf_name, _ = self.str_obf.obfuscate(module_name)
            try:
                name_expr = ast.parse(obf_name, mode='eval').body
            except SyntaxError:
                name_expr = ast.Constant(value=module_name)

            self.changes_made += 1
            return ast.Assign(
                targets=[ast.Name(id=as_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[name_expr],
                    keywords=[]
                )
            )

        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.ImportFrom, List[ast.Assign]]:
        """Transform from...import statement."""
        if not self.config.rft_mix_import_name:
            return node

        if node.module is None:
            return node

        # For single name: from x import y -> y = getattr(__import__('x'), 'y')
        if len(node.names) == 1 and node.names[0].name != '*':
            alias = node.names[0]
            attr_name = alias.name
            as_name = alias.asname or attr_name

            # Obfuscate strings
            obf_module, _ = self.str_obf.obfuscate(node.module)
            obf_attr, _ = self.str_obf.obfuscate(attr_name)

            try:
                module_expr = ast.parse(obf_module, mode='eval').body
                attr_expr = ast.parse(obf_attr, mode='eval').body
            except SyntaxError:
                return node

            self.changes_made += 1
            return ast.Assign(
                targets=[ast.Name(id=as_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='getattr', ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Name(id='__import__', ctx=ast.Load()),
                            args=[module_expr],
                            keywords=[]
                        ),
                        attr_expr
                    ],
                    keywords=[]
                )
            )

        return node


class RFTTransformer(BaseTransformer):
    """
    Refactoring Transformer - comprehensive identifier renaming.

    This transformer performs a complete analysis of the code and
    renames all identifiers consistently throughout.

    Note: Method names are NOT renamed because they're accessed via
    attribute access and we can't easily track all call sites.
    """

    def __init__(
        self,
        config: ObfuscationConfig,
        name_generator: NameGenerator
    ):
        super().__init__(config)
        self.name_gen = name_generator
        self._name_mapping: Dict[str, str] = {}
        self._class_methods: Set[str] = set()
        self._class_attrs: Set[str] = set()  # Class-level attributes (can't be renamed)
        self._global_names: Set[str] = set()
        self._imported_names: Set[str] = set()
        self._export_names: Set[str] = set()  # Names in __all__

    def _collect_class_methods(self, node: ast.AST) -> None:
        """Collect all method names defined in classes."""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self._class_methods.add(item.name)

    def _collect_class_attrs(self, node: ast.AST) -> None:
        """Collect all class-level attributes (enum members, dataclass fields, etc.)."""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for item in child.body:
                    # Simple assignments like DATA = 0 (enum members)
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                self._class_attrs.add(target.id)
                    # Annotated assignments like name: str (dataclass fields)
                    elif isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name):
                            self._class_attrs.add(item.target.id)

    def _should_rename(self, name: str, is_method: bool = False) -> bool:
        """Determine if a name should be renamed."""
        # Skip reserved names
        if name in NameManglingTransformer.RESERVED_NAMES:
            return False
        # Skip dunder methods
        if name.startswith('__') and name.endswith('__'):
            return False
        # Skip excluded names
        if name in self.config.rft_excludes:
            return False
        # Skip exports if preserving
        if self.config.rft_preserve_exports and name in self._export_names:
            return False
        # Skip imported names if not mixing imports
        if not self.config.rft_mix_import_name and name in self._imported_names:
            return False
        # Skip class methods - can't track all call sites via attribute access
        if is_method or name in self._class_methods:
            return False
        # Skip class attributes (enum members, dataclass fields, etc.)
        if name in self._class_attrs:
            return False
        return True

    def _get_renamed(self, name: str) -> str:
        """Get or create renamed identifier."""
        if not self._should_rename(name):
            return name

        if name in self._name_mapping:
            return self._name_mapping[name]

        new_name = self.name_gen.generate(name)
        self._name_mapping[name] = new_name
        self.changes_made += 1
        return new_name

    def _analyze_module(self, node: ast.Module) -> None:
        """Pre-analyze module for special names."""
        for stmt in node.body:
            # Find __all__ definition
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(stmt.value, (ast.List, ast.Tuple)):
                            for elt in stmt.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    self._export_names.add(elt.value)

            # Collect imports
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    name = alias.asname or alias.name.split('.')[0]
                    self._imported_names.add(name)
            elif isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    name = alias.asname or alias.name
                    self._imported_names.add(name)

            # Collect global definitions
            if isinstance(stmt, ast.Global):
                self._global_names.update(stmt.names)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Transform module with full refactoring."""
        self._analyze_module(node)
        self._collect_class_methods(node)  # Collect methods to exclude
        self._collect_class_attrs(node)    # Collect class attributes to exclude
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Rename function (but not methods - they're accessed via attributes)."""
        # Check if this is a method (it will be in _class_methods)
        is_method = node.name in self._class_methods
        if self._should_rename(node.name, is_method=is_method):
            node.name = self._get_renamed(node.name)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Rename async function (but not methods)."""
        is_method = node.name in self._class_methods
        if self._should_rename(node.name, is_method=is_method):
            node.name = self._get_renamed(node.name)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Rename class."""
        if self._should_rename(node.name):
            node.name = self._get_renamed(node.name)
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Rename name reference."""
        if node.id in self._name_mapping:
            node.id = self._name_mapping[node.id]
        elif self._should_rename(node.id):
            # Only rename if we've seen a definition
            pass
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Process argument annotation (but don't rename arg names - breaks keyword args)."""
        # Don't rename argument names - this breaks keyword arguments like partial(func, arg=value)
        # Only process annotation to rename type references
        if node.annotation:
            node.annotation = self.visit(node.annotation)
        return node

    def visit_alias(self, node: ast.alias) -> ast.alias:
        """Handle import alias renaming."""
        if node.asname and self._should_rename(node.asname):
            node.asname = self._get_renamed(node.asname)
        return node


# =============================================================================
# CODE OBJECT TRANSFORMATION
# =============================================================================


class CodeObjectObfuscator:
    """
    Handles bytecode-level code object obfuscation.

    This includes:
    - Bytecode encryption
    - Code object attribute obfuscation
    - Constant pool obfuscation
    """

    def __init__(self, config: ObfuscationConfig):
        self.config = config
        self._key = config.encryption_key or secrets.token_bytes(32)

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            self._key,
            salt,
            self.config.key_derivation_rounds,
            dklen=32
        )

    def _xor_bytes(self, data: bytes, key: bytes) -> bytes:
        """XOR encrypt/decrypt bytes."""
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def encrypt_bytecode(self, code: types.CodeType) -> Tuple[bytes, bytes]:
        """
        Encrypt a code object's bytecode.

        Returns:
            Tuple of (encrypted_data, salt)
        """
        # Marshal the code object
        marshaled = marshal.dumps(code)

        # Optionally compress
        if self.config.use_compression:
            marshaled = zlib.compress(marshaled, level=9)

        # Generate salt and derive key
        salt = secrets.token_bytes(16)
        key = self._derive_key(salt)

        # Encrypt
        encrypted = self._xor_bytes(marshaled, key)

        return encrypted, salt

    def create_decryption_stub(
        self,
        encrypted_data: bytes,
        salt: bytes
    ) -> str:
        """Create Python code that decrypts and executes the bytecode."""
        encoded_data = base64.b64encode(encrypted_data).decode('ascii')
        encoded_salt = base64.b64encode(salt).decode('ascii')
        encoded_key = base64.b64encode(self._key).decode('ascii')

        stub = f'''
# Obfuscated code - do not modify
import base64 as _b
import hashlib as _h
import marshal as _m
import types as _t
import zlib as _z

def _d():
    _ed = _b.b64decode('{encoded_data}')
    _s = _b.b64decode('{encoded_salt}')
    _k = _b.b64decode('{encoded_key}')
    _dk = _h.pbkdf2_hmac('sha256', _k, _s, {self.config.key_derivation_rounds}, dklen=32)
    _dc = bytes(b ^ _dk[i % len(_dk)] for i, b in enumerate(_ed))
    {'_dc = _z.decompress(_dc)' if self.config.use_compression else ''}
    return _m.loads(_dc)

exec(_d())
'''
        return stub

    def obfuscate_code_object(
        self,
        code: types.CodeType,
        name_mapping: Optional[Dict[str, str]] = None
    ) -> types.CodeType:
        """
        Obfuscate a code object's attributes.

        This modifies:
        - co_varnames (local variable names)
        - co_names (global names used)
        - co_freevars (closure variables)
        - co_cellvars (cell variables)
        """
        if not name_mapping:
            return code

        # Python 3.8+ code object replacement
        def map_names(names: Tuple[str, ...]) -> Tuple[str, ...]:
            return tuple(name_mapping.get(n, n) for n in names)

        # Get code attributes based on Python version
        if sys.version_info >= (3, 8):
            new_code = code.replace(
                co_varnames=map_names(code.co_varnames),
                co_freevars=map_names(code.co_freevars),
                co_cellvars=map_names(code.co_cellvars),
            )
        else:
            # Older Python - use types.CodeType constructor
            new_code = types.CodeType(
                code.co_argcount,
                code.co_kwonlyargcount,
                code.co_nlocals,
                code.co_stacksize,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                map_names(code.co_varnames),
                code.co_filename,
                code.co_name,
                code.co_firstlineno,
                code.co_lnotab,
                map_names(code.co_freevars),
                map_names(code.co_cellvars),
            )

        return new_code

    def obfuscate_constants(
        self,
        code: types.CodeType,
        string_obfuscator: StringObfuscator
    ) -> types.CodeType:
        """Obfuscate string constants in code object."""
        # This is complex because we need to modify bytecode too
        # For now, return unchanged - string obfuscation is done at AST level
        return code


# =============================================================================
# WRAP MODE IMPLEMENTATION
# =============================================================================


class WrapModeGenerator:
    """
    Generates wrap mode protection code.

    Wrap mode adds runtime encryption/decryption:
    - __armor_enter__() decrypts bytecode before execution
    - __armor_exit__() re-encrypts after execution
    """

    def __init__(self, config: ObfuscationConfig):
        self.config = config

    def generate_wrapped_function(
        self,
        func_name: str,
        original_code: str,
        encrypted_bytecode: bytes
    ) -> str:
        """Generate a wrapped function with dynamic decryption."""
        encoded = base64.b64encode(encrypted_bytecode).decode('ascii')

        # Simple wrap mode
        if self.config.wrap_mode == WrapMode.SIMPLE:
            return f'''
def {func_name}(*args, **kwargs):
    import base64, marshal, types
    _code = marshal.loads(base64.b64decode('{encoded}'))
    _func = types.FunctionType(_code, globals())
    return _func(*args, **kwargs)
'''

        # Full wrap mode with cleanup
        elif self.config.wrap_mode == WrapMode.FULL:
            return f'''
def {func_name}(*args, **kwargs):
    import base64, marshal, types, sys
    _code = marshal.loads(base64.b64decode('{encoded}'))
    _func = types.FunctionType(_code, globals())
    try:
        _result = _func(*args, **kwargs)
    finally:
        # Clear frame locals
        if {self.config.clear_frame_locals}:
            _frame = sys._getframe()
            if _frame.f_locals:
                _frame.f_locals.clear()
    return _result
'''

        return original_code

    def generate_armor_runtime(self) -> str:
        """Generate the armor runtime functions."""
        return '''
# Armor runtime
import sys as _sys
import types as _types

def __armor_enter__(code_data):
    """Decrypt and execute protected code."""
    import base64, marshal, zlib
    _data = base64.b64decode(code_data)
    _data = zlib.decompress(_data)
    return marshal.loads(_data)

def __armor_exit__():
    """Cleanup after protected code execution."""
    _frame = _sys._getframe(1)
    # Optionally clear locals
    pass

def __armor_wrap__(func):
    """Decorator for protected functions."""
    def wrapper(*args, **kwargs):
        __armor_enter__(func.__armor_data__)
        try:
            return func(*args, **kwargs)
        finally:
            __armor_exit__()
    return wrapper
'''


# =============================================================================
# BOOTSTRAP AND RUNTIME GENERATION
# =============================================================================


class RuntimeGenerator:
    """
    Generates the runtime support code and bootstrap.
    """

    def __init__(self, config: ObfuscationConfig):
        self.config = config

    def generate_bootstrap(
        self,
        obfuscated_code: str,
        encrypted_data: Optional[bytes] = None
    ) -> str:
        """Generate complete bootstrap code."""
        bootstrap = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Protected by Python Obfuscator

'''

        # Add restriction checks
        if self.config.restrict_module != RestrictionLevel.NONE:
            bootstrap += self._generate_restriction_check()

        # Add readonly protection
        if self.config.readonly_module:
            bootstrap += self._generate_readonly_protection()

        # Add the main code
        if encrypted_data:
            bootstrap += self._generate_encrypted_loader(encrypted_data)
        else:
            bootstrap += obfuscated_code

        return bootstrap

    def _generate_restriction_check(self) -> str:
        """Generate module restriction checking code."""
        level = self.config.restrict_module

        if level == RestrictionLevel.BASIC:
            return '''
# Module protection - basic
import sys as _sys
_orig_module = _sys.modules.get(__name__)

def _check_modification():
    if _sys.modules.get(__name__) is not _orig_module:
        raise RuntimeError("Module modification detected")
'''

        elif level == RestrictionLevel.PRIVATE:
            return '''
# Module protection - private
import sys as _sys

class _ProtectedModule:
    def __init__(self, module):
        self._module = module

    def __getattr__(self, name):
        _frame = _sys._getframe(1)
        _caller = _frame.f_globals.get('__name__', '')
        if not _caller.startswith(__name__.rsplit('.', 1)[0]):
            if not hasattr(_frame.f_code, '__armor__'):
                raise ImportError("Cannot import from unprotected code")
        return getattr(self._module, name)

_sys.modules[__name__] = _ProtectedModule(_sys.modules[__name__])
'''

        elif level == RestrictionLevel.RESTRICTED:
            return '''
# Module protection - restricted
import sys as _sys

class _RestrictedModule:
    __slots__ = ('_module', '_allowed')

    def __init__(self, module, allowed):
        object.__setattr__(self, '_module', module)
        object.__setattr__(self, '_allowed', allowed)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(f"Access denied: {name}")
        return getattr(self._module, name)

    def __setattr__(self, name, value):
        raise AttributeError("Module is read-only")

    def __dir__(self):
        return [n for n in dir(self._module) if not n.startswith('_')]

_sys.modules[__name__] = _RestrictedModule(_sys.modules[__name__], set())
'''

        return ''

    def _generate_readonly_protection(self) -> str:
        """Generate readonly module protection."""
        return '''
# Readonly module protection
import sys as _sys

class _ReadonlyModule:
    def __init__(self, module):
        self.__dict__['_module'] = module

    def __getattr__(self, name):
        return getattr(self._module, name)

    def __setattr__(self, name, value):
        raise AttributeError(f"Cannot modify readonly module attribute: {name}")

    def __delattr__(self, name):
        raise AttributeError(f"Cannot delete readonly module attribute: {name}")

_sys.modules[__name__] = _ReadonlyModule(_sys.modules[__name__])
'''

    def _generate_encrypted_loader(self, encrypted_data: bytes) -> str:
        """Generate encrypted code loader."""
        encoded = base64.b64encode(encrypted_data).decode('ascii')
        key_encoded = base64.b64encode(self.config.encryption_key).decode('ascii')

        return f'''
# Encrypted code loader
def _load():
    import base64, hashlib, marshal, zlib
    _data = base64.b64decode('{encoded}')
    _key = base64.b64decode('{key_encoded}')
    _salt = _data[:16]
    _encrypted = _data[16:]
    _dk = hashlib.pbkdf2_hmac('sha256', _key, _salt, {self.config.key_derivation_rounds}, dklen=32)
    _decrypted = bytes(b ^ _dk[i % len(_dk)] for i, b in enumerate(_encrypted))
    _decompressed = zlib.decompress(_decrypted)
    _code = marshal.loads(_decompressed)
    exec(_code, globals())

_load()
del _load
'''

    def generate_runtime_package(self, output_dir: Path) -> None:
        """Generate a runtime package for the obfuscated code."""
        runtime_dir = output_dir / 'obfus_runtime'
        runtime_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_code = '''
"""
Obfus Runtime Package

This package provides runtime support for obfuscated Python code.
"""

from ._runtime import __obfus__, __armor_enter__, __armor_exit__

__all__ = ['__obfus__', '__armor_enter__', '__armor_exit__']
'''
        (runtime_dir / '__init__.py').write_text(init_code)

        # Create _runtime.py
        runtime_code = '''
"""
Runtime support functions for obfuscated code.
"""

import base64
import hashlib
import marshal
import sys
import types
import zlib


def __obfus__(name, filepath, data):
    """
    Main entry point for loading obfuscated modules.

    Args:
        name: Module name
        filepath: Original file path
        data: Encrypted bytecode data
    """
    # Decode the data
    decoded = base64.b64decode(data)

    # Extract salt and encrypted content
    salt = decoded[:16]
    encrypted = decoded[16:]

    # Get the key from environment or embedded
    key = _get_key()

    # Derive decryption key
    dk = hashlib.pbkdf2_hmac('sha256', key, salt, 10000, dklen=32)

    # Decrypt
    decrypted = bytes(b ^ dk[i % len(dk)] for i, b in enumerate(encrypted))

    # Decompress
    decompressed = zlib.decompress(decrypted)

    # Load code object
    code = marshal.loads(decompressed)

    # Execute in caller's namespace
    frame = sys._getframe(1)
    exec(code, frame.f_globals)


def __armor_enter__(data):
    """Enter protected code section."""
    decoded = base64.b64decode(data)
    decompressed = zlib.decompress(decoded)
    return marshal.loads(decompressed)


def __armor_exit__():
    """Exit protected code section."""
    # Cleanup can be done here
    frame = sys._getframe(1)
    # Optionally clear sensitive data from frame
    pass


def _get_key():
    """Get the encryption key."""
    import os
    # Try environment variable first
    key = os.environ.get('OBFUS_KEY')
    if key:
        return base64.b64decode(key)
    # Fallback to embedded key (should be replaced during obfuscation)
    return b'\\x00' * 32
'''
        (runtime_dir / '_runtime.py').write_text(runtime_code)


# =============================================================================
# MAIN OBFUSCATION ENGINE
# =============================================================================


class ObfuscationEngine:
    """
    Main obfuscation engine that orchestrates all transformations.

    This is the primary interface for obfuscating Python code.
    """

    def __init__(self, config: Optional[ObfuscationConfig] = None):
        self.config = config or ObfuscationConfig()
        self.name_gen = NameGenerator(self.config)
        self.str_obf = StringObfuscator(self.config)
        self.code_obf = CodeObjectObfuscator(self.config)
        self.wrap_gen = WrapModeGenerator(self.config)
        self.runtime_gen = RuntimeGenerator(self.config)

        # Statistics
        self._stats = {
            'files_processed': 0,
            'names_mangled': 0,
            'strings_obfuscated': 0,
            'control_flow_changes': 0,
        }

    def obfuscate_source(self, source: str, filename: str = '<string>') -> str:
        """
        Obfuscate Python source code.

        Args:
            source: Python source code string
            filename: Original filename (for error messages)

        Returns:
            Obfuscated source code
        """
        # Parse source to AST
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as e:
            raise ValueError(f"Failed to parse source: {e}")

        # Apply transformations
        tree = self._apply_transformations(tree)

        # Convert back to source
        obfuscated = ast.unparse(tree)

        # Add bootstrap if configured
        if self.config.add_bootstrap:
            obfuscated = self.runtime_gen.generate_bootstrap(obfuscated)

        self._stats['files_processed'] += 1
        return obfuscated

    def obfuscate_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Obfuscate a Python file.

        Args:
            input_path: Path to input Python file
            output_path: Path for output (defaults to input_path with .obf suffix)

        Returns:
            Path to obfuscated file
        """
        input_path = Path(input_path)

        if output_path is None:
            output_path = input_path.with_suffix('.obf.py')
        else:
            output_path = Path(output_path)

        # Read source
        source = input_path.read_text(encoding='utf-8')

        # Obfuscate
        obfuscated = self.obfuscate_source(source, str(input_path))

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(obfuscated, encoding='utf-8')

        return output_path

    def obfuscate_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        pattern: str = '**/*.py',
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """
        Obfuscate all Python files in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory (defaults to input_dir/dist)
            pattern: Glob pattern for finding Python files
            exclude_patterns: Patterns to exclude

        Returns:
            List of obfuscated file paths
        """
        input_dir = Path(input_dir)

        if output_dir is None:
            output_dir = input_dir / 'dist'
        else:
            output_dir = Path(output_dir)

        exclude_patterns = exclude_patterns or ['**/__pycache__/**', '**/.*']

        output_files = []

        for py_file in input_dir.glob(pattern):
            # Check exclusions
            skip = False
            for exclude in exclude_patterns:
                if py_file.match(exclude):
                    skip = True
                    break

            if skip:
                continue

            # Calculate output path
            rel_path = py_file.relative_to(input_dir)
            out_path = output_dir / rel_path

            # Obfuscate
            try:
                result_path = self.obfuscate_file(py_file, out_path)
                output_files.append(result_path)
            except Exception as e:
                if self.config.debug_mode:
                    print(f"Error obfuscating {py_file}: {e}")

        # Generate runtime package if configured
        if self.config.include_runtime:
            self.runtime_gen.generate_runtime_package(output_dir)

        return output_files

    def obfuscate_to_bytecode(self, source: str, filename: str = '<string>') -> bytes:
        """
        Obfuscate source and return encrypted bytecode.

        Args:
            source: Python source code
            filename: Original filename

        Returns:
            Encrypted bytecode data
        """
        # First obfuscate at AST level (without bootstrap)
        original_bootstrap = self.config.add_bootstrap
        self.config.add_bootstrap = False
        obfuscated = self.obfuscate_source(source, filename)
        self.config.add_bootstrap = original_bootstrap

        # Compile to bytecode
        code = compile(obfuscated, filename, 'exec')

        # Encrypt
        encrypted, salt = self.code_obf.encrypt_bytecode(code)

        # Combine salt + encrypted data
        return salt + encrypted

    def _apply_transformations(self, tree: ast.Module) -> ast.Module:
        """Apply all configured transformations to AST."""
        transformers: List[BaseTransformer] = []

        # RFT (full refactoring) - comprehensive renaming
        if self.config.enable_rft:
            transformers.append(RFTTransformer(self.config, self.name_gen))
            # When RFT is enabled, skip NameMangling to avoid conflicts
            # RFT handles comprehensive identifier renaming
        elif self.config.mix_localnames or self.config.mix_argnames or self.config.mix_coname:
            # Name mangling only when RFT is not enabled
            transformers.append(NameManglingTransformer(self.config, self.name_gen))

        # String obfuscation
        if self.config.mix_str:
            transformers.append(StringObfuscationTransformer(self.config, self.str_obf))

        # Attribute obfuscation
        if self.config.mix_attr:
            transformers.append(AttributeObfuscationTransformer(self.config, self.str_obf))

        # Import obfuscation
        if self.config.rft_mix_import_name:
            transformers.append(ImportObfuscationTransformer(self.config, self.str_obf))

        # Control flow obfuscation
        if self.config.enable_control_flow:
            transformers.append(ControlFlowObfuscationTransformer(self.config))

        # Apply all transformers
        for transformer in transformers:
            tree = transformer.visit(tree)
            ast.fix_missing_locations(tree)

            # Update stats
            if hasattr(transformer, 'changes_made'):
                self._stats['names_mangled'] += transformer.changes_made

        return tree

    def get_statistics(self) -> Dict[str, int]:
        """Get obfuscation statistics."""
        return self._stats.copy()

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        for key in self._stats:
            self._stats[key] = 0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def obfuscate(
    source: str,
    level: str = 'standard',
    **config_overrides
) -> str:
    """
    Convenience function to obfuscate Python source code.

    Args:
        source: Python source code
        level: Obfuscation level ('minimal', 'standard', 'aggressive', 'maximum')
        **config_overrides: Override specific config options

    Returns:
        Obfuscated source code
    """
    # Get preset config
    if level == 'minimal':
        config = ObfuscationConfig.minimal()
    elif level == 'standard':
        config = ObfuscationConfig.standard()
    elif level == 'aggressive':
        config = ObfuscationConfig.aggressive()
    elif level == 'maximum':
        config = ObfuscationConfig.maximum()
    else:
        config = ObfuscationConfig()

    # Apply overrides
    for key, value in config_overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    engine = ObfuscationEngine(config)
    return engine.obfuscate_source(source)


def obfuscate_file(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    level: str = 'standard',
    **config_overrides
) -> Path:
    """
    Convenience function to obfuscate a Python file.

    Args:
        input_path: Input file path
        output_path: Output file path (optional)
        level: Obfuscation level
        **config_overrides: Override specific config options

    Returns:
        Path to obfuscated file
    """
    if level == 'minimal':
        config = ObfuscationConfig.minimal()
    elif level == 'standard':
        config = ObfuscationConfig.standard()
    elif level == 'aggressive':
        config = ObfuscationConfig.aggressive()
    elif level == 'maximum':
        config = ObfuscationConfig.maximum()
    else:
        config = ObfuscationConfig()

    for key, value in config_overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    engine = ObfuscationEngine(config)
    return engine.obfuscate_file(
        Path(input_path),
        Path(output_path) if output_path else None
    )


def obfuscate_directory(
    input_dir: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    level: str = 'standard',
    **config_overrides
) -> List[Path]:
    """
    Convenience function to obfuscate all Python files in a directory.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path (optional)
        level: Obfuscation level
        **config_overrides: Override specific config options

    Returns:
        List of obfuscated file paths
    """
    if level == 'minimal':
        config = ObfuscationConfig.minimal()
    elif level == 'standard':
        config = ObfuscationConfig.standard()
    elif level == 'aggressive':
        config = ObfuscationConfig.aggressive()
    elif level == 'maximum':
        config = ObfuscationConfig.maximum()
    else:
        config = ObfuscationConfig()

    for key, value in config_overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    engine = ObfuscationEngine(config)
    return engine.obfuscate_directory(
        Path(input_dir),
        Path(output_dir) if output_dir else None
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Command-line interface for the obfuscator."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Python Code Obfuscator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s input.py                    # Obfuscate file with standard settings
  %(prog)s input.py -o output.py       # Specify output file
  %(prog)s src/ -o dist/               # Obfuscate directory
  %(prog)s input.py --level maximum    # Maximum obfuscation
  %(prog)s input.py --mix-str          # Enable string obfuscation
'''
    )

    parser.add_argument(
        'input',
        help='Input Python file or directory'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file or directory'
    )

    parser.add_argument(
        '--level',
        choices=['minimal', 'standard', 'aggressive', 'maximum'],
        default='standard',
        help='Obfuscation level (default: standard)'
    )

    parser.add_argument(
        '--mix-str',
        action='store_true',
        help='Enable string obfuscation'
    )

    parser.add_argument(
        '--mix-attr',
        action='store_true',
        help='Enable attribute obfuscation'
    )

    parser.add_argument(
        '--mix-args',
        action='store_true',
        help='Enable argument name obfuscation'
    )

    parser.add_argument(
        '--control-flow',
        action='store_true',
        help='Enable control flow obfuscation'
    )

    parser.add_argument(
        '--rft',
        action='store_true',
        help='Enable full refactoring (RFT)'
    )

    parser.add_argument(
        '--no-bootstrap',
        action='store_true',
        help='Do not add bootstrap code'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )

    args = parser.parse_args()

    # Build config overrides
    overrides = {}

    if args.mix_str:
        overrides['mix_str'] = True
    if args.mix_attr:
        overrides['mix_attr'] = True
    if args.mix_args:
        overrides['mix_argnames'] = True
    if args.control_flow:
        overrides['enable_control_flow'] = True
    if args.rft:
        overrides['enable_rft'] = True
    if args.no_bootstrap:
        overrides['add_bootstrap'] = False
    if args.debug:
        overrides['debug_mode'] = True

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    try:
        if input_path.is_dir():
            results = obfuscate_directory(
                input_path,
                output_path,
                level=args.level,
                **overrides
            )
            print(f"Obfuscated {len(results)} files")
            for path in results:
                print(f"  - {path}")
        else:
            result = obfuscate_file(
                input_path,
                output_path,
                level=args.level,
                **overrides
            )
            print(f"Obfuscated: {result}")

    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
