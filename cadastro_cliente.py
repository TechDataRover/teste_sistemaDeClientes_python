import csv
import re
from datetime import datetime
from fpdf import FPDF
from validate_docbr import CPF

# Classe Cliente
class Cliente:
    def __init__(self, nome, cpf, email, endereco, numero, complemento, telefone):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.endereco = endereco
        self.numero = numero
        self.complemento = complemento
        self.telefone = telefone

    def __str__(self):
        return f"Nome: {self.nome}, CPF: {self.cpf}, Email: {self.email}, Endereço: {self.endereco}, Número: {self.numero}, Complemento: {self.complemento}, Telefone: {self.telefone}"

# Funções de Validação
def validar_cpf(cpf):
    cpf_validator = CPF()
    return cpf_validator.validate(cpf)

def validar_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

def input_com_valida(prompt, validacao_func=None, mensagem_erro="Entrada inválida. Tente novamente.", min_len=None, max_len=None):
    """
    Solicita uma entrada ao usuário e valida com uma função fornecida.
    Retorna o valor validado ou None se o usuário optar por voltar ao menu.
    """
    while True:
        valor = input(prompt).strip()
        
        # Verifica comprimento mínimo
        if min_len and len(valor) < min_len:
            print(f"A entrada deve ter pelo menos {min_len} caracteres.")
            continue

        # Verifica comprimento máximo
        if max_len and len(valor) > max_len:
            print(f"A entrada deve ter no máximo {max_len} caracteres.")
            continue

        # Valida usando a função fornecida
        if validacao_func:
            resultado = validacao_func(valor)
            if resultado:
                return valor
            else:
                print(mensagem_erro)
                opcao = input("Digite novamente ou 0 para voltar ao menu: ").strip()
                if opcao == '0':
                    return None
        else:
            if valor:
                return valor
            else:
                print("Este campo é obrigatório. Tente novamente.")

# Função para Gerar PDFs
def gerar_pdf(cliente, data, tipo, motivo_exclusao=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"{'Cadastro de Cliente' if tipo == 'cadastro' else 'Exclusão de Cliente'}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Nome: {cliente.nome}", ln=True)
    pdf.cell(200, 10, txt=f"CPF: {cliente.cpf}", ln=True)
    pdf.cell(200, 10, txt=f"E-mail: {cliente.email}", ln=True)
    pdf.cell(200, 10, txt=f"Endereço: {cliente.endereco}, Número: {cliente.numero}", ln=True)
    pdf.cell(200, 10, txt=f"Complemento: {cliente.complemento}", ln=True)
    pdf.cell(200, 10, txt=f"Telefone: {cliente.telefone}", ln=True)
    pdf.cell(200, 10, txt=f"Data de {'Emissão' if tipo == 'cadastro' else 'Exclusão'}: {data}", ln=True)
    
    if tipo == "exclusao":
        pdf.cell(200, 10, txt=f"Motivo da Exclusão: {motivo_exclusao}", ln=True)

    nome_arquivo = f"{tipo}_{cliente.cpf}.pdf"
    pdf.output(nome_arquivo)

# Funções de Persistência
def salvar_dados_em_csv(clientes, nome_arquivo='clientes.csv'):
    """
    Salva os dados dos clientes em um arquivo CSV.
    """
    with open(nome_arquivo, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "CPF", "Email", "Endereço", "Número", "Complemento", "Telefone"])
        for cliente in clientes.values():
            writer.writerow([cliente.nome, cliente.cpf, cliente.email, cliente.endereco, cliente.numero, cliente.complemento, cliente.telefone])

def carregar_dados_de_csv(nome_arquivo='clientes.csv'):
    """
    Carrega os dados dos clientes a partir de um arquivo CSV.
    """
    clientes = {}
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cpf = re.sub(r'\D', '', row["CPF"])  # Remove formatação do CPF
                cliente = Cliente(row["Nome"], row["CPF"], row["Email"], row["Endereço"], row["Número"], row["Complemento"], row["Telefone"])
                clientes[cpf] = cliente
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado. Iniciando com clientes vazios.")
    return clientes

# Funções do Menu
def cadastrar_cliente(clientes):
    """
    Solicita ao usuário os dados de um cliente e cadastra no sistema.
    """
    nome = input_com_valida("Digite o nome completo: ", min_len=6, max_len=30)
    if nome is None:
        return
    
    cpf = input_com_valida("Digite o CPF do cliente (apenas números): ", validar_cpf, "CPF inválido. Tente novamente.")
    if cpf is None:
        return

    if cpf in clientes:
        print("Cliente já cadastrado.")
        return

    email = input_com_valida("Digite o e-mail do cliente: ", validar_email, "E-mail inválido. Tente novamente.")
    if email is None:
        return

    endereco = input_com_valida("Digite o endereço do cliente: ")
    if endereco is None:
        return

    numero = input_com_valida("Digite o número do endereço: ")
    if numero is None:
        return

    complemento = input("Digite o complemento do endereço (opcional): ").strip()

    telefone = input_com_valida("Digite o telefone do cliente (no formato DDD + número, apenas números): ", lambda t: len(t) >= 10, "Telefone inválido. Tente novamente.")
    if telefone is None:
        return
    
    cliente = Cliente(nome, cpf, email, endereco, numero, complemento, telefone)
    clientes[cpf] = cliente
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    gerar_pdf(cliente, data_emissao, "cadastro")
    print("Cliente cadastrado com sucesso! PDF gerado.")

def excluir_cliente(clientes):
    """
    Solicita o CPF de um cliente para exclusão e gera um PDF com os dados da exclusão.
    """
    while True:
        cpf_input = input_com_valida("Digite o CPF do cliente a ser excluído (apenas números): ", lambda c: c in clientes, "Cliente não encontrado. Verifique o CPF e tente novamente.")
        if cpf_input is None:
            return
        
        motivo_exclusao = input("Digite o motivo da exclusão: ").strip()
        if not motivo_exclusao:
            print("O motivo da exclusão é obrigatório. Tente novamente.")
            continue
        
        data_exclusao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        cliente = clientes.pop(cpf_input, None)  # Remove o cliente do dicionário e evita KeyError
        
        if cliente:
            gerar_pdf(cliente, data_exclusao, "exclusao", motivo_exclusao)
            print("Cliente excluído com sucesso! PDF gerado.")
            break
        else:
            print("Cliente não encontrado. Verifique o CPF e tente novamente.")
            opcao = input("Digite novamente ou 0 para voltar ao menu: ").strip()
            if opcao == '0':
                return

def menu():
    """
    Exibe o menu principal e permite ao usuário escolher ações.
    """
    clientes = carregar_dados_de_csv()

    while True:
        print("\nMenu:")
        print("1. Cadastrar Cliente")
        print("2. Excluir Cliente")
        print("3. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            cadastrar_cliente(clientes)
        elif opcao == '2':
            excluir_cliente(clientes)
        elif opcao == '3':
            salvar_dados_em_csv(clientes)
            print("Dados salvos com sucesso. Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
