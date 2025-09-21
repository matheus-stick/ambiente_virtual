# 02/09 - O que foi feito?

##
- Inicio do trabalho: 19h30
- Finalização do trabalho: 20h45

## Mudanças no projeto
- Mudança do layout da página de entradas_saidas.py, melhorando o texto e o alinhamento nos campos descritivos que devem ser preenchidos.
- Criação de um código único para streamlit_app que consolidará o st.navigation para permitir a navegação entre as páginas criadas (por enquanto apenas entradas_saidas/py). Essa parte ainda não foi finalizada pois estou enfrentando dificuldades durante a configuração visto que o st.navigation não existe na versão que estou usando do streamlit. Não posso evoluir para uma versão que tenha ela, pois se torna incompatível com outra biblioteca que tenho instalada. Por isso, precisarei retomar um método antigo que utilizei em outra aplicação. 

## Atualizações no código
- Deleção do arquivo cadastros.py
- Mudança das funções _norm e filtra_produtos para db_utils, centralizando todas as funções dentro desse arquivo.
- Alteração no st.columns do entradas_saidas.py para ajuste de ordem dos campos.
- Refatoração do código streamlit_app.py para centralizar todas as páginas. Essa parte segue ainda com erro, mas tratarei na próxima manutenção.