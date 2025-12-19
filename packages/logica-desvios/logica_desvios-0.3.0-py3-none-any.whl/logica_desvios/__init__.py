"""
Lógica dos Desvios - Circuit Breaker Inteligente com Machine Learning

Este módulo implementa um Circuit Breaker adaptativo que aprende com padrões
históricos e ajusta seus parâmetros automaticamente para maximizar resiliência.

Componentes principais:
    - AdaptiveCircuitBreakerAgent: Orquestrador principal (RECOMENDADO)
    - CircuitBreakerAgent: Circuit Breaker básico
    - MLAdapter: Análise de Machine Learning
    - DecisionMaker: Lógica de decisão adaptativa

Exemplo básico:
    >>> from logica_desvios import AdaptiveCircuitBreakerAgent
    >>> 
    >>> agent = AdaptiveCircuitBreakerAgent(
    ...     name="meu_servico",
    ...     initial_failure_threshold=3,
    ...     initial_reset_timeout=60
    ... )
    >>> 
    >>> agent.start_adaptive_learning()
    >>> 
    >>> @agent.protect
    >>> def operacao_critica():
    ...     return chamar_api_externa()

Autor:
    Marcos Sea (socramsea)

Licença:
    MIT License

Versão:
    0.2.0
"""

# Metadados do pacote
__version__ = "0.3.0"
__author__ = "Marcos Sea"
__email__ = "wss13.framework@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024 Marcos Sea"

# Importações dos componentes principais
from .circuit_breaker import (
    CircuitBreakerAgent,
    CircuitBreakerOpenException,
    CLOSED,
    OPEN,
    HALF_OPEN,
)

from .machine_learning_adapter import MLAdapter

from .decision_maker import DecisionMaker

from .agente_inteligente import AdaptiveCircuitBreakerAgent

# Aliases em português para facilitar uso por desenvolvedores brasileiros
AgenteInteligente = AdaptiveCircuitBreakerAgent
AgenteCircuitBreaker = CircuitBreakerAgent
AdaptadorML = MLAdapter
TomadorDecisao = DecisionMaker
CircuitBreakerAbertoException = CircuitBreakerOpenException

# Estados em português
FECHADO = CLOSED
ABERTO = OPEN
MEIO_ABERTO = HALF_OPEN

# Define o que é exportado com "from logica_desvios import *"
__all__ = [
    # ========================================
    # CLASSE PRINCIPAL (RECOMENDADA)
    # ========================================
    "AdaptiveCircuitBreakerAgent",  # Nome oficial em inglês
    "AgenteInteligente",            # Alias em português
    
    # ========================================
    # COMPONENTES INDIVIDUAIS (USO AVANÇADO)
    # ========================================
    "CircuitBreakerAgent",          # Circuit Breaker básico
    "AgenteCircuitBreaker",         # Alias em português
    
    "MLAdapter",                    # Adaptador de Machine Learning
    "AdaptadorML",                  # Alias em português
    
    "DecisionMaker",                # Tomador de decisões
    "TomadorDecisao",               # Alias em português
    
    # ========================================
    # EXCEÇÕES
    # ========================================
    "CircuitBreakerOpenException",  # Exceção quando CB está aberto
    "CircuitBreakerAbertoException",# Alias em português
    
    # ========================================
    # CONSTANTES DE ESTADO (INGLÊS)
    # ========================================
    "CLOSED",                       # Estado fechado (operação normal)
    "OPEN",                         # Estado aberto (bloqueando requisições)
    "HALF_OPEN",                    # Estado meio-aberto (testando recuperação)
    
    # ========================================
    # CONSTANTES DE ESTADO (PORTUGUÊS)
    # ========================================
    "FECHADO",                      # Alias em português
    "ABERTO",                       # Alias em português
    "MEIO_ABERTO",                  # Alias em português
]


# Função auxiliar para verificação rápida da versão
def get_version():
    """
    Retorna a versão atual do pacote.
    
    Returns:
        str: Versão no formato semântico (X.Y.Z)
    
    Example:
        >>> import logica_desvios
        >>> logica_desvios.get_version()
        '0.2.0'
    """
    return __version__


# Função auxiliar para informações do pacote
def info():
    """
    Exibe informações sobre o pacote.
    
    Example:
        >>> import logica_desvios
        >>> logica_desvios.info()
        Lógica dos Desvios v0.2.0
        ...
    """
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           LÓGICA DOS DESVIOS - CIRCUIT BREAKER INTELIGENTE           ║
╠══════════════════════════════════════════════════════════════╣
║  Versão:     {__version__:<50} ║
║  Autor:      {__author__:<50} ║
║  Licença:    {__license__:<50} ║
╠══════════════════════════════════════════════════════════════╣
║  Componentes:                                                ║
║    • AdaptiveCircuitBreakerAgent (Orquestrador Principal)   ║
║    • CircuitBreakerAgent (Circuit Breaker Básico)           ║
║    • MLAdapter (Machine Learning)                           ║
║    • DecisionMaker (Decisões Adaptativas)                   ║
╠══════════════════════════════════════════════════════════════╣
║  Features:                                                   ║
║    ✅ Threshold adaptativo (2-10)                           ║
║    ✅ Timeout adaptativo (5-300s)                           ║
║    ✅ Predição de falhas com ML                             ║
║    ✅ Recuperação gradual                                   ║
║    ✅ Análise de padrões históricos                         ║
║    ✅ Alertas por severidade                                ║
║    ✅ Persistência de estado                                ║
╚══════════════════════════════════════════════════════════════╝

Exemplo de uso:

    from logica_desvios import AdaptiveCircuitBreakerAgent
    
    agent = AdaptiveCircuitBreakerAgent(name="api_externa")
    agent.start_adaptive_learning()
    
    @agent.protect
    def minha_operacao():
        return chamar_api()

Para mais informações: https://github.com/WSS13Framework/curso-automacao-linux-resiliente-limpo
    """)


# Adiciona aliases ao __all__ para garantir que apareçam no autocomplete
__all__.extend([
    "get_version",
    "info",
])
