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


@app.route("/perfilcompleto/<cpf>/<senha>/<certificado>")
def obter_perfilcompleto(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    perfil = nu.get_customer()
    
    return {"dados": perfil
            }


@app.route("/transacaocredito/<cpf>/<senha>/<certificado>")
def obter_dadosdaconta(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    perfil = nu.get_card_feed()

    
    return {"dados": perfil
            }
@app.route("/extratobancario/<cpf>/<senha>/<certificado>")
def obter_extratobancario(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    perfil = nu.get_account_statements()

    
    return {"dados": perfil
            }

@app.route("/faturas/<cpf>/<senha>/<certificado>")
def obter_faturas(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    bills = nu.get_bills()

    # Percorre a lista de faturas e verifica a chave states
    return {"faturas": bills}

@app.route("/limite/<cpf>/<senha>/<certificado>")
def obter_limite(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    limit = nu.get_account_limit()

    # Print the credit limit
    print("Current credit limit:", limit)   

@app.route("/limite2/<cpf>/<senha>/<certificado>")
def obter_limite2(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    
    account_url = "https://prod-s13-facade.nubank.com.br/api/accounts"
    accounts = nu.get(account_url).json()
    account_id = accounts["items"][0]["id"]
    
    account_details_url = f"https://prod-s13-facade.nubank.com.br/api/accounts/{account_id}"
    account_details = nu.get(account_details_url).json()
    
    saldo_disponivel = account_details['saldos']['disponivel'] / 100
    
    return {"limite_disponivel": saldo_disponivel}

@app.route("/limite3/<cpf>/<senha>/<certificado>")
def obter_limite3(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    account = nu.get_account_limits()
    return {"get_account_limits": account}



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









if __name__ == "__main__":
    app.run(debug=True)
