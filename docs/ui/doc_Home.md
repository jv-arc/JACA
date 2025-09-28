# Home (/ui/Home.py)

É o entrypoint da aplicação, recebe os argumentos do terminal, e passa para adiciona classe ControlFacade que é adicionada à sessão da página. Home também exibe as páginas da aplicação

Por padrão exibe apenas page1_projeto.py, page5_configuracao.py e page6_sobre.py, caso haja um projeto carregado na sessão exibe também page2_extracao.py, page3_verificacao.py e page4_exportacao.py. 

> AINDA NÃO IMPLEMENTADO
> se receber a flag de debug exibe também a página page7_hidden.py
