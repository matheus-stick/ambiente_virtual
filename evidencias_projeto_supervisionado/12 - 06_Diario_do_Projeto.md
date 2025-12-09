# 06/12 - O que foi feito?

##
- Inicio do trabalho: 10h00
- Finalização do trabalho: 14h00

## Mudanças no projeto
- Finalização do módulo de precificação na aba de consultas de estoque, permitindo visualizar tudo o que gasta APENAS com os ingredientes de acordo com cada porção.
- Alteramos algumas premissas de cadastro na aba de cadastro de estoque, permitindo subir um valor sem quantidade, apenas com preço, para habilitar fazer um levantamento de preços mesmo que o produto não exista no estoque ainda.

## Atualizações no código
- Atuação no db_utils.py para criação de nova função que permitisse avaliar a precificação de cada receita.
- Inclusão da chamada da nova função para o arquivo consulta_receitas, incluindo ao final com st.info o resultado do custo dos ingredientes de acordo com a porção.