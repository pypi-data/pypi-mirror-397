"""
Testes básicos para o Agente Inteligente.
"""

import sys
import os

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logica_desvios.agente_inteligente import AgenteInteligente
from logica_desvios.circuit_breaker import CircuitBreakerOpenException


def test_agente_creation():
    """Testa criação do agente."""
    agente = AgenteInteligente(name="TestAgent")
    assert agente.name == "TestAgent"
    assert agente.get_state() == "CLOSED"
    print("✓ test_agente_creation passou")


def test_circuit_opens_after_failures():
    """Testa se o circuito abre após falhas."""
    agente = AgenteInteligente(
        name="TestFailures",
        initial_failure_threshold=2,
        initial_reset_timeout=5
    )
    
    # Simula 2 falhas
    agente.fail()
    agente.fail()
    
    assert agente.get_state() == "OPEN"
    print("✓ test_circuit_opens_after_failures passou")


def test_protection_decorator():
    """Testa o decorador de proteção."""
    agente = AgenteInteligente(name="TestDecorator")
    
    @agente.protect_intelligent
    def operacao_que_funciona():
        return "sucesso"
    
    resultado = operacao_que_funciona()
    assert resultado == "sucesso"
    assert agente.get_state() == "CLOSED"
    print("✓ test_protection_decorator passou")


if __name__ == "__main__":
    print("Executando testes...")
    print()
    
    test_agente_creation()
    test_circuit_opens_after_failures()
    test_protection_decorator()
    
    print()
    print("Todos os testes passaram! ✓")
