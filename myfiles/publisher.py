from pymongo import MongoClient

# Credenciais do MongoDB
mongo_port = 27017
mongo_host = 'localhost'
mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/?replicaSet=rs0"
mongo_db = 'engdados'

# Abrir conexão
client = MongoClient(mongo_uri)

# Database engdados
db = client[mongo_db]

# Collection alunos
alunos = db.alunos

# Inserção de registro
alunos.insert_one({
    "nome" : "Raphael Ramos",
    "idade" : 23,
    "date" : '2001-04-25'
})