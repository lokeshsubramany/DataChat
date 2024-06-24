import chromadb

def load_document(file):
    print('\n In chromadb load_document')
    import os
    name, extension = os.path.splitext(file)
    if extension == '.txt':
        with open(file) as temp:
            data = temp.read()
    else:
        print('Document format not supported')
        return None
    
    return data

def split_data(data,splitter='**'):
    print('\n In chromadb split_data')
    return str(data).split(splitter)

def get_db_conn(collection_name='default'):
    print('\n In chromadb get db connection')

    client = chromadb.PersistentClient(path="./chromadb")
    collection = client.get_or_create_collection(name=collection_name)
    return collection

def add_to_collection(collection,docs,ids):
    print('\n In chromadb add to collection')
    collection.upsert(documents = docs,ids=ids)

def chroma_query(query,n_results=2,collection='default'):
    """ Returns string of results"""
    print('\nin chromadb query')
    collection = get_db_conn(collection)
    results = collection.query(query_texts=query,n_results=2)
    
    return '\n'.join(results['documents'][0])