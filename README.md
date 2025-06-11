# DatabaseAssistant
AI Assistant for product managers in order to analyze their company sales.



# 🧠 Northwind SQL Assistant with Gemini & Gradio

This project is an intelligent chatbot interface powered by **Google Gemini 1.5** and **Gradio**, designed to interact with the classic **Northwind database**. It takes user queries in **English or Turkish**, converts them into **SQL queries**, executes them on the database, and provides **natural language explanations** of both the query and its results.

---

## 🚀 Features

- 🌐 **Bilingual Support**: Understands both Turkish and English.
- 🧠 **LLM-Powered**: Uses Google Gemini to generate SQL queries and natural explanations.
- 🗂️ **Northwind Schema Awareness**: Fully understands the structure of the Northwind sample database.
- 🧵 **Conversation Memory**: Keeps recent history in mind to maintain context.
- ⚡ **Caching**: Avoids repeated computation by caching previous results.
- 💬 **Natural Language Output**: Converts raw SQL output into friendly, easy-to-understand text.

---

## 🗃️ Northwind Database Schema

The assistant is trained on the following schema:

Categories: CategoryID, CategoryName, Description

Customers: CustomerID, CustomerName, ContactName, Address, City, PostalCode, Country

Employees: EmployeeID, LastName, FirstName, BirthDate, Photo, Notes

OrderDetails: OrderDetailID, OrderID, ProductID, Quantity

Orders: OrderID, CustomerID, EmployeeID, OrderDate, ShipperID

Products: ProductID, ProductName, SupplierID, CategoryID, Unit, Price

Shippers: ShipperID, ShipperName, Phone

Suppliers: SupplierID, SupplierName, ContactName, Address, City, PostalCode, Country, Phone



---

## 💡 How It Works

1. **User Input**: The user enters a question in natural language.
2. **Language Detection**: The system detects if the message is in English or Turkish.
3. **Gemini LLM**:
    - Generates a SQL query based on conversation context and input.
    - Explains what the query does.
4. **SQLite Execution**: The SQL query runs on the local `Northwind.db` file.
5. **Natural Language Response**: Results are returned with a friendly explanation.

---

## 🧩 Example Questions

You can ask questions like:

- `Show me the top 5 products by units sold`
- `List all customers from Germany`
- `En çok satış yapan 3 çalışanı göster`
- `Hangi ülkelere satış yapıyoruz?`

---

## 📦 Installation

> Make sure you have Python 3.10+ installed and `Northwind.db` placed in the root directory.

### 1. Install dependencies

```bash
pip install gradio google-generativeai
```

### 2. Set your Gemini API Key
You can get your API key from: Google AI Studio

```bash
genai.configure(api_key="YOUR_API_KEY")
```

### 3. Run the app
```bash
python app.py
```




