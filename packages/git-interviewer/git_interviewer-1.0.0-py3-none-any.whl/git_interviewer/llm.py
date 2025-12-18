# gemini or openrouter api llm wrapper
from google import genai
from .config import get_api_key, GIT_INTERVIEWER_MODE
from .personas import PERSONAS

def generate_question(diff_content):
    """ generate an interview question based on diff content"""
    api_key = get_api_key()
    if not api_key: 
        raise ValueError("API key is missing.")
    
    client = genai.Client(api_key=api_key)
    
    
   
    system_prompt = PERSONAS.get(GIT_INTERVIEWER_MODE, PERSONAS["nice"])
    
    prompt = f"""
    {system_prompt}
    
    Here is the git diff of the changes about to be committed:
    
    {diff_content}
    
    Review this code and ask ONE thoughtful, specific question about the implementation, design or intent. 
    Do not ask for a summary, Ask a question that requires the developer to think. 
    """
    try: 
        # new SDK update
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt)
        return response.text.strip()
    except Exception as e: 
        print(f"Error generating question: {e}")
        return None