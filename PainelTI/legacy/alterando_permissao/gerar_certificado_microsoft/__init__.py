# -*- coding: utf-8 -*-
## Gerado por IA
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import hashlib
import subprocess
import os

from dotenv import load_dotenv
load_dotenv()


class GerarCertificado:
    def __init__(self, cn: str = "ExchangeOnlineAutomation"):
        self.cn = cn
        self.key = None
        self.cert: x509.Certificate | None = None

    # 1) Gerar chave privada
    def gerar_chave_privada(self, key_size: int = 2048):
        self.key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )

    # 2) Gerar certificado self-signed (com extensões úteis)
    def gerar_certificado_self_signed(self, anos_validade: int = 5):
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, self.cn),
        ])

        not_before = datetime.utcnow() - timedelta(minutes=5)  # margem
        not_after = not_before + timedelta(days=365 * anos_validade)

        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(not_before)
            .not_valid_after(not_after)
        )

        # Extensões comuns para autenticação de app (não obrigatórias no Entra ID, mas boas práticas)
        # KeyUsage: digitalSignature + keyEncipherment
        key_usage = x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False
        )
        builder = builder.add_extension(key_usage, critical=True)

        # EKU (opcional; para este cenário geralmente não é exigido)
        # extended_ku = x509.ExtendedKeyUsage([
        #     ExtendedKeyUsageOID.CLIENT_AUTH,
        #     ExtendedKeyUsageOID.SERVER_AUTH
        # ])
        # builder = builder.add_extension(extended_ku, critical=False)

        # BasicConstraints (não é CA)
        builder = builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )

        # Assinar com SHA256
        self.cert = builder.sign(private_key=self.key, algorithm=hashes.SHA256())

    # 3) Exportar certificado público em DER (.cer)
    def salvar_certificado_der(self, caminho_cer: str):
        with open(caminho_cer, "wb") as f:
            f.write(self.cert.public_bytes(serialization.Encoding.DER))

    # 4) Exportar certificado público em PEM (Base64, também aceito pelo Entra ID)
    def salvar_certificado_pem(self, caminho_pem: str):
        with open(caminho_pem, "wb") as f:
            f.write(self.cert.public_bytes(serialization.Encoding.PEM))

    # 5) Exportar chave privada em PEM (sem senha ou com senha)
    def salvar_chave_privada_pem(self, caminho_key_pem: str, senha: str | None = None):
        if senha:
            enc = serialization.BestAvailableEncryption(senha.encode("utf-8"))
        else:
            enc = serialization.NoEncryption()
        with open(caminho_key_pem, "wb") as f:
            f.write(
                self.key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=enc
                )
            )

    # 6) Exportar PFX (PKCS#12) com senha
    def salvar_pfx(self, caminho_pfx: str, senha: str, friendly_name: str | None = None):
        # O friendly_name precisa ser bytes (sem Unicode fora de ASCII em algumas ferramentas)
        name_bytes = (friendly_name or self.cn).encode("utf-8", errors="ignore")
        pfx_bytes = pkcs12.serialize_key_and_certificates(
            name=name_bytes,
            key=self.key,
            cert=self.cert,
            cas=None,  # sem cadeia
            encryption_algorithm=serialization.BestAvailableEncryption(senha.encode("utf-8")),
        )
        with open(caminho_pfx, "wb") as f:
            f.write(pfx_bytes)

    # 7) Obter thumbprint (SHA1) a partir do DER
    def get_thumbprint_sha1(self) -> str:
        der = self.cert.public_bytes(serialization.Encoding.DER)
        return hashlib.sha1(der).hexdigest().upper()

    # 8) (Opcional) Instalar no CurrentUser\My via PowerShell (Windows)
    def instalar_no_windows_currentuser_my(self, caminho_pfx: str, senha: str) -> None:
        # Requer PowerShell disponível no PATH
        ps = f'''
            $password = ConvertTo-SecureString "{senha}" 
            -AsPlainText -Force
            Import-PfxCertificate -FilePath "{caminho_pfx}" 
            -CertStoreLocation "Cert:\\CurrentUser\\My" 
            -Password $password -Exportable | Out-Null
        '''
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True
        )


if __name__ == '__main__':
    # Ajuste estes caminhos conforme o seu projeto:
    OUT_DIR = r"C:\Temp"  # use um diretório existente
    os.makedirs(OUT_DIR, exist_ok=True)

    CER_DER = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.cer")   # DER
    CER_PEM = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.pem")   # PEM (opcional para upload no Entra ID)
    KEY_PEM = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.key")   # chave privada (use com proteção/segurança)
    PFX_PATH = os.path.join(OUT_DIR, "ExchangeOnlineAutomation.pfx")  # PFX para o seu app
    PFX_PASSWORD = f"{os.getenv('')}"

    g = GerarCertificado(cn="ExchangeOnlineAutomation")
    g.gerar_chave_privada()
    g.gerar_certificado_self_signed(anos_validade=5)

    # Exportações
    g.salvar_certificado_der(CER_DER)        # ✅ suba este .cer no App Registration
    g.salvar_certificado_pem(CER_PEM)        # (opcional) alternativa em PEM/Base64
    g.salvar_chave_privada_pem(KEY_PEM)      # (opcional) se precisar em PEM
    g.salvar_pfx(PFX_PATH, PFX_PASSWORD, friendly_name="MeuApp-Autenticacao (Exportable)")

    # (Opcional) instalar no store do usuário (Windows)
    g.instalar_no_windows_currentuser_my(PFX_PATH, PFX_PASSWORD)

    print("Certificado criado!")
    print("Thumbprint (SHA1):", g.get_thumbprint_sha1())
    print("Arquivos:")
    print("  CER (DER):", CER_DER)
    print("  PEM (cert):", CER_PEM)
    print("  KEY (privada PEM):", KEY_PEM)
    print("  PFX:", PFX_PATH)