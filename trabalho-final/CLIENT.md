# Tutorial de Configuração de Cliente LDAP no Ubuntu

## 1. Instalação do pacote de cliente LDAP

Para iniciar, abra um terminal e execute o seguinte comando para instalar o pacote de cliente LDAP:

```bash
sudo apt install ldap-utils -y
```

Agora que o pacote está instalado, podemos nos conectar ao servidor LDAP e realizar algumas operações.

- Comando para buscar todas as entradas no servidor LDAP:

```bash
ldapsearch -H ldap://xx.xx.xx.xx -x * -b dc=konoha,dc=jp
```

- Versão com autenticação para buscar todas as entradas:

```bash
ldapsearch -H ldap://xx.xx.xx.xx -x -D "cn=hokage,dc=konoha,dc=jp" -w "sua_senha" -b "dc=konoha,dc=jp" "(objectclass=*)"
```

- Alterar a senha de um usuário:

```bash
ldappasswd -H ldap://xx.xx.xx.xx -D "cn=hokage,dc=konoha,dc=jp" -W -x "uid=carolina,ou=ic-ciencia-computacao,o=ic,o=ccmn,dc=konoha,dc=jp"
```

## 2. Instalação de bibliotecas de autenticação

Agora, vamos instalar as bibliotecas necessárias para autenticação:

```bash
sudo apt install etckeeper
sudo apt install libnss-ldap
```

Durante a instalação de `libnss-ldap`, você será solicitado a preencher informações sobre o servidor de autenticação usando um instalador interativo.

### Configurações do sistema para autenticação

1. Edite o arquivo `/etc/nsswitch.conf`:

```bash
sudo vi /etc/nsswitch.conf
```

Altere as linhas referentes a `passwd`, `group`, e `shadow` para ficarem como abaixo:

```
passwd:         compat ldap
group:          compat ldap
shadow:         compat ldap
```

2. Para criar uma pasta ao efetuar login, edite o arquivo `/etc/pam.d/common-session`:

```bash
sudo vi /etc/pam.d/common-session
```

Adicione a seguinte linha ao final do arquivo:

```
session required	pam_mkhomedir.so skel=/etc/skel umask=077
```

3. Instale as bibliotecas adicionais e atualize as configurações:

```bash
sudo apt install libpam-ldapd # versão mais recente que libpam-ldap
sudo apt install nscd
sudo apt install nslcd

sudo pam-auth-update

sudo systemctl restart nscd
sudo systemctl restart nslcd
```

Após essas etapas, reinicie o sistema:

```bash
sudo reboot
```

Depois de reiniciar, você pode fazer login com o usuário configurado no servidor LDAP:

```bash
su - carolina
Password:
carolina@openldap:~$
```

Este tutorial cobre os passos básicos para configurar um cliente LDAP no Ubuntu.


Este tutorial assume que você está substituindo os valores `xx.xx.xx.xx`, `cn=hokage`, `dc=konoha`, `ou=ic-ciencia-computacao`, `uid=carolina`, `o=ic,o=ccmn` e `sua_senha` pelos valores reais correspondentes ao seu ambiente LDAP. Certifique-se de ajustar esses valores de acordo com a sua configuração.a