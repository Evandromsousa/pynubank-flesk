from flask import Flask, jsonify
from pynubank import Nubank, MockHttpClient
import os
import random
import string
from getpass import getpass
import json
from colorama import init, Fore, Style

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator




# def generate_random_id() -> str:
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


# def log(message, color=Fore.BLUE):
#     print(f'{color}{Style.DIM}[*] {Style.NORMAL}{Fore.LIGHTBLUE_EX}{message}')


# def save_cert(cert, name):
#     path = os.path.join(os.getcwd(), name)
#     with open(path, 'wb') as cert_file:
#         cert_file.write(cert.export())






app = Flask(__name__)



def init():
generators = []

def log(message, color=Fore.LIGHTBLUE_EX):
cprint(message, color)

def generate_random_id():
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
return ''.join(choice(letters) for i in range(16))

@app.route("/certificado/<cpf>/<senha>")
def main(cpf, senha):
    init()

    log(f'Starting {Fore.MAGENTA}{Style.DIM}PLAY SERVER{Style.NORMAL}{Fore.LIGHTBLUE_EX} context creation.')

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    cpf = cpf
    password = senha

    generator = CertificateGenerator(cpf, password, device_id)

    log('Requesting e-mail code')
    try:
        email = generator.request_code()
    except NuException:
        log(f'{Fore.RED}Failed to request code. Check your credentials!', Fore.RED)
        return jsonify({"error": "Failed to request code. Check your credentials."})

    log(f'Email sent to {Fore.LIGHTBLACK_EX}{email}{Fore.LIGHTBLUE_EX}')
    generators.append(generator)

    return {"Email": email}

    # @app.route("/balance/{cpf}/{senha}/{certificado}")
# def SaldoDisponivel(cpf: int, senha: str,certificado: str):
#     nu = Nubank()
#     nu.authenticate_with_cert(cpf, senha, certificado)
#     saldo = nu.get_account_balance()

#     return {"Saldo": saldo}
# @app.route("/")
# def inicial():
   
#     return {"Status": "Api Funcionando!"}



# @app.get("/codigo/{codigo}")

# def enviarcodigo(codigo: str):
#     try:
#         code = codigo
#         cert1, cert2 = generators[-1].exchange_certs(code)
#         save_cert(cert1, (codigo+'.p12'))

#         print(f'{Fore.GREEN}Certificates generated successfully. (cert.pem)')
#         print(f'{Fore.YELLOW}Warning, keep these certificates safe (Do not share or version in git)')
#         return {"mensagem": "Certificado Gerado com Sucesso!"}
#     except Exception as e:
#             # trate o erro aqui
#             print("Ocorreu um erro:", e)

#             return "Ocorreu um erro"







if __name__ == "__main__":
    app.run(debug=True)
