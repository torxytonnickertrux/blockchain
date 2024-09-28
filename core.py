import logging
import sqlite3
from hashlib import sha256
import time
import threading

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mutex para controle de concorrência no banco de dados
db_lock = threading.Lock()

class Block:
    def __init__(self, index, previous_hash, timestamp, data, block_hash, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = self.sanitize_data(data)
        self.hash = block_hash
        self.nonce = nonce
        logging.debug(f'Bloco criado com índice {self.index}.')

    def sanitize_data(self, data):
        if not isinstance(data, str) or len(data) == 0:
            raise ValueError("Dados do bloco devem ser uma string válida e não vazia.")
        return data

class Blockchain:
    def __init__(self):
        self.chain = []
        self.init_db()  # Inicializa o banco de dados e tabelas
        self.load_blocks()  # Carrega os blocos da cadeia
        if not self.chain:
            self.create_genesis_block()
        logging.info('Blockchain inicializada.')

    def init_db(self):
        # Inicializa a conexão com o banco e cria as tabelas, caso não existam
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS blocks
                              (block_index INTEGER PRIMARY KEY, previous_hash TEXT, timestamp REAL, data TEXT, hash TEXT, nonce INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS wallets
                              (address TEXT PRIMARY KEY, owner TEXT, balance REAL)''')
            conn.commit()
            conn.close()

    def load_blocks(self):
        # Carrega os blocos do banco de dados para a memória
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM blocks ORDER BY block_index')
            rows = cursor.fetchall()
            for row in rows:
                if len(row) == 6:  # Validação de formato
                    block = Block(row[0], row[1], row[2], row[3], row[4], row[5])
                    self.chain.append(block)
                else:
                    logging.warning(f'Registro ignorado, formato inválido: {row}')
            logging.info(f'{len(rows)} blocos carregados do banco de dados.')
            conn.close()

    def save_block(self, block):
        # Salva um novo bloco no banco de dados
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO blocks (block_index, previous_hash, timestamp, data, hash, nonce) VALUES (?, ?, ?, ?, ?, ?)',
                           (block.index, block.previous_hash, block.timestamp, block.data, block.hash, block.nonce))
            conn.commit()
            conn.close()

    def create_genesis_block(self):
        # Cria o bloco gênesis se não existir
        if self.get_block_by_index(0) is not None:
            logging.info("Bloco gênesis já existe.")
            return
        genesis_block = Block(0, "0", time.time(), "Bloco Gênesis", self.calculate_hash(0, "0", time.time(), "Bloco Gênesis"))
        self.chain.append(genesis_block)
        self.save_block(genesis_block)
        logging.info("Bloco gênesis criado.")

    def add_block(self, data):
        # Adiciona um novo bloco à cadeia
        last_block = self.chain[-1]
        new_index = last_block.index + 1
        new_timestamp = time.time()
        new_hash = self.calculate_hash(new_index, last_block.hash, new_timestamp, data)
        new_block = Block(new_index, last_block.hash, new_timestamp, data, new_hash)
        self.chain.append(new_block)
        self.save_block(new_block)
        logging.info(f'Bloco {new_index} adicionado à blockchain.')

    def calculate_hash(self, index, previous_hash, timestamp, data):
        return sha256(f'{index}{previous_hash}{timestamp}{data}'.encode()).hexdigest()

    def get_block_by_index(self, index):
        # Busca um bloco pelo índice
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM blocks WHERE block_index = ?', (index,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return Block(row[0], row[1], row[2], row[3], row[4], row[5])
            return None

class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.address = sha256(owner.encode()).hexdigest()[:34]
        self.balance = 0.0
        self.save_wallet()

    def save_wallet(self):
        # Salva uma nova carteira no banco de dados
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO wallets (address, owner, balance) VALUES (?, ?, ?)',
                           (self.address, self.owner, self.balance))
            conn.commit()
            conn.close()

    @staticmethod
    def load_wallets():
        wallets = {}
        # Carrega todas as carteiras do banco de dados
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM wallets')
            rows = cursor.fetchall()
            for row in rows:
                wallet = Wallet(row[1])
                wallet.address = row[0]
                wallet.balance = row[2]
                wallets[wallet.address] = wallet
            conn.close()
        logging.info(f'{len(wallets)} carteiras carregadas.')
        return wallets

    def add_funds(self, amount):
        # Adiciona fundos à carteira
        self.balance += amount
        self.update_balance()

    def subtract_funds(self, amount):
        # Subtrai fundos da carteira
        self.balance -= amount
        self.update_balance()

    def update_balance(self):
        # Atualiza o saldo da carteira no banco de dados
        with db_lock:
            conn = sqlite3.connect('blockchain.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('UPDATE wallets SET balance = ? WHERE address = ?', (self.balance, self.address))
            conn.commit()
            conn.close()
