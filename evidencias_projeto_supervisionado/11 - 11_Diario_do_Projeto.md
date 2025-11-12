# 03/11 - O que foi feito?

##
- Inicio do trabalho: 20h00
- Finalização do trabalho: 21h30

## Mudanças no projeto
- Continuação da inclusão de preços nos produtos do estoque. Agora na aba de alteração de estoque tem a possibilidade de preencher com um novo produto ou alterar um já existente, informando o preço em cada um dos casos. Essa alteração já muda diretamente o excel que é consumido pelo sistema.
- Inclusão das logotipos da Estância dos Ventos e da marca no rodapé de cada página.
## Atualizações no código
- Atuação no 'ajuste_estoque.py' para adicionar uma etapa de informar o valor do novo produto. Cada uma delas conta com uma progress bar para passar a sensação de alteração gradativa, por mais que o ajuste é instantâneo após o clique, visto que não demanda processamento de larga escala pois é uma operação extremamente simples. 
Está permitido também fazer a alteração de um produto já existente no "banco de dados".
Para próximos passos, precisamos incluir nessa mesma página a opção de deletar o registro de um determinado produto de dentro do excel.
- Ajuste no streamlit_app.py para adicionar as logotipos no sidebar e a marca no rodapé