from utils import LLMClient, SimpleRAGSystem, get_available_models, load_sample_documents, load_sample_documents_for_demo

def user_prompt_input(prompt: str):
    available_models = get_available_models()
    llm_client = LLMClient(model=available_models[2], temperature=0.2,max_tokens=2000)
    rag = SimpleRAGSystem()
    rag.load_data()
    context = rag.get_context_for_query(prompt, max_context_length=2000)
    #print(context)
    enhanced_prompt = f"""

    {context}

    User Question: {prompt}

    Based on the following information from the knowledge base, please answer the user's question:
    Your job is to give a review or introducing a new book to user with given exist data

    Sort it out by rating (max is 5)
    3 to 10 books Recommendation 
    if the book doesn't have a rating just said it doesn't have a rating
    (if i didn't said any before)

    Please provide a comprehensive answer based on the information provided above. If the information is not sufficient or not found in the knowledge base, please mention that clearly.
    """
    msg = [{"role": "user", "content": enhanced_prompt}]
    response = llm_client.chat(msg)
    return response
   #return
   #for q in ans:
   #    print("Q:", q)
   #    print("A:", result["answer"], "\n")
