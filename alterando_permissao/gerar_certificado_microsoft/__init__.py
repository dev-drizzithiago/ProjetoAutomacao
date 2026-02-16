from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import hashlib
import subprocess
import os


private_key = 'private_key.pem'
public_key = 'public_cert.cer'

class GerarCertificado:
    def __init__(self):

        self.cn = None
        self.key = None
        self.cert = None

    def gerar_chave_privada(self):
        # Gerar chave privada
        self.key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

    def gerar_certificado_self_signed(self, anos_validade: int = 5):
        # Gerar certificado self-signed
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"ExchangeOnlineAutomation"),
        ])

        not_before = datetime.utcnow() - timedelta(minutes=5)  # margem
        not_after = not_before + timedelta(days=365 * anos_validade)

        self.cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365 * 5))
            .sign(self.key, hashes.SHA256())
        )

    def salvar_certificado(self):
        # Salvar certificado
        with open(f"../{public_key}", "wb") as f:
            f.write(self.cert.public_bytes(serialization.Encoding.DER))

    def salvar_chave_privada(self):
        # Salvar chave privada
        with open(f"../{private_key}", "wb") as f:
            f.write(
                self.key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )



if __name__ == '__main__':
    init_obj_gerar_certificado = GerarCertificado()
    init_obj_gerar_certificado.gerar_chave_privada()
    init_obj_gerar_certificado.gerar_certificado_self_signed(5)
    init_obj_gerar_certificado.salvar_certificado()
    init_obj_gerar_certificado.salvar_chave_privada()

    print("Certificado criado!")