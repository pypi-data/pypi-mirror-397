#!/usr/bin/env python3
"""
Simple function API for decrypting snapshots.

Usage:
    from decrypt_function import decrypt_snapshot
    
    result = decrypt_snapshot(
        snapshot_url="https://example.com/snapshot.oleon",
        private_key="-----BEGIN PRIVATE KEY-----\n..."
    )
    
    print(result)
"""

import json
import gzip
import base64
import struct
from pathlib import Path
from typing import Any, Dict, Union
import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


def decrypt_snapshot(snapshot_source: str, private_key: str) -> Dict[str, Any]:
    """
    Decrypt a snapshot and return the decrypted data.
    
    Args:
        snapshot_source: URL or file path to the snapshot
        private_key: PEM-formatted private key string
        
    Returns:
        Decrypted snapshot data as a dictionary
        
    Example:
        >>> key = '''-----BEGIN PRIVATE KEY-----
        ... MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQgG2K+ke5t1j5
        ... ...
        ... -----END PRIVATE KEY-----'''
        >>> 
        >>> result = decrypt_snapshot(
        ...     "https://example.com/snapshot.oleon",
        ...     key
        ... )
        >>> print(result['projectId'])
    """
    # Normalize the private key (handle \n escape sequences)
    if '\\n' in private_key:
        private_key = private_key.replace('\\n', '\n')
    
    private_key = private_key.strip()
    
    # Load the snapshot
    buffer = _load_snapshot(snapshot_source)
    
    # Try JSON snapshot first, then OSNP binary
    try:
        parsed = json.loads(buffer.decode('utf-8'))
        return _decrypt_json_snapshot(parsed, private_key)
    except Exception:
        # Not JSON, try OSNP binary
        osnp_result = _decrypt_osnp_snapshot(buffer, private_key)
        return osnp_result['data']


def _load_snapshot(source: str) -> bytes:
    """Load snapshot from URL or file path."""
    # Check if it's a URL
    if source.lower().startswith(('http://', 'https://')):
        response = requests.get(source)
        if not response.ok:
            raise Exception(f"Failed to download snapshot (status {response.status_code})")
        return response.content
    
    # Otherwise treat as file path
    path = Path(source)
    if path.exists():
        return path.read_bytes()
    
    raise Exception("Snapshot source is neither a valid URL nor a readable file")


def _load_private_key(private_key_pem: str):
    """Load a private key from PEM format."""
    try:
        return serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
    except ValueError as e:
        error_msg = str(e).lower()
        if 'password' in error_msg or 'encrypted' in error_msg:
            raise ValueError("Private key appears to be encrypted. Please provide an unencrypted key.") from e
        raise ValueError(f"Failed to load private key: {e}") from e


def _decrypt_json_snapshot(payload: Dict, private_key_pem: str) -> Any:
    """Decrypt a JSON-formatted snapshot."""
    enc = payload.get('enc')
    if not enc:
        raise ValueError('Snapshot JSON missing "enc" section')
    
    wrapped_key = enc.get('wrappedKey')
    ciphertext = enc.get('ciphertext')
    nonce = enc.get('nonce')
    tag = enc.get('tag')
    compression = enc.get('compression')
    
    if not all([wrapped_key, ciphertext, nonce, tag]):
        raise ValueError('Snapshot JSON missing encryption fields')
    
    # Decode base64 values
    wrapped_key_buf = base64.b64decode(wrapped_key)
    cipher_buf = base64.b64decode(ciphertext)
    iv = base64.b64decode(nonce)
    tag_buf = base64.b64decode(tag)
    
    # Load and use private key
    private_key = _load_private_key(private_key_pem)
    
    content_key = private_key.decrypt(
        wrapped_key_buf,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Decrypt with AES-256-GCM
    cipher = Cipher(
        algorithms.AES(content_key),
        modes.GCM(iv, tag_buf),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(cipher_buf) + decryptor.finalize()
    
    # Decompress if needed
    if compression == 'gzip':
        decoded = gzip.decompress(plaintext)
    else:
        decoded = plaintext
    
    return json.loads(decoded.decode('utf-8'))


def _decode_msgpack(buffer: bytes, offset: int = 0):
    """Minimal MessagePack decoder for OSNP format."""
    if offset >= len(buffer):
        raise ValueError(f"Offset {offset} exceeds buffer length")
    
    type_byte = buffer[offset]
    
    # nil
    if type_byte == 0xc0:
        return None, offset + 1
    
    # bool
    if type_byte == 0xc2:
        return False, offset + 1
    if type_byte == 0xc3:
        return True, offset + 1
    
    # positive fixint
    if type_byte <= 0x7f:
        return type_byte, offset + 1
    
    # negative fixint
    if type_byte >= 0xe0:
        return type_byte - 0x100, offset + 1
    
    # fixstr
    if (type_byte & 0xe0) == 0xa0:
        length = type_byte & 0x1f
        offset += 1
        s = buffer[offset:offset + length].decode('utf-8')
        return s, offset + length
    
    # fixmap
    if (type_byte & 0xf0) == 0x80:
        length = type_byte & 0x0f
        offset += 1
        obj = {}
        for _ in range(length):
            key, offset = _decode_msgpack(buffer, offset)
            val, offset = _decode_msgpack(buffer, offset)
            obj[key] = val
        return obj, offset
    
    # fixarray
    if (type_byte & 0xf0) == 0x90:
        length = type_byte & 0x0f
        offset += 1
        arr = []
        for _ in range(length):
            val, offset = _decode_msgpack(buffer, offset)
            arr.append(val)
        return arr, offset
    
    # bin 8/16/32
    if type_byte == 0xc4:
        length = buffer[offset + 1]
        offset += 2
        return buffer[offset:offset + length], offset + length
    if type_byte == 0xc5:
        length = struct.unpack('>H', buffer[offset + 1:offset + 3])[0]
        offset += 3
        return buffer[offset:offset + length], offset + length
    if type_byte == 0xc6:
        length = struct.unpack('>I', buffer[offset + 1:offset + 5])[0]
        offset += 5
        return buffer[offset:offset + length], offset + length
    
    # ext formats
    if type_byte == 0xd4:
        offset += 2
        return buffer[offset:offset + 1], offset + 1
    if type_byte == 0xd5:
        offset += 2
        return buffer[offset:offset + 2], offset + 2
    if type_byte == 0xd6:
        offset += 2
        return buffer[offset:offset + 4], offset + 4
    if type_byte == 0xd7:
        offset += 2
        return buffer[offset:offset + 8], offset + 8
    if type_byte == 0xd8:
        offset += 2
        return buffer[offset:offset + 16], offset + 16
    
    if type_byte == 0xc7:
        length = buffer[offset + 1]
        offset += 3
        return buffer[offset:offset + length], offset + length
    if type_byte == 0xc8:
        length = struct.unpack('>H', buffer[offset + 1:offset + 3])[0]
        offset += 4
        return buffer[offset:offset + length], offset + length
    if type_byte == 0xc9:
        length = struct.unpack('>I', buffer[offset + 1:offset + 5])[0]
        offset += 6
        return buffer[offset:offset + length], offset + length
    
    # float/double
    if type_byte == 0xca:
        val = struct.unpack('>f', buffer[offset + 1:offset + 5])[0]
        return val, offset + 5
    if type_byte == 0xcb:
        val = struct.unpack('>d', buffer[offset + 1:offset + 9])[0]
        return val, offset + 9
    
    # uint
    if type_byte == 0xcc:
        return buffer[offset + 1], offset + 2
    if type_byte == 0xcd:
        return struct.unpack('>H', buffer[offset + 1:offset + 3])[0], offset + 3
    if type_byte == 0xce:
        return struct.unpack('>I', buffer[offset + 1:offset + 5])[0], offset + 5
    if type_byte == 0xcf:
        return struct.unpack('>Q', buffer[offset + 1:offset + 9])[0], offset + 9
    
    # str
    if type_byte == 0xd9:
        length = buffer[offset + 1]
        offset += 2
        return buffer[offset:offset + length].decode('utf-8'), offset + length
    if type_byte == 0xda:
        length = struct.unpack('>H', buffer[offset + 1:offset + 3])[0]
        offset += 3
        return buffer[offset:offset + length].decode('utf-8'), offset + length
    if type_byte == 0xdb:
        length = struct.unpack('>I', buffer[offset + 1:offset + 5])[0]
        offset += 5
        return buffer[offset:offset + length].decode('utf-8'), offset + length
    
    # array
    if type_byte == 0xdc:
        length = struct.unpack('>H', buffer[offset + 1:offset + 3])[0]
        offset += 3
        arr = []
        for _ in range(length):
            val, offset = _decode_msgpack(buffer, offset)
            arr.append(val)
        return arr, offset
    if type_byte == 0xdd:
        length = struct.unpack('>I', buffer[offset + 1:offset + 5])[0]
        offset += 5
        arr = []
        for _ in range(length):
            val, offset = _decode_msgpack(buffer, offset)
            arr.append(val)
        return arr, offset
    
    # map
    if type_byte == 0xde:
        length = struct.unpack('>H', buffer[offset + 1:offset + 3])[0]
        offset += 3
        obj = {}
        for _ in range(length):
            key, offset = _decode_msgpack(buffer, offset)
            val, offset = _decode_msgpack(buffer, offset)
            obj[key] = val
        return obj, offset
    if type_byte == 0xdf:
        length = struct.unpack('>I', buffer[offset + 1:offset + 5])[0]
        offset += 5
        obj = {}
        for _ in range(length):
            key, offset = _decode_msgpack(buffer, offset)
            val, offset = _decode_msgpack(buffer, offset)
            obj[key] = val
        return obj, offset
    
    raise ValueError(f"Unsupported msgpack type 0x{type_byte:02x}")


def _normalize_msgpack_value(value: Any) -> Any:
    """Normalize msgpack values (convert bytes to strings)."""
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.hex()
    if isinstance(value, list):
        return [_normalize_msgpack_value(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize_msgpack_value(v) for k, v in value.items()}
    return value


def _decrypt_osnp_snapshot(buffer: bytes, private_key_pem: str) -> Dict:
    """Decrypt an OSNP binary snapshot."""
    if not buffer or len(buffer) < 32:
        raise ValueError("Snapshot buffer is empty or too small")
    
    magic = buffer[0:4].decode('ascii')
    if magic != 'OSNP':
        raise ValueError("Not an OSNP snapshot")
    
    version_raw = struct.unpack('>I', buffer[4:8])[0]
    
    # Try decoding header at offset 9, fall back to 8
    header_offset = 9
    try:
        header, after_header = _decode_msgpack(buffer, header_offset)
    except Exception:
        header_offset = 8
        header, after_header = _decode_msgpack(buffer, header_offset)
    
    if not isinstance(header, dict):
        raise ValueError("Invalid OSNP header")
    
    cipher_len = struct.unpack('>I', buffer[after_header:after_header + 4])[0]
    nonce_start = after_header + 4
    nonce = buffer[nonce_start:nonce_start + 12]
    tag = buffer[nonce_start + 12:nonce_start + 28]
    ciphertext = buffer[nonce_start + 28:nonce_start + 28 + cipher_len]
    
    if len(ciphertext) != cipher_len:
        raise ValueError("Ciphertext length mismatch")
    
    # Load and use private key
    private_key = _load_private_key(private_key_pem)
    
    wrapped_key = header.get('wrappedKey')
    if not wrapped_key:
        raise ValueError("Missing wrappedKey in OSNP header")
    
    content_key = private_key.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # Decrypt
    cipher = Cipher(
        algorithms.AES(content_key),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Decompress if needed
    compression = header.get('compression')
    if compression == 'gzip':
        decoded = gzip.decompress(plaintext)
    else:
        decoded = plaintext
    
    # Try JSON first, fall back to msgpack
    try:
        data = json.loads(decoded.decode('utf-8'))
    except Exception:
        msg, _ = _decode_msgpack(decoded, 0)
        data = _normalize_msgpack_value(msg)
    
    return {
        'data': data,
        'meta': {
            'projectId': header.get('projectId'),
            'queueId': header.get('queueId'),
            'messageCount': header.get('messageCount'),
            'versionRaw': version_raw
        }
    }


