# 10/02/2026 - O que foi feito?

- Início: 18h30
- Fim: 21h40
- Total: 3h10min

## Decisões e alinhamentos do projeto
- Padronização da ordem de apresentação dos dataframes em toda a ferramenta, garantindo consistência visual e lógica para os usuários finais.
- Redefinição conceitual do campo de quantidade, alinhando-o a um modelo cumulativo em vez de substitutivo, para refletir melhor operações incrementais reais.

## Refatorações e ajustes técnicos
- Ajuste na lógica de ordenação dos dataframes para assegurar que todas as visualizações e comparações sigam exatamente a mesma sequência de dados.
- Refatoração do processamento do campo de quantidade, substituindo a sobrescrita direta do valor persistido por uma lógica de soma ou subtração incremental baseada na entrada do usuário.
- Adequação da persistência de dados para suportar corretamente operações cumulativas sem perda de histórico implícito.

## Evoluções de UX e interface (Streamlit)
- Redução de confusão cognitiva para o usuário ao garantir que todos os dataframes sigam a mesma ordem de exibição.
- Melhoria da previsibilidade do comportamento do campo de quantidade, evitando alterações inesperadas de valores já registrados e tornando a interação mais intuitiva.