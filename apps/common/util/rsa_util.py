# coding=utf-8
"""
    @project: maxkb
    @Author：The Tiger
    @file： rsa_util.py
    @date：2023/11/3 11:13
    @desc:
"""
import base64
import threading

from Crypto.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Crypto.PublicKey import RSA
from django.core import cache
from django.db.models import QuerySet

from setting.models import SystemSetting, SettingType

lock = threading.Lock()
rsa_cache = cache.caches['default']
cache_key = "rsa_key"
# Encryption of the key.
secret_code = "mac_kb_password"


def generate():
    """
    produced The private key.
    :return:{key:'The Public Key',value:'The private key'}
    """
    # Create one. 2048 The key.
    key = RSA.generate(2048)

    # Get a private key.
    encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                                   protection="scryptAndAES128-CBC")
    return {'key': key.publickey().export_key(), 'value': encrypted_key}


def get_key_pair():
    rsa_value = rsa_cache.get(cache_key)
    if rsa_value is None:
        lock.acquire()
        rsa_value = rsa_cache.get(cache_key)
        if rsa_value is not None:
            return rsa_value
        try:
            rsa_value = get_key_pair_by_sql()
            rsa_cache.set(cache_key, rsa_value)
        finally:
            lock.release()
    return rsa_value


def get_key_pair_by_sql():
    system_setting = QuerySet(SystemSetting).filter(type=SettingType.RSA.value).first()
    if system_setting is None:
        kv = generate()
        system_setting = SystemSetting(type=SettingType.RSA.value,
                                       meta={'key': kv.get('key').decode(), 'value': kv.get('value').decode()})
        system_setting.save()
    return system_setting.meta


def encrypt(msg, public_key: str | None = None):
    """
    Cryptocurrency
    :param msg:        Crypto data
    :param public_key: The Public Key
    :return: Data after encryption
    """
    if public_key is None:
        public_key = get_key_pair().get('key')
    cipher = PKCS1_cipher.new(RSA.importKey(public_key))
    encrypt_msg = cipher.encrypt(msg.encode("utf-8"))
    return base64.b64encode(encrypt_msg).decode()


def decrypt(msg, pri_key: str | None = None):
    """
    disclosure
    :param msg: Required data disclosure
    :param pri_key: The private key
    :return: Data after disclosure
    """
    if pri_key is None:
        pri_key = get_key_pair().get('value')
    cipher = PKCS1_cipher.new(RSA.importKey(pri_key, passphrase=secret_code))
    decrypt_data = cipher.decrypt(base64.b64decode(msg), 0)
    return decrypt_data.decode("utf-8")


def rsa_long_encrypt(message, public_key: str | None = None, length=200):
    """
    Extremely Long Text Encryption

    :param message:         Requires a encrypted string.
    :param public_key   The Public Key
    :param length:      1024bitThe certificate.100， 2048bitThe certificate. 200
    :return: Data after encryption
    """
    # Read the public key.
    if public_key is None:
        public_key = get_key_pair().get('key')
    cipher = PKCS1_cipher.new(RSA.importKey(extern_key=public_key,
                                            passphrase=secret_code))
    # Processed：Plaintext is too long. Section of encryption
    if len(message) <= length:
        # Encryption of coded data.，and passedbase64to code.
        result = base64.b64encode(cipher.encrypt(message.encode('utf-8')))
    else:
        rsa_text = []
        # Cut the data after coding.，Causes：The encryption length cannot be too long.
        for i in range(0, len(message), length):
            cont = message[i:i + length]
            # Encryption of data after cutting.，and newly addedtextbehind.
            rsa_text.append(cipher.encrypt(cont.encode('utf-8')))
        # Encryption is complete.
        cipher_text = b''.join(rsa_text)
        # base64to code.
        result = base64.b64encode(cipher_text)
    return result.decode()


def rsa_long_decrypt(message, pri_key: str | None = None, length=256):
    """
    Extremely long text.，Not encrypted.
    :param  message:    Required data disclosure
    :param  pri_key:    The Secret Key
    :param  length :     1024bitThe certificate.128，2048bitThe certificate256The place
    :return: Data after disclosure
    """
    if pri_key is None:
        pri_key = get_key_pair().get('value')
    cipher = PKCS1_cipher.new(RSA.importKey(pri_key, passphrase=secret_code))
    base64_de = base64.b64decode(message)
    res = []
    for i in range(0, len(base64_de), length):
        res.append(cipher.decrypt(base64_de[i:i + length], 0))
    return b"".join(res).decode()
