# Desafio

Existem tres formas de rodar uma extração com meltano nesse projeto. A primeira refere se ao projeto meltano que esta dentro da pasta northwinf_meltano.
A segunda roda uma extração usando um meltano dentro do container e a terceira roda o meltano dentro do conteiner usando airflow. 
Se vc pretende rodar o airflow vá direto para o topico 3

# Meltano

## 1 - Rodando projeto meltano

01 - pegar os arquivos docker-compose e data do nothwind

02 - criar a venv
    ```
    python3 -m venv venv
    ```

03 - ativar a venv
    ```
    source venv/bin/activate
    ```

03.1 - Instalar pacotes
 
    ```
    pip install -r requirements.txt

    ```

04 - instalar meltano:
    ```
    pip install meltano
    meltano init 
    ```

        e adicionar o nome do projeto (northwind_meltano)

05 - apagar as pastas dentro do projeto e deixar apenas .meltano e output

06 - entrar dentro do projeto meltano e roda
    ```
    cd northwind_meltano
    ```

    ```
    meltano install
    ```

## Configurando Extract, Load e String connection no meltano

08 - volta para pasta pokedesk_meltano
    ```    
    meltano add extractor tap-postgres
    ```

09 - instalar o plugin criado
    ```
    meltano install
    ```

obs: sempre rodar o load com extractor

10 - adicionar plugin de load e instalar 
    ```
    meltano add loader target-jsonl
    meltano install
    ```

11 - rodar o projeto
    ```
    meltano run tap-postgres target-jsonl
    ```

    11.1 - vai rodar um erro pq nao configurou a string conexao

    ```
    postgresql://[username]:[password]@localhost:5432/[db_name]
    ```

12 - pode apagar a pasta .meltano pra deletar as coisas q vc ja instalou
    e pode rodar o comando meltano install para criar novamente

13 - comando para listar arquivos do postgres

    ```
    meltano select tap-postgres --list
    ```

14 - pode se selecionar apenas uma tabela no banco
    adicione o comando dentro do arquivo meltano.yml
    ```    
    config: 
      sqlalchemy_url: postgresql://northwind_user:thewindisblowing@localhost:5432/northwind
    select: 
      - public-products.*
    ```

## Rodando primeira extração

15 - rode novamente o projeto:
    
    ```
    meltano install
    meltano run tap-postgres target-jsonl
    ```

16 - observe o erro pois essa tabela tem dados diferentes ou faltando
    ```
    Failed validating 'type' in schema ['properties']
    ```

        16.1 - vc pode selecionar outra tabela

        ```    
        config: 
        sqlalchemy_url: postgresql://northwind_user:thewindisblowing@localhost:5432/northwind
        select: 
        - public-suppliers.*
        ```
17 - Criação de um dockerfile.meltano para copiar o projeto meltano para um container docker

## Comando para carregar do data lake -> arquivo json
```
meltano run tap-postgres target-jsonl
```

## Comando para carregar os arquivo json -> data warehouse
```
meltano run tap-singer-jsonl target-postgres
```

# 2 - Rodando meltano no docker

## Levantar os Containers  

07 - abrir terminal e levantar o container dos bancos postegres

    ```
    docker compose up -d
    ```


## Comando para rodar o container meltano (data lake -> arquivo json)
```
docker build -f Dockerfile.meltano -t meltano .
```
```
docker run -v $(pwd)/northwind_meltano/output:/meltano/northwind_meltano/output --network=host meltano
```

# 3 - airflow 

## Rodar o airflow database:
```docker compose up airflow-init``` 

### Build a imagem do meltano
``` docker build -f Dockerfile.meltano -t meltano . ```

### dentro da dag tutorial verifique o caminho do seu projeto e coloque na source da dag meltano_extraction_task, meltano_ingestion_task

### Rodar o projeto
```docker compose up```

### Rode o docker ps para verificar se ta health

### Acessar o localhost://8080

### trigger na dag e observe os logs



## bugs no airflow

### Lembrar de subir a imagem do meltano. Rode na pasta do projeto
```docker build -f Dockerfile.meltano -t meltano .```

### problema de permissao do docker sock. Rodar no terminal da sua maquina: 
```sudo chmod 666 /var/run/docker.sock```

### Evite usar caminhos com espaços no volume do docker

### Liberar permissao para a pasta output. Rodar na pasta do projeto: 

```chmod -R 777 northwind_meltano```
```ls -lah northwind_meltano```
