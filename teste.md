# Diagrama de Interação - MVP Simulado Adaptativo

```mermaid
sequenceDiagram
    autonumber

    participant Actor
    participant Site
    participant ServUsuario as "Serviço do Usuário"
    participant ServSimulado as "Serviço do Simulado"
    participant ServModelo as "Serviço do Modelo"
    participant ServQuestoes as "Serviço de Questões"
    participant LLM as "Serviço de Terceiro LLM"
    participant MDB_Simulado as "MongoDB Simulado"
    participant MDB_Plano as "MongoDB Plano do Aluno"

    %% ====== Fluxo de Acesso e Autenticação ======
    Actor --> Site: Acessa sistema
    Site --> ServUsuario: Cadastrar/logar conta
    ServUsuario ---> Site: Token JWT + Informações da conta

    %% ====== Fluxo de Geração de Simulado Adaptativo ======
    Actor --> Site: Solicita gerar simulado adaptativo
    Site --> ServSimulado: Gerar simulado adaptativo
    ServSimulado --> ServModelo: Envia ID conta
    ServModelo --> LLM: Envia Prompt
    LLM ---> ServModelo: Retorna Questões
    ServModelo --> MDB_Plano: Salva plano do aluno
    ServModelo ---> ServSimulado: Retorna Questões
    ServSimulado --> MDB_Simulado: Salva novo simulado
    ServSimulado ---> Site: Retorna Simulado

    %% ====== Responder questões ======
    Actor --> Site: Responde questões do simulado

    %% ====== Finalização do Simulado ======
    Actor --> Site: Finalizar Simulado
    Site --> ServSimulado: Finalizar Simulado
    ServSimulado --> ServQuestoes: Enviar Questões
    ServQuestoes --> MDB_Simulado: Atualizar questões respondidas
    ServSimulado --> MDB_Simulado: Atualizar simulado
    ServSimulado ---> Site: Retorna Simulado Finalizado
