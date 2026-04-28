from backend.langchain_pipeline import run_pipeline

if __name__ == "__main__":
    print("AI Gift Finder")
    
    while True:
        query = input("\nEnter your query (or 'exit'): ")
        
        if query.lower() == "exit":
            break
        
        result = run_pipeline(query)
        print("\nResult:\n", result)