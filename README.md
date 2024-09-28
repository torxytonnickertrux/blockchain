# Projeto de Criptomoeda - AistenCoin

Este projeto implementa uma criptomoeda chamada AistenCoin, utilizando conceitos fundamentais de blockchain e segurança. A AistenCoin permite a criação de carteiras, realização de transações e mineração de blocos, garantindo a integridade e segurança da cadeia de blocos.

## Funcionalidades Principais

### Criação de Carteiras

Os usuários podem criar carteiras para armazenar suas criptomoedas. Cada carteira é identificada por um endereço único gerado de forma segura. A criação de carteiras é feita através da função `criar_wallet`, que valida o nome do proprietário e gera um endereço único.

### Transações

Os usuários podem realizar transações entre carteiras. A função `adicionar_transacao` permite transferir fundos de uma carteira para outra, garantindo que todas as transações sejam registradas na blockchain. O sistema limita tentativas de transações para evitar ataques de força bruta e valida os endereços das carteiras envolvidas.

### Mineração de Blocos

A mineração é o processo pelo qual novos blocos são adicionados à blockchain. A função `minerar` recompensa o minerador com uma quantidade predeterminada de AistenCoins por adicionar um novo bloco válido à cadeia. A segurança do processo de mineração é garantida pela validação dos blocos antes de serem adicionados à blockchain.

### Validação da Blockchain

A integridade da blockchain é verificada pela função `is_chain_valid`, que assegura que todos os blocos na cadeia são válidos e que os hashes são consistentes. Isso previne fraudes e garante a segurança da cadeia de blocos.

## Exemplo de Código

Aqui está um exemplo de como a criação de carteiras, transações e mineração são implementadas no código:

### Exemplo Prático do Processo

Aqui está um exemplo prático de como as criptomoedas são geradas no seu código com o método minerar. A função simula o processo de mineração ao adicionar um novo bloco na blockchain e premiar o minerador:

#### Exemplo de Código de Mineração:
```python
# Exemplo de Código de Mineração

# Inicializar a criptomoeda
aistencoin = Criptomoeda("AistenCoin")

# Criar uma carteira para o minerador
miner_address = aistencoin.criar_wallet("Minerador1")

# Definir a quantidade de recompensa
reward_amount = 50.0

# Minerar um bloco e adicionar a recompensa à carteira do minerador
try:
    aistencoin.minerar(miner_address, reward_amount)
    print(f"Bloco minerado com sucesso! Recompensa de {reward_amount} AistenCoins adicionada à carteira {miner_address}.")
except ValueError as e:
    print(f"Erro: {e}")
except Exception as e:
    logging.error(f"Erro inesperado: {e}")

# Verificar o saldo da carteira do minerador
if miner_address in aistencoin.wallets:
    wallet = aistencoin.wallets[miner_address]
    print(f"Detalhes da carteira - Endereço: {wallet.address}, Saldo: {wallet.balance}")
else:
    print("Endereço de carteira inválido")

