"""
Implementação do padrão Circuit Breaker para operações resilientes.
"""

import time
import json
import os
from functools import wraps
from datetime import datetime
from typing import Callable, Any, Optional

# Importando os novos componentes
from logica_desvios.machine_learning_adapter import MLAdapter
from logica_desvios.decision_maker import DecisionMaker

# Estados do Circuit Breaker
CLOSED = "CLOSED"        # Operação normal
OPEN = "OPEN"            # Bloqueando chamadas (serviço falhou)
HALF_OPEN = "HALF_OPEN"  # Testando recuperação

# CONSTANTES DE SEGURANÇA
MIN_FAILURE_THRESHOLD = 2  # Threshold mínimo permitido
MAX_FAILURE_THRESHOLD = 10  # Threshold máximo permitido
MIN_RESET_TIMEOUT = 5  # Timeout mínimo em segundos
MAX_RESET_TIMEOUT = 300  # Timeout máximo em segundos


class CircuitBreakerAgent:
    """
    Implementa o padrão Circuit Breaker.
    
    Protege operações contra falhas em cascata, transitando entre estados:
    - CLOSED: Funcionamento normal
    - OPEN: Bloqueando operações após múltiplas falhas
    - HALF_OPEN: Testando se o serviço recuperou
    
    Agora integrado com MLAdapter e DecisionMaker para adaptabilidade.
    """
    
    def __init__(
        self, 
        name: str, 
        failure_threshold: int = 3, 
        reset_timeout: int = 60,
        ml_adapter: Optional[MLAdapter] = None,
        decision_maker: Optional[DecisionMaker] = None
    ):
        """
        Args:
            name: Nome do agente (único por serviço)
            failure_threshold: Número de falhas antes de abrir o circuito
            reset_timeout: Tempo (s) antes de tentar recuperar
            ml_adapter: Instância do MLAdapter para registrar eventos
            decision_maker: Instância do DecisionMaker para obter recomendações
        """
        self.name = name
        self.initial_failure_threshold = failure_threshold  # Guarda valor inicial
        self.initial_reset_timeout = reset_timeout
        
        # Aplica limites de segurança
        self.failure_threshold = self._clamp_threshold(failure_threshold)
        self.reset_timeout = self._clamp_timeout(reset_timeout)
        
        self.state = CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self.last_attempt_time = 0
        self.consecutive_successes = 0  # NOVO: Rastreia sucessos consecutivos
        
        self.ml_adapter = ml_adapter
        self.decision_maker = decision_maker
        
        # Arquivo de estado específico para este agente
        self._state_file = os.path.join(
            os.path.dirname(__file__),
            f"cb_state_{name}.json"
        )
        
        self._load_state()

    def _clamp_threshold(self, threshold: int) -> int:
        """Garante que threshold está dentro dos limites seguros."""
        return max(MIN_FAILURE_THRESHOLD, min(threshold, MAX_FAILURE_THRESHOLD))

    def _clamp_timeout(self, timeout: int) -> int:
        """Garante que timeout está dentro dos limites seguros."""
        return max(MIN_RESET_TIMEOUT, min(timeout, MAX_RESET_TIMEOUT))

    def _load_state(self) -> None:
        """Carrega estado persistido do disco com validação de segurança."""
        if not os.path.exists(self._state_file):
            self._save_state()
            return
        
        try:
            with open(self._state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.state = data.get("state", CLOSED)
                self.failures = data.get("failures", 0)
                self.last_failure_time = data.get("last_failure_time", 0)
                self.last_attempt_time = data.get("last_attempt_time", 0)
                self.consecutive_successes = data.get("consecutive_successes", 0)
                
                # CORREÇÃO CRÍTICA: Aplica limites de segurança ao carregar
                loaded_threshold = data.get("failure_threshold", self.failure_threshold)
                loaded_timeout = data.get("reset_timeout", self.reset_timeout)
                
                self.failure_threshold = self._clamp_threshold(loaded_threshold)
                self.reset_timeout = self._clamp_timeout(loaded_timeout)
                
                # Se os valores foram corrigidos, loga o ajuste
                if loaded_threshold != self.failure_threshold:
                    print(f"🛡️  [{self.name}] Threshold ajustado de {loaded_threshold} "
                          f"para {self.failure_threshold} (limites de segurança)")
                
                if loaded_timeout != self.reset_timeout:
                    print(f"🛡️  [{self.name}] Timeout ajustado de {loaded_timeout}s "
                          f"para {self.reset_timeout}s (limites de segurança)")
            
            # Se estava OPEN e timeout expirou, vai para HALF_OPEN
            if self.state == OPEN:
                if time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = HALF_OPEN
                    self._save_state()
                    
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  [{self.name}] Erro ao carregar estado: {e}")
            print(f"    Usando estado padrão: {CLOSED}")
            self._save_state()

    def _save_state(self) -> None:
        """Persiste estado no disco."""
        try:
            data = {
                "state": self.state,
                "failures": self.failures,
                "last_failure_time": self.last_failure_time,
                "last_attempt_time": self.last_attempt_time,
                "failure_threshold": self.failure_threshold,
                "reset_timeout": self.reset_timeout,
                "consecutive_successes": self.consecutive_successes,
                "timestamp": time.time()
            }
            
            with open(self._state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except IOError as e:
            print(f"⚠️  [{self.name}] Erro ao salvar estado: {e}")

    def _transition_to_open(self) -> None:
        """Transiciona para estado OPEN."""
        self.state = OPEN
        self.last_failure_time = time.time()
        self.failures = 0
        self.consecutive_successes = 0  # Reset sucessos
        self._save_state()
        print(f"🔴 [{self.name}] Circuit Breaker ABERTO "
              f"(timeout: {self.reset_timeout}s)")

    def _transition_to_half_open(self) -> None:
        """Transiciona para estado HALF_OPEN."""
        self.state = HALF_OPEN
        self.last_attempt_time = time.time()
        self._save_state()
        print(f"🟡 [{self.name}] Circuit Breaker MEIO-ABERTO "
              f"(testando recuperação)")

    def _transition_to_closed(self) -> None:
        """Transiciona para estado CLOSED."""
        self.state = CLOSED
        self.failures = 0
        self.last_failure_time = 0
        self.last_attempt_time = 0
        self._save_state()
        print(f"🟢 [{self.name}] Circuit Breaker FECHADO "
              f"(operação normal)")

    def success(self) -> None:
        """Registra uma operação bem-sucedida."""
        if self.state in [HALF_OPEN, CLOSED]:
            self.consecutive_successes += 1
            self._transition_to_closed()
            
            # RECUPERAÇÃO GRADUAL: Após sucessos consecutivos, aumenta threshold
            if self.consecutive_successes >= 5 and self.consecutive_successes % 5 == 0:
                new_threshold = min(
                    self.failure_threshold + 1,
                    self.initial_failure_threshold
                )
                if new_threshold != self.failure_threshold:
                    print(f"📈 [{self.name}] Recuperação detectada! "
                          f"Threshold: {self.failure_threshold} → {new_threshold}")
                    self.failure_threshold = new_threshold
                    self._save_state()

    def fail(self) -> None:
        """Registra uma falha na operação."""
        self.consecutive_successes = 0  # Reset sucessos
        
        if self.state == CLOSED:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self._transition_to_open()
            else:
                self._save_state()
                print(f"⚠️  [{self.name}] Falha {self.failures}/{self.failure_threshold}")
                
        elif self.state == HALF_OPEN:
            self._transition_to_open()

    def can_proceed(self) -> bool:
        """
        Verifica se a operação pode prosseguir.
        
        Returns:
            True se pode executar, False se bloqueado
        """
        if self.state == CLOSED:
            return True
        
        if self.state == OPEN:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self._transition_to_half_open()
                return True
            return False
        
        if self.state == HALF_OPEN:
            # Cooldown de 1 segundo entre tentativas
            if time.time() - self.last_attempt_time > 1:
                self.last_attempt_time = time.time()
                self._save_state()
                return True
            return False
        
        return False

    def get_state(self) -> str:
        """Retorna o estado atual do circuit breaker."""
        return self.state

    def get_stats(self) -> dict:
        """Retorna estatísticas do circuit breaker."""
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "failure_threshold": self.failure_threshold,
            "reset_timeout": self.reset_timeout,
            "last_failure_time": self.last_failure_time,
            "consecutive_successes": self.consecutive_successes
        }

    def update_parameters(self, new_threshold: int, new_timeout: int) -> None:
        """
        Atualiza dinamicamente os parâmetros do Circuit Breaker.
        Chamado pelo DecisionMaker com limites de segurança aplicados.
        """
        # Aplica limites de segurança
        safe_threshold = self._clamp_threshold(new_threshold)
        safe_timeout = self._clamp_timeout(new_timeout)
        
        if safe_threshold != self.failure_threshold:
            print(f"🔄 [{self.name}] Atualizando failure_threshold: "
                  f"{self.failure_threshold} -> {safe_threshold}")
            self.failure_threshold = safe_threshold
        
        if safe_timeout != self.reset_timeout:
            print(f"🔄 [{self.name}] Atualizando reset_timeout: "
                  f"{self.reset_timeout}s -> {safe_timeout}s")
            self.reset_timeout = safe_timeout
        
        self._save_state()

    def reset_to_defaults(self) -> None:
        """Reseta para valores iniciais seguros. Útil para recuperação manual."""
        print(f"🔄 [{self.name}] Resetando para valores padrão seguros...")
        self.failure_threshold = self._clamp_threshold(self.initial_failure_threshold)
        self.reset_timeout = self._clamp_timeout(self.initial_reset_timeout)
        self.failures = 0
        self.consecutive_successes = 0
        if self.state == OPEN:
            self.state = HALF_OPEN
        self._save_state()
        print(f"✅ [{self.name}] Reset completo. Threshold={self.failure_threshold}, "
              f"Timeout={self.reset_timeout}s")

    def protect(self, func: Callable) -> Callable:
        """
        Decorador para proteger uma função com o circuit breaker.
        
        Args:
            func: Função a ser protegida
            
        Returns:
            Função decorada
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            state_before = self.state
            
            if not self.can_proceed():
                # Registro do evento mesmo quando bloqueado
                if self.ml_adapter:
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    self.ml_adapter.record_event(
                        datetime.now(), False, duration, state_before, self.state
                    )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' está {self.state}. "
                    f"Operação bloqueada."
                )
            
            try:
                result = func(*args, **kwargs)
                self.success()
                
                # Registro de sucesso no MLAdapter
                if self.ml_adapter:
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    self.ml_adapter.record_event(
                        datetime.now(), True, duration, state_before, self.state
                    )
                return result
            except Exception as e:
                self.fail()
                
                # Registro de falha no MLAdapter
                if self.ml_adapter:
                    duration = (datetime.now() - start_time).total_seconds() * 1000
                    self.ml_adapter.record_event(
                        datetime.now(), False, duration, state_before, self.state
                    )
                raise e
        
        return wrapper


class CircuitBreakerOpenException(Exception):
    """
    Exceção levantada quando o circuit breaker está OPEN ou HALF_OPEN
    e bloqueia uma operação.
    """
    pass