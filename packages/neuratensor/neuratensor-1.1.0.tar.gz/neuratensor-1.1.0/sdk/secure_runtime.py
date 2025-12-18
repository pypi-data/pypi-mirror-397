
"""
NeuraTensor Runtime Validator
==============================

Valida integridad y acoplamiento del kernel.
"""

import hashlib
import ctypes
from pathlib import Path


class SecureRuntime:
    """Runtime con validación de integridad"""
    
    def __init__(self, lib_path: str, expected_hash: str):
        self.lib_path = Path(lib_path)
        self.expected_hash = expected_hash
        
        # Validar integridad del .so
        if not self._verify_integrity():
            raise RuntimeError("Kernel integrity check failed")
        
        # Cargar biblioteca
        self.lib = ctypes.CDLL(str(self.lib_path))
        
        # Definir prototipos de funciones
        self._setup_prototypes()
    
    def _verify_integrity(self) -> bool:
        """Verifica hash del binario"""
        if not self.lib_path.exists():
            return False
        
        # Calcular hash del archivo
        sha256 = hashlib.sha256()
        with open(self.lib_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        actual_hash = sha256.hexdigest()
        return actual_hash == self.expected_hash
    
    def _setup_prototypes(self):
        """Configura prototipos de funciones C"""
        # nt_create_context
        self.lib.nt_create_context.argtypes = [
            ctypes.c_void_p,  # config_data
            ctypes.c_size_t,  # config_size
            ctypes.c_char_p   # config_hash
        ]
        self.lib.nt_create_context.restype = ctypes.c_void_p
        
        # nt_run
        self.lib.nt_run.argtypes = [
            ctypes.c_void_p,  # ctx
            ctypes.c_void_p,  # input_data
            ctypes.c_void_p,  # output_data
            ctypes.c_size_t,  # batch_size
            ctypes.c_size_t   # seq_len
        ]
        self.lib.nt_run.restype = ctypes.c_int
        
        # nt_destroy_context
        self.lib.nt_destroy_context.argtypes = [ctypes.c_void_p]
        self.lib.nt_destroy_context.restype = None
    
    def create_context(self, config_dict: dict) -> ctypes.c_void_p:
        """Crea contexto con validación de config"""
        import json
        
        # Serializar config
        config_data = json.dumps(config_dict, sort_keys=True).encode()
        
        # Calcular hash
        config_hash = hashlib.sha256(config_data).hexdigest()
        
        # Crear contexto
        ctx = self.lib.nt_create_context(
            config_data,
            len(config_data),
            config_hash.encode()
        )
        
        if not ctx:
            raise RuntimeError("Failed to create context - config mismatch?")
        
        return ctx
    
    def run(self, ctx, input_data, output_data, batch_size, seq_len):
        """Ejecuta inferencia con validación"""
        result = self.lib.nt_run(ctx, input_data, output_data, batch_size, seq_len)
        
        if result != 0:
            raise RuntimeError(f"Inference failed with code {result}")
        
        return result
