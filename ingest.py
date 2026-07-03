import os
from database.vector_memory import vectorMemory  # Ensure matches your class name exactly

def run_ingestion_pipeline():
    print("Initializing Document Ingestion Pipeline...")
    
    # Define our folders
    source_folder = "./knowledge_base"
    
    # Auto-create the folder if it doesn't exist yet
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
        print(f"✨ Created empty folder: '{source_folder}'. Drop your raw text threat intelligence files here!")
        return
    '''
    files = []
    for f in os.listdir(source_folder):
        if f.endswith('.txt'):
            files.append(f)
    '''
    # Look for files to read
    files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]
    
    if not files:
        print("⚠️ No new .txt files found in './knowledge_base/'. Place reports there to train the AI.")
        return

    # Initialize your existing ChromaDB module
    vector_store = vectorMemory()
    
    print(f" Found {len(files)} document(s) to ingest. Commencing processing...")
    
    for file_name in files:
        file_path = os.path.join(source_folder, file_name)
        print(f" Processing: {file_name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        #  Simple Paragraph Chunking
        # We split by double newlines so the AI gets full context paragraphs instead of broken individual words
        chunks = [chunk.strip() for chunk in raw_text.split("\n\n") if chunk.strip()]
        
        print(f" Split document into {len(chunks)} structural context chunks.")
        
        # Feed each chunk directly into your ChromaDB collection
        for index, chunk in enumerate(chunks):
            # Using your existing vector store logic to add data
            # If your analyze_similarity setup needs an 'add' method, we make sure it works here:
            unique_id = f"{file_name}_chunk_{index}"
            
            # Direct insertion using ChromaDB collection under the hood
            vector_store.collection.add(
                documents=[chunk],
                metadatas=[{"source": file_name}],
                ids=[unique_id]
            )
            
        print(f"Successfully ingested and memorized: {file_name}")
        
        # Clean up or archive the file so we don't double-ingest it next time
        os.rename(file_path, os.path.join(source_folder, f"processed_{file_name}"))
        print(f" Moved {file_name} to processed state.")

if __name__ == "__main__":
    run_ingestion_pipeline()