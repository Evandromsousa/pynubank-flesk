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



@app.route("/saldo/<cpf>/<senha>/<certificado>")
def consultar_saldo(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    fatura = nu.get_card_feed()

    if 'bills' not in fatura:
        return 'Não há faturas disponíveis'

    saldo = fatura['bills'][0]['summary']['balance']['amount']
    limite_disponivel = fatura['bills'][0]['summary']['due_date_balance']['amount']
    limite_total = fatura['bills'][0]['summary']['credit_limit']['amount']

    saldo_formatado = f'R$ {saldo/100:.2f}'.replace('.', ',')
    limite_formatado = f'R$ {limite_disponivel/100:.2f}'.replace('.', ',')
    limite_total_formatado = f'R$ {limite_total/100:.2f}'.replace('.', ',')

    return {"Saldo atual": saldo_formatado, "Limite disponível": limite_formatado, "Limite total": limite_total_formatado}
    
        

@app.route("/perfil/<cpf>/<senha>/<certificado>")
def obter_perfil(cpf, senha, certificado):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    perfil = nu.get_customer()

    telefone = perfil.get('phone', 'Telefone não informado')
    email = perfil['email']
    endereco = perfil.get('address', {}).get('street', '') + ', ' + perfil.get('address', {}).get('number', '') + ' - ' + perfil.get('address', {}).get('neighborhood', '') + ', ' + perfil.get('address', {}).get('city', '') + ' - ' + perfil.get('address', {}).get('state', '') + ', ' + perfil.get('address', {}).get('zipcode', '')
    data_nascimento = perfil['birth_date']
    dia_vencimento = nu.get_bill().due_date.day

    return {"Telefone": telefone,
            "E-mail": email,
            "Endereço": endereco,
            "Data de nascimento": data_nascimento,
            "Dia de vencimento da fatura": dia_vencimento}

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
