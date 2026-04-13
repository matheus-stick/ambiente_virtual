# 02/09 - O que foi feito?

##
- Inicio do trabalho: 18h30
- Finalização do trabalho: 21:00

## Mudanças no projeto
- Mudança da página, deixando-a menos engessada
    - Pagina anterior complicava o cadastro de produto pois haviam diversos campos. Ela foi pensada dessa maneira pra aprofundar o nivel de analise, mas revisitamos o conceito e iremos ter um trade-off entre menos analise e mais user experience na interface.
- Criacao de tabela dimensao para produtos, a partir do que ja existe
    - Acessamos a ferramenta que utilizam hoje e exportamos os campos que já haviam sido cadastrados

## Atualizações no código
- Desativamos por enquanto a página de cadastro, diminuindo uma das páginas pra termos uma experiência melhor.
- Trabalhamos apenas em cima da pagina entradas_saidas.py por enquanto para criarmos a opção de ser inserido um produto de maneira textual e já buscar quais opções próximas existem.
- Ajustamos a db_utils para criar uma função que sempre retornará o dataframe dim_produtos, com as colunas padronizadas sem acento e minúscula.
- Desativamos os arquivos categorias.csv, fornecedores.csv e marcas.csv . Provavelmente não serão mais necessários, por enquanto os deixei na pasta mas pretendo remove-lôs nos próximos dias.
- Inclusao de bibliotecas como unidecode para padronização dos textos. Inclusão da openpyxl pra leitura de excel.
- Precisamos ajustar o requirements por incompatibilidade de versão entre as bibliotecas.