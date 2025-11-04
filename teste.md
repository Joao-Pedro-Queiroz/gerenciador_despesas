# Diagrama de Interação - MVP Simulado Adaptativo

```mermaid
sequenceDiagram
    participant Actor
    participant Site
    participant ServicoUsuario
    participant ServicoSimulado
    participant ServicoModelo
    participant ServicoQuestoes
    participant LLM
    participant DBSimulado
    participant DBPlano
    Actor->>Site: acessa sistema
    Site->>ServicoUsuario: cadastrar/login
    ServicoUsuario-->>Site: token JWT e info da conta
    Actor->>Site: gerar simulado
    Site->>ServicoSimulado: gerar simulado
    ServicoSimulado->>ServicoModelo: envia ID conta
    ServicoModelo->>LLM: envia prompt
    LLM-->>ServicoModelo: retorna questoes
    ServicoModelo->>DBPlano: salva plano do aluno
    ServicoModelo-->>ServicoSimulado: retorna questoes
    ServicoSimulado->>DBSimulado: salva novo simulado
    ServicoSimulado-->>Site: retorna simulado
    Actor->>Site: responder questoes
    Actor->>Site: finalizar simulado
    Site->>ServicoSimulado: finalizar simulado
    ServicoSimulado->>ServicoQuestoes: enviar questoes
    ServicoQuestoes->>DBSimulado: atualizar questoes respondidas
    ServicoSimulado->>DBSimulado: atualizar simulado
    ServicoSimulado-->>Site: retorna simulado finalizado
```