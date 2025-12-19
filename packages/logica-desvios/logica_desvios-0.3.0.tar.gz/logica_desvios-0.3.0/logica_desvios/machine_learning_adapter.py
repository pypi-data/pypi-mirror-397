"""
Adaptador de Machine Learning para análise e predição.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, Optional


class MLAdapter:
    """
    Componente de cognição do Agente Inteligente.
    
    Analisa padrões históricos e faz predições sobre:
    - Taxa de falha
    - Probabilidade de falha futura
    - Tempo de recuperação esperado
    - Padrões horários
    """
    
    def __init__(self, agent_name: str):
        """
        Args:
            agent_name: Nome do agente (para arquivo de histórico)
        """
        self.agent_name = agent_name
        self.history = pd.DataFrame(columns=[
            'timestamp', 'success', 'duration_ms',
            'state_before', 'state_after'
        ])
        
        self._history_file = os.path.join(
            os.path.dirname(__file__),
            f"ml_history_{agent_name}.json"
        )
        
        self._load_history()
        self._event_counter = 0

    def _load_history(self) -> None:
        """Carrega histórico do disco."""
        if not os.path.exists(self._history_file):
            return
        
        try:
            with open(self._history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if data:
                self.history = pd.DataFrame(data)
                self.history['timestamp'] = pd.to_datetime(
                    self.history['timestamp']
                )
                print(f"📊 [{self.agent_name}] Histórico carregado: "
                      f"{len(self.history)} eventos")
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  [{self.agent_name}] Erro ao carregar histórico: {e}")

    def _save_history(self) -> None:
        """Persiste histórico no disco (últimos 1000 eventos)."""
        try:
            # Limita a 1000 registros para performance
            df_to_save = self.history.tail(1000).copy()
            df_to_save['timestamp'] = df_to_save['timestamp'].astype(str)
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(df_to_save.to_dict('records'), f, indent=2)
                
        except IOError as e:
            print(f"⚠️  [{self.agent_name}] Erro ao salvar histórico: {e}")

    def record_event(
        self,
        timestamp: datetime,
        success: bool,
        duration_ms: float,
        state_before: str,
        state_after: str
    ) -> None:
        """
        Registra um evento de operação.
        
        Args:
            timestamp: Momento da operação
            success: Se foi bem-sucedida
            duration_ms: Duração em milissegundos
            state_before: Estado do CB antes da operação
            state_after: Estado do CB depois da operação
        """
        new_event = pd.DataFrame([{
            'timestamp': timestamp,
            'success': success,
            'duration_ms': duration_ms,
            'state_before': state_before,
            'state_after': state_after
        }])
        
        # FIX: Evita warning de concatenação com DataFrame vazio
        if self.history.empty:
            self.history = new_event.copy()
        else:
            self.history = pd.concat([self.history, new_event], ignore_index=True)
        
        self._event_counter += 1
        
        # Salva a cada 10 eventos
        if self._event_counter % 10 == 0:
            self._save_history()

    def analyze_patterns(self) -> Dict:
        """
        Analisa padrões no histórico de eventos.
        
        Returns:
            Dicionário com métricas e padrões
        """
        if self.history.empty:
            return {
                "failure_rate": 0.0,
                "avg_duration_ms": 0.0,
                "hourly_failure_pattern": {},
                "total_operations": 0,
                "total_failures": 0,
                "success_rate": 0.0
            }

        total_ops = len(self.history)
        failures = self.history[self.history['success'] == False]
        successes = self.history[self.history['success'] == True]
        
        failure_rate = len(failures) / total_ops if total_ops > 0 else 0
        success_rate = len(successes) / total_ops if total_ops > 0 else 0
        avg_duration = self.history['duration_ms'].mean()

        # Análise de padrão horário de falhas
        hourly_pattern = {}
        if not failures.empty:
            failures_copy = failures.copy()
            failures_copy['hour'] = failures_copy['timestamp'].dt.hour
            hourly_counts = failures_copy['hour'].value_counts(normalize=True)
            hourly_pattern = {str(k): round(v, 4) for k, v in hourly_counts.to_dict().items()}

        return {
            "failure_rate": round(failure_rate, 4),
            "success_rate": round(success_rate, 4),
            "avg_duration_ms": round(avg_duration, 2),
            "hourly_failure_pattern": hourly_pattern,
            "total_operations": total_ops,
            "total_failures": len(failures),
            "total_successes": len(successes)
        }

    def predict_failure(self) -> float:
        """
        Prediz probabilidade de falha baseado em padrões recentes.
        
        Returns:
            Probabilidade de falha (0.0 a 1.0)
        """
        if self.history.empty or len(self.history) < 10:
            return 0.1  # Probabilidade base

        # Analisa últimas 10 operações
        recent = self.history.tail(10)
        recent_failures = recent[recent['success'] == False]
        
        return len(recent_failures) / len(recent)

    def predict_recovery_time(self) -> float:
        """
        Prediz tempo de recuperação em segundos.
        
        Returns:
            Tempo estimado de recuperação
        """
        if self.history.empty or len(self.history) < 5:
            return 30.0  # Tempo base

        # Usa duração média das falhas como proxy
        failures = self.history[self.history['success'] == False]
        
        if not failures.empty and 'duration_ms' in failures.columns:
            avg_failure_duration = failures['duration_ms'].mean()
            return max(5.0, avg_failure_duration / 1000)  # Mínimo 5s
        
        return 30.0

    def get_recent_trend(self, window: int = 20) -> str:
        """
        Analisa tendência recente (melhorando/piorando/estável).
        
        Args:
            window: Número de operações para análise
            
        Returns:
            "improving", "degrading", ou "stable"
        """
        if len(self.history) < window:
            return "stable"
        
        recent = self.history.tail(window)
        first_half = recent.head(window // 2)
        second_half = recent.tail(window // 2)
        
        first_failure_rate = len(first_half[first_half['success'] == False]) / len(first_half)
        second_failure_rate = len(second_half[second_half['success'] == False]) / len(second_half)
        
        diff = second_failure_rate - first_failure_rate
        
        if diff < -0.1:
            return "improving"
        elif diff > 0.1:
            return "degrading"
        else:
            return "stable"