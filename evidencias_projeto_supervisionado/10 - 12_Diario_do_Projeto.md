# 12/10 - O que foi feito?

##
- Inicio do trabalho: 10h40
- Finalização do trabalho: 13h40
INTERVALO
- Reinicio do trabalho: 

## Mudanças no projeto
- Inclusão da página de alteração de estoque, no qual o usuário poderá acessar os dados do excel e alterar no próprio sistema, sem a necessidade de abrir o excel para fazer isso (por mais que essa possa ser uma opção válida ainda).
- Integração entre todas as 3 páginas: A página de ajuste_estoque lê os dados diretamente do excel e permite edição nas quantidades em estoque. A página receitas_cadastro cria receitas a partir do produtos listados na dimensão. Por final, a página receitas mostra se determinada receita, criada na página citada anteriormente, existe e se existir quais as quantidades de ingredientes que precisa, isso será verificado na base de dados do estoque.
## Atualizações no código
- Definição de cada página como uma função, para chamar elas no arquivo streamlit_app.py
- Ajuste na página de cadastro de receitas para aumentar a possibilidade até 20 ingredientes ao invés de 10
- Ajuste nas funções de db_utils para leitura, alteração e salvamento dos dados (para praticamente todas as paginas)
- Criação da página de ajuste_estoque
- Integração entre as 3 paginas