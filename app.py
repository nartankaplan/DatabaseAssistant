import gradio as gr
import sqlite3
import google.generativeai as genai
import json
from typing import Dict, Any

# Configure Gemini API
genai.configure(api_key="")

# Using a more advanced model for better context handling
model = genai.GenerativeModel('gemini-1.5-flash')

# Northwind database schema description
database_schema = """
Here is the schema for the Northwind database:
- Categories: CategoryID, CategoryName, Description
- Customers: CustomerID, CustomerName, ContactName, Address, City, PostalCode, Country
- Employees: EmployeeID, LastName, FirstName, BirthDate, Photo, Notes
- OrderDetails: OrderDetailID, OrderID, ProductID, Quantity
- Orders: OrderID, CustomerID, EmployeeID, OrderDate, ShipperID
- Products: ProductID, ProductName, SupplierID, CategoryID, Unit, Price
- Shippers: ShipperID, ShipperName, Phone
- Suppliers: SupplierID, SupplierName, ContactName, Address, City, PostalCode, Country, Phone
"""

# Caching mechanism
query_cache = {}  
gemini_cache = {}  

# Database file path
DB_PATH = r"Northwind.db"

# Function to execute SQL queries
def execute_sql_query(query: str) -> list:
    if query in query_cache:
        return query_cache[query]
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            query_cache[query] = results
            return results
    except Exception as e:
        return [{"error": f"Database error: {str(e)}"}]

# Function to detect user language
def detect_language(text: str) -> str:
    prompt = f"""
    Analyze the following text and determine if it's in Turkish or English.
    Respond with ONLY "tr" for Turkish or "en" for English.
    Text: {text}
    """
    
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            lang = response.text.strip().lower()
            return "tr" if lang == "tr" else "en"
    except:
        pass
    return "en"

# Function to generate SQL query and explanation using LLM
def generate_sql_query_and_response(user_input: str, history) -> Dict[str, Any]:
    lang = detect_language(user_input)

    # Format conversation history for better context
    formatted_history = "\n".join([f"User: {h[0]}\nBot: {h[1]}" for h in history[-5:]])

    # Create cache key based on history and input
    cache_key = f"{formatted_history}\nUser: {user_input}"
    if cache_key in gemini_cache:
        return gemini_cache[cache_key]

    # Prompt with schema and conversation history
    prompt = f"""
    You are a SQL assistant for the Northwind database.
    Here is the schema of the database:
    {database_schema}

    The following is the conversation history between the user and you:
    {formatted_history}

    Now the user asks: {user_input}
    
    Your task:

    - Understand the context of the user's request based on the conversation history.
    - Generate a SQL query to answer the user's question.
    - Provide a natural language explanation of the query, including what it does and why it's relevant to the user's request.
    - Fetch the actual query results and include them in your response.

    The response must be a valid JSON object with this exact structure:
    {{
        "sql_query": "THE SQL QUERY HERE",
        "explanation": "EXPLANATION HERE",
        "results": "ACTUAL DATA RESULTS HERE"
    }}
    """

    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            return {"error": "No response received from Gemini API."}

        text = response.text
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1

        if start_idx >= 0 and end_idx > start_idx:
            json_str = text[start_idx:end_idx]
            result = json.loads(json_str)
        else:
            raise ValueError("No valid JSON found in response")

        if "sql_query" in result:
            query_results = execute_sql_query(result["sql_query"])
            result["results"] = query_results  

        # Cache the result
        gemini_cache[cache_key] = result
        return result
    except Exception as e:
        return {"sql_query": "", "explanation": "", "results": [], "error": str(e)}

# Function to generate natural language explanation for SQL output
def generate_natural_response(response: Dict[str, Any], lang: str) -> str:
    if response.get("error"):
        return f"❌ Error: {response['error']}" if lang == "en" else f"❌ Hata: {response['error']}"

    sql_query = response["sql_query"]
    explanation = response["explanation"]
    results = response["results"]

    if not sql_query:
        return "❌ Error: SQL query could not be generated." if lang == "en" else "❌ Hata: SQL sorgusu oluşturulamadı."

    if not results:
        return (
            f"🔍 {explanation}\n📌 However, no relevant data was found."
            if lang == "en" else
            f"🔍 {explanation}\n📌 Ancak, sorguya uygun bir veri bulunamadı."
        )

    results_text = "\n".join(
        [", ".join(f"{key}: {value}" for key, value in row.items()) for row in results]
    )

    prompt = f"""
    Given the following SQL query, explanation, and results, generate a natural language response in *{lang}*:

    SQL Query: {sql_query}
    Explanation: {explanation}
    Results: {results_text}

    The response should be conversational and easy to understand.
    """

    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            return "❌ Explanation could not be generated." if lang == "en" else "❌ Açıklama üretilemedi."

        return response.text
    except Exception as e:
        return f"❌ Explanation could not be generated: {str(e)}" if lang == "en" else f"❌ Açıklama oluşturulamadı: {str(e)}"

# Main chatbot function
def chatbot(message: str, history):
    sql_response = generate_sql_query_and_response(message, history)
    lang = detect_language(message)
    natural_response = generate_natural_response(sql_response, lang)
    return natural_response

# Gradio UI theme
theme = gr.themes.Soft(primary_hue="blue", secondary_hue="gray")

# Gradio Chat Interface
iface = gr.ChatInterface(
    fn=chatbot,
    title="Northwind Database Assistant 🤖",
    description="Ask questions about the Northwind database in English or Turkish.",
    examples=[
        ["Show me the top 5 products by units sold"],
        ["List all customers from Germany"],
        ["En çok satış yapan 3 çalışanı göster"],
        ["Hangi ülkelere satış yapıyoruz?"],
    ],
    theme=theme,
)

# Launch the application
if __name__ == "__main__":
    iface.launch()
