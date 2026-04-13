# 2026-03-01 - O que foi feito?

 - Horário: **10:00 - 15:00**
 - Total: **05:00**

## Decisões e alinhamentos do projeto
 - Mudança na fonte e no formato dos dados de precificação, passando a considerar **quantidade por embalagem** do estoque para cálculo de custo unitário.
 - Redefinição dos campos de custos adicionais na precificação de receitas, substituindo o campo **comissões** por **frete**, alinhando a modelagem de custos à realidade operacional.

## Refatorações e ajustes técnicos
 - Ajuste de tipagem de quantidades no fluxo de estoque e precificação:
   - Conversão de `quantidade` e `quantidade_disponivel` de `float` para `int` nas validações de disponibilidade.
   - Conversão de `quantidade` de ingredientes de `float` para `int` na função de cálculo de preço da receita.
 - Refatoração do cálculo de custo dos ingredientes:
   - Implementação de custo unitário por meio de `preco_base / quantidade_embalagem`.
   - Cálculo do custo da porção via `custo_unitario * quantidade_necessaria`.
   - Simplificação das validações de unidade, concentrando a regra na unidade cadastrada no estoque.
 - Ajuste estrutural do dataframe de retorno da precificação:
   - Substituição do campo numérico `Preço Base (R$)` por label formatado (`R$ valor/quantidade_unidade`).
   - Remoção de colunas relacionadas à unidade da receita no dataframe final.
   - Manutenção de arredondamento apenas no campo `Custo da Porção (R$)`.
 - Atualização de metadados do notebook para kernel **Python 3**.
 - Inclusão de artefatos de ambiente virtual (`venv/pyvenv.cfg`) e atualização de arquivos `__pycache__` no versionamento.

## Evoluções de UX e interface (Streamlit)
 - Alteração do input de tempo de preparo:
   - Mudança de minutos (0–60) para horas (0–24).
   - Ajuste de valor padrão para `1` hora.
 - Substituição do campo **Comissões (R$)** por **Frete (R$)** na interface.
 - Atualização do cálculo do valor final do prato para incorporar o novo campo de frete.
 - Ajuste da exibição do resumo de custos com nova nomenclatura e ícone correspondente ao frete.