"""
Decision Maker - Lógica de decisão adaptativa do Circuit Breaker.
"""

from typing import Dict


class DecisionMaker:
    """
    Analisa insights do MLAdapter e decide ajustes nos parâmetros do Circuit Breaker.
    """
    
    # Limites de segurança
    MIN_THRESHOLD = 2
    MAX_THRESHOLD = 10
    MIN_TIMEOUT = 5
    MAX_TIMEOUT = 300
    
    def __init__(self, agent_name: str, initial_threshold: int = 3, initial_timeout: int = 60):
        """
        Args:
            agent_name: Nome do agente
            initial_threshold: Threshold inicial (valor de referência)
            initial_timeout: Timeout inicial (valor de referência)
        """
        self.agent_name = agent_name
        self.initial_threshold = max(initial_threshold, self.MIN_THRESHOLD)
        self.initial_timeout = max(initial_timeout, self.MIN_TIMEOUT)
        self.last_decision = None

    def make_decision(
        self,
        current_state: str,
        ml_insights: Dict,
        current_cb_threshold: int,
        current_cb_timeout: int
    ) -> Dict:
        """
        Toma decisão sobre ajustes baseado em insights de ML.
        
        Args:
            current_state: Estado atual do CB
            ml_insights: Métricas do MLAdapter
            current_cb_threshold: Threshold atual
            current_cb_timeout: Timeout atual
            
        Returns:
            Dicionário com recomendações
        """
        failure_rate = ml_insights.get("failure_rate", 0.0)
        predicted_failure = ml_insights.get("predicted_failure_prob", 0.0)
        
        # Aplica limites de segurança aos valores atuais
        safe_threshold = max(self.MIN_THRESHOLD, min(current_cb_threshold, self.MAX_THRESHOLD))
        safe_timeout = max(self.MIN_TIMEOUT, min(current_cb_timeout, self.MAX_TIMEOUT))
        
        recommended_threshold = safe_threshold
        recommended_timeout = safe_timeout
        action = "MONITOR"
        
        # Lógica de decisão baseada em taxa de falha
        if failure_rate > 0.7 or predicted_failure > 0.8:
            # Situação crítica: reduz threshold
            recommended_threshold = max(safe_threshold - 1, self.MIN_THRESHOLD)
            recommended_timeout = min(safe_timeout + 10, self.MAX_TIMEOUT)
            action = "ADJUST_PARAMETERS"
            
            print(f"🔻 [{self.agent_name}] Threshold: {safe_threshold} → "
                  f"{recommended_threshold} (alta taxa de falha detectada ou predita)")
        
        elif failure_rate < 0.2 and predicted_failure < 0.3:
            # Situação saudável: aumenta threshold gradualmente
            recommended_threshold = min(safe_threshold + 1, self.initial_threshold)
            recommended_timeout = max(safe_timeout - 5, self.MIN_TIMEOUT)
            
            if recommended_threshold != safe_threshold or recommended_timeout != safe_timeout:
                action = "ADJUST_PARAMETERS"
                print(f"📈 [{self.agent_name}] Sistema saudável. "
                      f"Threshold: {safe_threshold} → {recommended_threshold}")
        
        self.last_decision = {
            "action": action,
            "recommended_failure_threshold": recommended_threshold,
            "recommended_reset_timeout": recommended_timeout,
            "reasoning": f"failure_rate={failure_rate:.2f}, predicted={predicted_failure:.2f}"
        }
        
        return self.last_decision

    def should_alert(self, ml_insights: Dict) -> bool:
        """
        Decide se deve emitir alerta baseado em condições críticas.
        
        Args:
            ml_insights: Métricas do MLAdapter
            
        Returns:
            True se deve alertar
        """
        failure_rate = ml_insights.get("failure_rate", 0.0)
        predicted_failure = ml_insights.get("predicted_failure_prob", 0.0)
        
        # Alerta em condições severas
        return failure_rate > 0.8 or predicted_failure > 0.9