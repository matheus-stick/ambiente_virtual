# 17/09 - O que foi feito?

##
- Inicio do trabalho: 19h00
- Finalização do trabalho: 20h55

## Mudanças no projeto
- Tivemos mais uma mudança no escopo por conta da mudança de sistema para a TOTVS. Com isso, estamos aguardando a adequaçao...
- Foco na entrega do sistema com receitas, que mostra a receita e a quantidade atual no estoque, informando se sera possivel efetuar o prato com a quantidade atual que tem no estoque
- Como a entrega que faremos inicialmente se tornou mais simples, estou utilizando até então apenas o excel como armazenamento dos dados.

## Atualizações no código
- A página entradas_saídas.py segue sem alterações, visto que com a aquisição da TOTVS não saberemos exatamente como efetuar a integração dos sistemas. Além disso, pode ser que a TOTVS já entregue isso.
- Criamos o arquivo receitas_cadastro.py, onde gera uma página no streamlit que permitirá que o usuário crie uma receita de algum novo prato, utilizando os produtos salvos no sistema. Esse resultado será salvo em um excel chamado receitas.xlsx.
- Criamos um receitas.py que será o local onde o usuário irá avaliar se as receitas criadas através do menu anterior têm produtos suficientes para serem executadas. Para poder efetuar essa validação, a base de consumos será um excel com todos os produtos e quais as respectivas quantidades de cada um dos produtos no estoque.