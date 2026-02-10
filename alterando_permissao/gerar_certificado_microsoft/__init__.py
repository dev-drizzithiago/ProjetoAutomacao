from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

class GerarCertificado:
    def __init__(self):
        pass


    def gerar_chave_privada(self):
        # Gerar chave privada
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

    def gerar_certificado_self_signed(self):
        # Gerar certificado self-signed
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"ExchangeOnlineAutomation"),
        ])




cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365 * 5))
    .sign(key, hashes.SHA256())
)

# Salvar certificado
with open("public_cert.cer", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.DER))

# Salvar chave privada
with open("private_key.pem", "wb") as f:
    f.write(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

print("Certificado criado!")