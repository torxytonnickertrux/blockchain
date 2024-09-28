from core import Block, Blockchain
import logging
import pytest

# Configuração do logger para exibir mensagens no console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def testar_block():
    logging.info("Iniciando teste da classe Block")
    bloco_teste = Block(1, "0", 1234567890.0, "Dados de Teste", "hash_teste")
    logging.info(f"Testando atributos do bloco: {bloco_teste.__dict__}")
    assert bloco_teste.index == 1, f"Esperado index 1, mas obteve {bloco_teste.index}"
    assert bloco_teste.previous_hash == "0", f"Esperado previous_hash '0', mas obteve {bloco_teste.previous_hash}"
    assert bloco_teste.timestamp == 1234567890.0, f"Esperado timestamp 1234567890.0, mas obteve {bloco_teste.timestamp}"
    assert bloco_teste.data == "Dados de Teste", f"Esperado data 'Dados de Teste', mas obteve {bloco_teste.data}"
    assert bloco_teste.hash == "hash_teste", f"Esperado hash 'hash_teste', mas obteve {bloco_teste.hash}"
    logging.info("Teste da classe Block concluído com sucesso")

def testar_blockchain():
    logging.info("Iniciando teste da classe Blockchain")
    blockchain_teste = Blockchain()
    blockchain_teste.create_genesis_block()
    blockchain_teste.add_block("Primeiro bloco após o gênesis")
    logging.info("Testando tamanho da blockchain")
    assert len(blockchain_teste.chain) == 2, f"Esperado tamanho 2, mas obteve {len(blockchain_teste.chain)}"
    logging.info("Testando dados dos blocos na blockchain")
    assert blockchain_teste.chain[0].data == "Genesis Block", f"Esperado 'Genesis Block', mas obteve {blockchain_teste.chain[0].data}"
    assert blockchain_teste.chain[1].data == "Primeiro bloco após o gênesis", f"Esperado 'Primeiro bloco após o gênesis', mas obteve {blockchain_teste.chain[1].data}"
    for bloco in blockchain_teste.chain:
        logging.info(f"Bloco na Blockchain: {bloco.__dict__}")
    logging.info("Teste da classe Blockchain concluído com sucesso")

if __name__ == "__main__":
    pytest.main()
