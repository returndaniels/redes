# README - Construção de um Servidor Web com Programação Socket

Este repositório contém o código-fonte de um servidor web simples desenvolvido como parte da atividade de "Construção de um Servidor Web com Programação Socket" na disciplina de Redes de Computadores (2023/2). Veja a tarefa completa em [Tarefa2graduacao](./github/Tarefa2graduacao.pdf).

## Sobre o Projeto

O objetivo deste projeto é criar um servidor web básico que utiliza programação de socket em Python para atender a solicitações de clientes web. O servidor é capaz de responder a solicitações HTTP, fornecendo páginas da web solicitadas ou retornando um erro "404 Not Found" se a página não existir. O código foi baseado nos exemplos de programação de sockets cliente/servidor do livro texto "Computer Networking: Principles, Protocols and Practice" (https://gaia.cs.umass.edu/kurose_ross/programming/simple_socket/K_R_sockets_in_Java.pdf).

## Laboratório Prático

Este projeto também inclui um laboratório prático baseado em um roteiro disponibilizado no seguinte link: [WebServer Programming Lab](https://gaia.cs.umass.edu/kurose_ross/programming/Python_code_only/WebServer_programming_lab_only.pdf). No entanto, o laboratório foi modificado para atender aos seguintes requisitos específicos:

1. **Página de Login:** Em vez de implementar os exercícios opcionais de multithread e cliente, decidimos implementar uma página de login básica no servidor. O cliente (navegador) captura as informações de usuário e senha inseridas e as envia para o servidor.

2. **Verificação de Usuário:** O servidor verifica se o usuário e a senha correspondem a um usuário pré-cadastrado no servidor. Se forem válidos, o usuário é autenticado e uma segunda página web é apresentada no navegador. A página acessada também inclui uma opção de "logoff".

3. **Tratamento de Erro:** Se as credenciais inseridas não corresponderem a um usuário cadastrado, o servidor responde com o erro "404 Not Found".

## Executando o Servidor

Para executar o servidor, siga as instruções abaixo:

1. **Populando o Banco de Dados:** Primeiro, execute o script `db_seeder.py` para popular o banco de dados. Use o seguinte comando:

```python
python db_seeder.py
```

Isso criará um banco de dados de usuários e definirá a senha padrão para todos os usuários como `"senha123"`.
#### Usuários
```
[{ username: 'usuario1', password: 'senha123' },
 { username: 'usuario2', password: 'senha123' },
 { username: 'usuario3', password: 'senha123' }]
```


2. **Executando o Servidor:** Após popular o banco de dados, execute o programa `WebServer.py` para levantar o servidor. O servidor estará disponível em "localhost:3000" ou "127.0.0.1:3000". Para acessar de outros dispositivos na mesma rede, você precisa saber o IP do computador onde o servidor está rodando, por exemplo, `"192.168.1.3:3000"`.

```python
python WebServer.py
```

Este projeto serve como uma introdução básica à criação de servidores web usando programação de socket em Python. É apenas um exemplo de servidor web simples e não cobre todos os aspectos de um servidor web completo, como autenticação segura e autorização, manipulação de múltiplas solicitações simultâneas, entre outros.
