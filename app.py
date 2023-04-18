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




def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color=Fore.BLUE):
    print(f'{color}{Style.DIM}[*] {Style.NORMAL}{Fore.LIGHTBLUE_EX}{message}')


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())






app = Flask(__name__)




@app.route("/")
def inicial():
    
    return {"Status": "API FUNCIONANDO"}


junto = {}

junto = []



@app.route("/certificado/<cpf>/<senha>")
def main(cpf, senha):
    init()

    log(f'Starting {Fore.MAGENTA}{Style.DIM}PLAY SERVER{Style.NORMAL}{Fore.LIGHTBLUE_EX} context creation.')

    device_id = generate_random_id()

    log(f'Generated random id: {device_id}')

    cpf = cpf
    password = senha

    generator = CertificateGenerator(cpf, password, device_id) ## AQUI GERA O CODIGO PRA ENVIAR 

    junto2 = {cpf : {"cpf": cpf, "chave": generator}}
    
    log(f'Requesting e-mail code')
    try:
        email = generator.request_code() # AQUI ELE ENVIA O CODIGO PARA O EMAIL
    except NuException:
        log(f'{Fore.RED}Failed to request code. Check your credentials!', Fore.RED)
        return

    log(f'Email sent to {Fore.LIGHTBLACK_EX}{email}{Fore.LIGHTBLUE_EX}')

    for i, item in enumerate(junto):
        if cpf in item:
            junto.pop(i)
            break

    junto.append(junto2)
    
    return {"email": email}



@app.route("/limite/<cpf>/<senha>/<certificado>")
def consultar_limite(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)    

# Verifique o limite disponível
    card_limit = nu.get_card_limit()
    available_credit_limit = card_limit['available_credit_limit']
    
    return {"Limite disponivel": available_credit_limit}
 
@app.route("/perfil/<cpf>/<senha>/<certificado>")
def obter_perfil(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    perfil = nu.get_customer()
    debito = nu.get_account_balance()

    telefone = perfil.get('phone', 'Telefone não informado')
    email = perfil['email']
    
    return {"telefone": telefone,
            "email": email,
            "debito": debito
            }



@app.route("/codigo/<codigo>/<cpf>")
def enviarcodigo(codigo, cpf):

   
    code = codigo
    cpf = cpf

    for item in junto:
        if cpf in item:
            if "chave" in item[cpf]:
                chave = item[cpf]["chave"]
                cert1, cert2 = chave.exchange_certs(code)
                save_cert(cert1, (codigo+'.p12'))
                print(f'{Fore.GREEN}Certificates generated successfully. (cert.pem)')
                print(f'{Fore.YELLOW}Warning, keep these certificates safe (Do not share or version in git)')
                return {"mensagem": "Certificado Gerado com sucesso!"}
            else:
                log(f'Chave "chave" não encontrada para o CPF {cpf}')
        else:
                log(f'CPF {cpf} não encontrado')



@app.route("/balance/<cpf>/<senha>/<certificado>")
def SaldoDisponivel(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    debito = nu.get_account_balance()


    return {"Saldo": debito}


@app.route("/credito/<cpf>/<senha>/<certificado>")
def credito(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    card = nu.get_card()


    return jsonfy.dumps(card)
   








if __name__ == "__main__":
    app.run(debug=True)
