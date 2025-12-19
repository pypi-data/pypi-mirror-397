#!/usr/bin/env python3
"""
Exemplos de uso do logica-desvios

Este arquivo demonstra diferentes formas de usar o pacote,
desde o básico até casos avançados.
"""

import time
import random
from typing import Dict, Any


# ============================================================================
# EXEMPLO 1: Uso Básico (Nome em Inglês)
# ============================================================================

def exemplo_1_basico_ingles():
    """Exemplo mais simples - Circuit Breaker básico"""
    print("\n" + "="*70)
    print("EXEMPLO 1: Uso Básico (Inglês)")
    print("="*70)
    
    from logica_desvios import AdaptiveCircuitBreakerAgent
    
    # Cria o agente
    agent = AdaptiveCircuitBreakerAgent(
        name="exemplo_basico",
        initial_failure_threshold=3,
        initial_reset_timeout=10
    )
    
    # Define operação que pode falhar
    @agent.protect
    def operacao_instavel():
        if random.random() < 0.4:  # 40% de chance de falha
            raise ConnectionError("Serviço temporariamente indisponível")
        return {"status": "ok", "data": [1, 2, 3]}
    
    # Executa várias vezes
    for i in range(10):
        try:
            resultado = operacao_instavel()
            print(f"  Tentativa {i+1}: ✅ {resultado}")
        except Exception as e:
            print(f"  Tentativa {i+1}: ❌ {e}")
        time.sleep(0.5)
    
    print(f"\n  Estado final: {agent.circuit_breaker.get_state()}")


# ============================================================================
# EXEMPLO 2: Uso com Nomes em Português
# ============================================================================

def exemplo_2_portugues():
    """Exemplo usando aliases em português"""
    print("\n" + "="*70)
    print("EXEMPLO 2: Uso em Português")
    print("="*70)
    
    from logica_desvios import AgenteInteligente, CircuitBreakerAbertoException
    
    # Cria o agente (mesmo que AdaptiveCircuitBreakerAgent)
    agente = AgenteInteligente(
        name="exemplo_portugues",
        initial_failure_threshold=2,
        initial_reset_timeout=5
    )
    
    @agente.protect
    def buscar_dados_externos():
        if random.random() < 0.5:
            raise TimeoutError("Timeout na API")
        return {"usuarios": 150, "status": "ativo"}
    
    for i in range(8):
        try:
            dados = buscar_dados_externos()
            print(f"  {i+1}. Sucesso: {dados}")
        except CircuitBreakerAbertoException as e:
            print(f"  {i+1}. Circuit Breaker aberto: {e}")
        except Exception as e:
            print(f"  {i+1}. Erro: {e}")
        time.sleep(0.3)


# ============================================================================
# EXEMPLO 3: Com Aprendizado Adaptativo
# ============================================================================

def exemplo_3_aprendizado_adaptativo():
    """Exemplo com loop de decisão ML ativo"""
    print("\n" + "="*70)
    print("EXEMPLO 3: Aprendizado Adaptativo")
    print("="*70)
    
    from logica_desvios import AdaptiveCircuitBreakerAgent
    
    agent = AdaptiveCircuitBreakerAgent(
        name="exemplo_ml",
        initial_failure_threshold=3,
        initial_reset_timeout=10
    )
    
    # IMPORTANTE: Inicia o loop de aprendizado
    agent.start_adaptive_learning()
    
    @agent.protect
    def processar_pedido(pedido_id: int) -> Dict[str, Any]:
        # Simula falhas mais frequentes em horários de pico
        hora_atual = time.localtime().tm_hour
        chance_falha = 0.6 if 12 <= hora_atual <= 14 else 0.3
        
        if random.random() < chance_falha:
            raise RuntimeError(f"Erro ao processar pedido {pedido_id}")
        
        return {"pedido_id": pedido_id, "status": "processado"}
    
    print("  Executando com aprendizado ativo...")
    
    for i in range(15):
        try:
            resultado = processar_pedido(i + 1)
            print(f"  [{i+1}] ✅ Pedido processado")
        except Exception as e:
            print(f"  [{i+1}] ❌ Falha: {type(e).__name__}")
        time.sleep(0.5)
    
    # Para o loop
    agent.stop_adaptive_learning()
    
    # Exibe estatísticas
    stats = agent.get_stats()
    print(f"\n  📊 Estatísticas:")
    print(f"     • Threshold atual: {stats['failure_threshold']}")
    print(f"     • Timeout atual: {stats['reset_timeout']}s")
    print(f"     • Taxa de falha: {stats['failure_rate']*100:.1f}%")
    print(f"     • Total de operações: {stats['total_operations']}")


# ============================================================================
# EXEMPLO 4: Caso de Uso Real - Backup Automático
# ============================================================================

def exemplo_4_backup_automatico():
    """Exemplo realista - Sistema de backup resiliente"""
    print("\n" + "="*70)
    print("EXEMPLO 4: Backup Automático Resiliente")
    print("="*70)
    
    from logica_desvios import AdaptiveCircuitBreakerAgent
    
    # Agent para proteger operações de backup
    backup_agent = AdaptiveCircuitBreakerAgent(
        name="backup_system",
        initial_failure_threshold=2,  # Mais sensível
        initial_reset_timeout=30      # Espera mais
    )
    
    backup_agent.start_adaptive_learning()
    
    @backup_agent.protect
    def fazer_backup(arquivo: str) -> bool:
        """Simula backup que pode falhar (disco cheio, rede, etc)"""
        # Simula diferentes tipos de falha
        rand = random.random()
        
        if rand < 0.2:
            raise IOError("Disco cheio")
        elif rand < 0.3:
            raise TimeoutError("Timeout na rede")
        elif rand < 0.35:
            raise PermissionError("Sem permissão")
        
        print(f"     ✅ Backup de '{arquivo}' concluído")
        return True
    
    arquivos = [
        "database.sql", "logs.tar.gz", "config.json",
        "images.zip", "documents.pdf", "cache.db"
    ]
    
    sucessos = 0
    falhas = 0
    
    for arquivo in arquivos:
        print(f"\n  📦 Tentando backup: {arquivo}")
        try:
            fazer_backup(arquivo)
            sucessos += 1
        except Exception as e:
            print(f"     ❌ Falha: {type(e).__name__}: {e}")
            falhas += 1
        time.sleep(1)
    
    backup_agent.stop_adaptive_learning()
    
    print(f"\n  📊 Resultado final:")
    print(f"     • Sucessos: {sucessos}/{len(arquivos)}")
    print(f"     • Falhas: {falhas}/{len(arquivos)}")
    
    stats = backup_agent.get_stats()
    print(f"     • Estado CB: {stats['state']}")
    print(f"     • Threshold ajustado: {stats['failure_threshold']}")


# ============================================================================
# EXEMPLO 5: Múltiplos Agentes (Microserviços)
# ============================================================================

def exemplo_5_multiplos_agentes():
    """Exemplo com múltiplos circuit breakers para diferentes serviços"""
    print("\n" + "="*70)
    print("EXEMPLO 5: Múltiplos Serviços (Microserviços)")
    print("="*70)
    
    from logica_desvios import AdaptiveCircuitBreakerAgent
    
    # Um agente para cada serviço
    agent_auth = AdaptiveCircuitBreakerAgent(name="servico_auth", initial_failure_threshold=2)
    agent_pagamento = AdaptiveCircuitBreakerAgent(name="servico_pagamento", initial_failure_threshold=3)
    agent_email = AdaptiveCircuitBreakerAgent(name="servico_email", initial_failure_threshold=5)
    
    @agent_auth.protect
    def autenticar_usuario(user_id: int):
        if random.random() < 0.2:
            raise ConnectionError("Auth service down")
        return {"user_id": user_id, "token": "abc123"}
    
    @agent_pagamento.protect
    def processar_pagamento(valor: float):
        if random.random() < 0.3:
            raise TimeoutError("Payment gateway timeout")
        return {"status": "approved", "valor": valor}
    
    @agent_email.protect
    def enviar_email(destinatario: str):
        if random.random() < 0.4:
            raise ConnectionError("SMTP error")
        return {"enviado": True, "destinatario": destinatario}
    
    # Simula fluxo de pedido
    for i in range(5):
        print(f"\n  🛒 Pedido #{i+1}")
        
        try:
            auth = autenticar_usuario(i + 100)
            print(f"     ✅ Autenticação OK")
        except Exception as e:
            print(f"     ❌ Auth falhou: {type(e).__name__}")
            continue
        
        try:
            pagamento = processar_pagamento(99.90)
            print(f"     ✅ Pagamento OK")
        except Exception as e:
            print(f"     ❌ Pagamento falhou: {type(e).__name__}")
            continue
        
        try:
            email = enviar_email(f"user{i}@example.com")
            print(f"     ✅ Email enviado")
        except Exception as e:
            print(f"     ❌ Email falhou: {type(e).__name__}")
        
        time.sleep(0.5)
    
    # Exibe status de cada serviço
    print(f"\n  📊 Status dos serviços:")
    print(f"     • Auth: {agent_auth.circuit_breaker.get_state()}")
    print(f"     • Pagamento: {agent_pagamento.circuit_breaker.get_state()}")
    print(f"     • Email: {agent_email.circuit_breaker.get_state()}")


# ============================================================================
# EXEMPLO 6: Usando info() para ver informações
# ============================================================================

def exemplo_6_info_pacote():
    """Exemplo mostrando informações do pacote"""
    print("\n" + "="*70)
    print("EXEMPLO 6: Informações do Pacote")
    print("="*70)
    
    import logica_desvios
    
    # Mostra versão
    print(f"\n  Versão: {logica_desvios.get_version()}")
    
    # Mostra informações completas
    logica_desvios.info()


# ============================================================================
# MAIN - Executa todos os exemplos
# ============================================================================

def main():
    """Executa todos os exemplos"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  LOGICA-DESVIOS - EXEMPLOS DE USO".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    exemplos = [
        ("Básico (Inglês)", exemplo_1_basico_ingles),
        ("Português", exemplo_2_portugues),
        ("Aprendizado Adaptativo", exemplo_3_aprendizado_adaptativo),
        ("Backup Automático", exemplo_4_backup_automatico),
        ("Múltiplos Serviços", exemplo_5_multiplos_agentes),
        ("Info do Pacote", exemplo_6_info_pacote),
    ]
    
    for i, (nome, funcao) in enumerate(exemplos, 1):
        try:
            funcao()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro no exemplo '{nome}': {e}")
        
        if i < len(exemplos):
            input("\n  ⏸️  Pressione ENTER para continuar...")
    
    print("\n" + "█"*70)
    print("█" + "  FIM DOS EXEMPLOS".center(68) + "█")
    print("█"*70 + "\n")


if __name__ == "__main__":
    main()
