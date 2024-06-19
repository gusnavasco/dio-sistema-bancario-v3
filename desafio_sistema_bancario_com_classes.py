from abc import ABC, abstractmethod
from datetime import datetime
import textwrap


class Conta:

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def historico(self):
        return self._historico
    
    @classmethod
    def nova_conta(cls, numero, cliente):
        return cls(numero, cliente)

    def sacar(self, valor):
        excedeu_saldo = valor > self.saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        
        return False
    
    def __str__(self):
        return textwrap.dedent(f"""\
                               Agência: {self._agencia}
                               Número: {self._numero}
                               Cliente: {self._cliente.nome}
                               """)


class ContaCorrente(Conta):

    def __init__(self, numero, cliente, limite, limite_saques):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len([1 for transacao in self.historico.transacoes 
                             if transacao["Tipo"] == "Saque"])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        
        else:
            return super().sacar(valor)
        
        return False


class Cliente:

    def __init__(self, endereco, nome):
        self.endereco = endereco
        self.nome = nome
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):

    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco, nome)
        self.cpf = cpf
        self.data_nascimento = data_nascimento


class Transacao(ABC):

    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):

    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):

    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Historico:

    def __init__(self):
        self._transacoes = []
        self._saldo = 0
        self._extrato = ""

    @property
    def transacoes(self):
        return self._transacoes
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def extrato(self):
        return self._extrato
    
    def adicionar_transacao(self, transacao):
        transacao_tipo = transacao.__class__.__name__
        transacao_valor = transacao.valor
        transacao_data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._transacoes.append(
            {
                "Tipo": transacao_tipo,
                "Valor": transacao_valor,
                "Data": transacao_data
            }
        )
        if transacao_tipo == "Deposito":
            self._saldo += transacao_valor
        if transacao_tipo == "Saque":
            self._saldo -= transacao_valor
        self._extrato += f"{transacao_tipo}: R$ {transacao_valor} - {transacao_data}\n"
    
    def mostrar_transacoes(self):
        print(self.extrato + f"\nSaldo Total: R$ {self.saldo}")


# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def depositar(conta, valor):
    valor_deposito = Deposito(valor)
    valor_deposito.registrar(conta)


def sacar(conta, valor):
    valor_saque = Saque(valor)
    valor_saque.registrar(conta)


def exibir_extrato(conta):
    conta.historico.mostrar_transacoes()


def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    novo_usuario = PessoaFisica(endereco, cpf, nome, data_nascimento)

    usuarios.append(novo_usuario)

    print("=== Usuário criado com sucesso! ===")

    return novo_usuario


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def criar_conta(numero_conta, usuarios, limite_por_saque, limite_de_saques):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        nova_conta = ContaCorrente(numero_conta, usuario, limite_por_saque, limite_de_saques)

        print("\n=== Conta criada com sucesso! ===")

        return nova_conta

    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")


def listar_contas(contas):
    for conta in contas:
        print(conta)


def main():
    LIMITE_SAQUES = 3

    numero_conta = 1
    limite_por_saque = 500
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))

            try:
                depositar(contas[-1], valor)
            except:
                print("Falha no depósito. Crie uma conta primeiro.")

        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))

            try:
                sacar(contas[-1], valor)
            except:
                print("Falha no saque. Crie uma conta primeiro.")

        elif opcao == "e":
            try:
                exibir_extrato(contas[-1])
            except:
                print("Falha na exibição do extrato. Crie uma conta primeiro.")

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            conta = criar_conta(numero_conta, usuarios, limite_por_saque, LIMITE_SAQUES)

            if conta:
                contas.append(conta)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


main()
