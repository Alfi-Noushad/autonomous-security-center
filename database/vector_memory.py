import chromadb
from chromadb.utils import embedding_functions 

class vectorMemory():
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_storage")

        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        #Create or get our security exploit data log collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="security_exploits",
            embedding_function=self.sentence_transformer_ef
        )
        
        #automatically execute the seeding sequence on startup
        self._seed_attack_database()

    def _seed_attack_database(self):
        #Only add the signature profiles if the database storage is empty
        if self.collection.count() == 0:
            self.collection.add(
                documents = [
                    "Brute force password cracking attempt on server administration root control panel", 
                "Volumetric Distributed Denial of Service DDoS overflow saturation attack flooding network ports"
                ],
                ids = ["exploit_brute", "exploit_ddos"]
            )

        print("Vector Database initialized and seeded with exploit files!")

    def analyze_similarity(self,log_message: str):
        query_results = self.collection.query(
            query_texts = [log_message],
            n_results=1
        )
        return query_results
        





