"""
Ao receber uma nova conexão de um cliente, seleciona um servidor
para atender essa conexão e repassa os dados pro servidor. Deve implementar duas políticas de escolha: (i) Round-Robin;
(ii) Least Connections. Apenas uma política de escolha deve permanecer ativa por vez,
definindo durante a inicialização do LB.
Possivelmente há casos de teste que só passem com uma das políticas
então precisaremos implementar as 2.
"""