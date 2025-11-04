# Diagrama de Interação - MVP Simulado Adaptativo

```mermaid
sequenceDiagram
    autonumber

    participant Actor
    participant Site
    participant ServicoUsuario
    participant ServicoSimulado
    participant ServicoModelo
    participant ServicoQuestoes
    participant LLM
    participant DB_Simulado
    participant DB_Plano

    Actor -> Site: acessa sistema
    Site -> ServicoUsuario: cadastrar / login
    ServicoUsuario --> Site: token JWT + info da conta

    Actor -> Site: gerar simulado
    Site -> ServicoSimulado: gerar simulado
    ServicoSimulado -> ServicoModelo: envia ID conta
    ServicoModelo -> LLM: envia prompt
    LLM --> ServicoModelo: retorna questoes
    ServicoModelo -> DB_Plano: salva plano do aluno
    ServicoModelo --> ServicoSimulado: retorna questoes
    ServicoSimulado -> DB_Simulado: salva novo simulado
    ServicoSimulado --> Site: retorna simulado

    Actor -> Site: responder questoes

    Actor -> Site: finalizar simulado
    Site -> ServicoSimulado: finalizar simulado
    ServicoSimulado -> ServicoQuestoes: enviar questoes
    ServicoQuestoes -> DB_Simulado: atualizar questoes respondidas
    ServicoSimulado -> DB_Simulado: atualizar simulado
    ServicoSimulado --> Site: retorna simulado finalizado
```