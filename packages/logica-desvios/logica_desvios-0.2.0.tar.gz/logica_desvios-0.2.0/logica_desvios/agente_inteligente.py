"""
Agente Inteligente orquestrador para o Método do Desvio.
Instancia e conecta o MLAdapter, DecisionMaker e CircuitBreakerAgent.
"""

import json
import time
import threading
from logica_desvios.circuit_breaker import CircuitBreakerAgent, CircuitBreakerOpenException
from logica_desvios.machine_learning_adapter import MLAdapter
from logica_desvios.decision_maker import DecisionMaker
from typing import Callable, Any

class AdaptiveCircuitBreakerAgent:
    """
    Orquestra o CircuitBreakerAgent, MLAdapter e DecisionMaker
    para um Circuit Breaker adaptativo e inteligente.
    """
    def __init__(self, name: str,
                 initial_failure_threshold: int = 3,
                 initial_reset_timeout: int = 60,
                 decision_interval_seconds: int = 15):
        
        self.name = name
        self.ml_adapter = MLAdapter(agent_name=name)
        self.decision_maker = DecisionMaker(
            agent_name=name,
            initial_threshold=initial_failure_threshold,
            initial_timeout=initial_reset_timeout
        )
        self.circuit_breaker = CircuitBreakerAgent(
            name=name,
            failure_threshold=initial_failure_threshold,
            reset_timeout=initial_reset_timeout,
            ml_adapter=self.ml_adapter,  # Injeta o MLAdapter
            decision_maker=self.decision_maker # Injeta o DecisionMaker (para referência, mas o loop fará a chamada)
        )
        self.decision_interval_seconds = decision_interval_seconds
        self._running = True
        self._decision_thread = None

        print(f"🤖 [{self.name}] Agente Adaptativo inicializado. "
              f"CB: {self.circuit_breaker.state}, "
              f"Threshold: {self.circuit_breaker.failure_threshold}, "
              f"Timeout: {self.circuit_breaker.reset_timeout}s")

    def _decision_loop(self):
        """Loop que periodicamente solicita decisões ao DecisionMaker."""
        while self._running:
            time.sleep(self.decision_interval_seconds)
            try:
                # O MLAdapter precisa de dados antes que o DecisionMaker possa usá-los
                ml_insights = self.ml_adapter.analyze_patterns()
                ml_insights["predicted_failure_prob"] = self.ml_adapter.predict_failure()
                ml_insights["predicted_recovery_time"] = self.ml_adapter.predict_recovery_time()

                recommendations = self.decision_maker.make_decision(
                    current_state=self.circuit_breaker.get_state(),
                    ml_insights=ml_insights,
                    current_cb_threshold=self.circuit_breaker.failure_threshold,
                    current_cb_timeout=self.circuit_breaker.reset_timeout
                )
                
                # Aplica as recomendações ao Circuit Breaker
                if recommendations.get("action") == "ADJUST_PARAMETERS":
                    self.circuit_breaker.update_parameters(
                        new_threshold=recommendations["recommended_failure_threshold"],
                        new_timeout=recommendations["recommended_reset_timeout"]
                    )
                
                if self.decision_maker.should_alert(ml_insights):
                    print(f"🚨 [{self.name}] ALERTA: Condições de falha severas detectadas!")

            except Exception as e:
                print(f"❌ [{self.name}] Erro no loop de decisão: {e}")

    def start_adaptive_learning(self):
        """Inicia o loop de decisão em uma thread separada."""
        if self._decision_thread is None or not self._decision_thread.is_alive():
            self._running = True
            self._decision_thread = threading.Thread(target=self._decision_loop, daemon=True)
            self._decision_thread.start()
            print(f"🧠 [{self.name}] Loop de decisão adaptativa iniciado.")

    def stop_adaptive_learning(self):
        """Para o loop de decisão."""
        if self._decision_thread and self._decision_thread.is_alive():
            self._running = False
            self._decision_thread.join(timeout=self.decision_interval_seconds + 2) # Espera um pouco para a thread terminar
            print(f"😴 [{self.name}] Loop de decisão adaptativa parado.")
    
    def protect(self, func: Callable) -> Callable:
        """
        Decorador para proteger uma função usando o Circuit Breaker adaptativo.
        """
        return self.circuit_breaker.protect(func)

    def get_stats(self) -> dict:
        """Retorna estatísticas combinadas do CB e ML."""
        cb_stats = self.circuit_breaker.get_stats()
        ml_stats = self.ml_adapter.analyze_patterns()
        return {**cb_stats, **ml_stats}

# Exemplo de uso
if __name__ == "__main__":
    def my_risky_operation():
        """Simula uma operação que pode falhar."""
        if time.time() % 7 < 3: # Mais propenso a falhar
            print("❌ Operação falhou!")
            raise ConnectionError("Falha simulada!")
        print("✅ Operação bem-sucedida!")
        return "Dados processados"

    # 1. Instancia o Agente Adaptativo
    # Isso inicializa o MLAdapter, DecisionMaker e CircuitBreakerAgent
    adaptive_agent = AdaptiveCircuitBreakerAgent(name="processamento_dados",
                                                initial_failure_threshold=3,
                                                initial_reset_timeout=10)

    # 2. Inicia o loop de aprendizado adaptativo (em background)
    adaptive_agent.start_adaptive_learning()

    # 3. Protege a operação com o decorador do agente
    @adaptive_agent.protect
    def protected_risky_operation():
        return my_risky_operation()

    # 4. Executa a operação várias vezes
    print("\n--- Iniciando execuções ---")
    for i in range(25):
        print(f"\nTentativa {i+1} - CB: {adaptive_agent.circuit_breaker.get_state()} "
              f"(T:{adaptive_agent.circuit_breaker.failure_threshold}/R:{adaptive_agent.circuit_breaker.reset_timeout}s)")
        try:
            protected_risky_operation()
            time.sleep(0.5) # Pequeno delay
        except CircuitBreakerOpenException as e:
            print(f"🚫 {e}")
            time.sleep(1) # Espera mais se o CB estiver aberto
        except Exception as e:
            print(f"🚨 Falha externa: {e}")
            time.sleep(0.5)
            
    print("\n--- Parando loop de decisão ---")
    adaptive_agent.stop_adaptive_learning()

    print("\n--- Estatísticas Finais ---")
    print(json.dumps(adaptive_agent.get_stats(), indent=2))