## Tutorial de Instalação e Configuração do OpenLDAP no CentOS (Servidor)

### 1. Instalação e Configuração Inicial

Para iniciar, é necessário instalar o OpenLDAP e suas dependências no CentOS:

```bash
yum install openldap openldap-clients openldap-servers -y
systemctl enable slapd
systemctl start slapd
```

Para verificar se o serviço está ativo e aguardando conexões na porta LDAP (389), utilize o comando:

```bash
ss -ln | grep 389
```

Os arquivos de configuração do OpenLDAP podem ser encontrados em "/etc/openldap/". É importante ressaltar que os arquivos de configuração gerados automaticamente só devem ser editados utilizando o comando `ldapmodify`.

#### 1.1. Geração de Senha

Para gerar uma senha para o administrador do OpenLDAP:

```bash
cd ~
slappasswd > senha_root
```

#### 1.2. Configuração dos Arquivos

##### 1.2.1. Arquivo do Banco de Dados (DB)

Crie ou edite o arquivo `db.ldif`, e insira o conteúdo de [db.ldif](db.ldif):

```bash
cd ~
vi db.ldif
```

Após colar o conteúdo do arquivo, ajuste a última linha para que a senha esteja presente em `olcRootPW`, e então utilize o comando `ldapmodify` para aplicar as configurações:

```bash
cat senha_root > db.ldif
ldapmodify -H ldapi:/// -f db.ldif
```

##### 1.2.2. Arquivo de Monitoramento (MONITOR)

Crie ou edite o arquivo `monitor.ldif`, e insira o conteúdo de [monitor.ldif](monitor.ldif):

```bash
vi monitor.ldif
```

Aplique as configurações utilizando o comando `ldapmodify`:

```bash
ldapmodify -H ldapi:/// -f monitor.ldif
```

#### 1.3. Importação de Plugins

Importe os plugins necessários:

```bash
cd /etc/openldap/schema/
ldapadd -H ldapi:/// -f cosine.ldif 
ldapadd -H ldapi:/// -f inetorgperson.ldif 
ldapadd -H ldapi:/// -f nis.ldif
```

### 2. Inserção de Dados

#### 2.1. Criação de Domínios e Relações

Edite ou crie o arquivo `base.ldif` e insira o conteúdo de [base.ldif](base.ldif):

```bash
vi base.ldif
```

Em seguida, utilize o comando `ldapadd` para adicionar os dados:

```bash
ldapadd -x -W -D "cn=hokage,dc=konoha,dc=jp" -f base.ldif
```

#### 2.2. Remoção de Dados

Se necessário, é possível remover dados usando o comando:

```bash
ldapdelete -x -W -D "cn=hokage,dc=konoha,dc=jp" "centro=ccmn,dc=konoha,dc=jp"
```

Substitua `cn=hokage,dc=konoha,dc=jp` pelo DN do usuário com permissões para operações de exclusão no servidor LDAP.

Este tutorial apresenta os passos iniciais para instalar, configurar e inserir dados no OpenLDAP no CentOS. Certifique-se de ajustar as configurações de acordo com suas necessidades específicas.