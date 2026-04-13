# 2026-03-31 - O que foi feito?

## ⏱️ Horários
 - Início: 09h
 - Fim: 17h
 - Total: 8h 00min

## Decisões e alinhamentos do projeto
 - Padronização do uso de componentes visuais personalizados em substituição aos componentes nativos do Streamlit, visando maior controle de estilo e consistência visual
 - Definição de desacoplamento da estilização da sidebar em um módulo dedicado (`styles.py`), promovendo reutilização e melhor organização do código
 - Reorganização da navegação principal da aplicação, priorizando a funcionalidade de alteração de estoque na ordem de uso
 - Ajuste na lógica de resumo de receitas para refletir corretamente a contagem de itens (baseado na quantidade de produtos ao invés da soma de quantidades)

## Refatorações e ajustes técnicos
 - Alteração da função `_resumir_receita` para substituir soma de quantidades por contagem de produtos
 - Remoção de valores padrão nos parâmetros `prefixo_medida` das funções `card_metric` e `card_metric_big`, tornando o uso mais explícito e controlado
 - Refatoração da chamada de `card_metric_big` para suportar prefixo separado do valor
 - Extração da lógica de estilização da sidebar para o módulo `functions/styles.py`
 - Remoção de código duplicado e limpeza da implementação anterior de estilos inline no `streamlit_app.py`
 - Ajuste na ordem das páginas no menu lateral
 - Atualização de tooltips no gráfico de precificação, removendo informação redundante
 - Alteração de cor do gráfico de barras para adequação à nova identidade visual

## Evoluções de UX e interface (Streamlit)
 - Implementação de identidade visual mais consistente com uso de gradientes e paleta personalizada
 - Criação de sidebar com aparência mais moderna e leve, incluindo:
   - fundo com gradientes suaves
   - estados de hover e seleção mais claros
   - tipografia customizada (Montserrat)
 - Melhoria na hierarquia visual dos inputs e campos interativos
 - Ajuste visual dos cards de métricas para melhor legibilidade e destaque de valores monetários
 - Padronização de cores alinhadas à identidade do projeto (tons de rosa e variações suaves)
 - Simplificação das informações exibidas em gráficos para reduzir ruído cognitivo