🚀 SpendlyAI

AI-Powered Voice & Receipt Based Expense Tracker
SpendlyAI is a smart expense tracking application that allows users to record expenses using voice input and receipt uploads. It leverages AI (Gemini API) to automatically understand, extract, and categorize expenses, making expense management effortless and fast.
🧠 Key Features
🎙 Voice-Based Expense Tracking
Add expenses by simply speaking in any language
AI converts speech → text → structured expense data
Supports current and past expenses

🧾 Receipt Recognition (AI-Powered)
Upload receipt images (JPG/PNG)
AI extracts:
Final amount
Vendor name
Date
Category

No manual entry required
📊 Smart Dashboard

Total expenses

Monthly expense summary

Category-wise breakdown

Expense history

🔐 Secure Authentication

User signup & login

JWT-based authentication

Each user has isolated expense data
<img width="1919" height="926" alt="Screenshot 2026-01-06 104704" src="https://github.com/user-attachments/assets/4ff9e72f-276f-42d3-833c-2f7e1e6cac6e" />

<img width="1904" height="976" alt="Screenshot 2026-01-06 111254" src="https://github.com/user-attachments/assets/baabc2c9-399c-40ac-9990-8d509524feca" />

<img width="400" height="864" alt="Screenshot 2026-01-06 111305" src="https://github.com/user-attachments/assets/be0bb2a7-0e22-470f-8006-29ef0ef51b05" />     <img width="390" height="870" alt="Screenshot 2026-01-06 111842" src="https://github.com/user-attachments/assets/9ed27aad-f493-418b-9059-e4bc5ee75750" />



🏗 System Architecture
Web App (HTML,CSS,JS)
        |
        | REST API
        v
Backend (Python - Flask)
        |
        ├── Auth Service
        ├── Expense Service
        ├── AI Service (Gemini)
        └── Receipt Service
        |
Cloud Database

🛠 Tech Stack
Backend
Python
Flask
AI / LLM
Google Gemini API 
Speech-to-Text
Text Understanding
Vision (Receipt Recognition)
Database
Cloud Database (MongoDB)
Frontend (Web App)
Html,Css,Js

📂 Project Structure
SPENDLYAI/

<img width="735" height="759" alt="Screenshot 2026-01-06 112055" src="https://github.com/user-attachments/assets/b467857a-c5d0-496d-84c3-2adb69636a8e" />


🧠 AI Intelligence Flow
🎤 Voice Expense Flow
User records voice
Backend sends audio to Gemini (Speech-to-Text)
Gemini extracts:
Amount
Category
Vendor
Date
Backend validates & stores expense

🧾 Receipt Upload Flow
User uploads receipt image
Gemini Vision reads receipt
Extracts final bill details
Backend stores expense

🗂 Supported Expense Categories
Food
Travel
Shopping
Bills
Medical
Other

(Categories can be expanded later)

🔒 Security & Validation Rules
Only completed expenses are stored
Future expenses are ignored
Amount must be > 0
Invalid or unclear AI output is safely rejected
Passwords are securely hashed

🎯 Project Scope (Current Phase)
✔ Expense tracking only
✔ Voice input
✔ Receipt recognition
✔ No income tracking (yet)
✔ No future expenses

🚧 Future Enhancements
Income tracking
Budget limits
AI spending insights
Voice-based queries (“How much did I spend this month?”)
Charts & graphs
Multi-language UI
Export to CSV/PDF

👨‍💻 Developer Note
SpendlyAI is built with clean architecture, keeping:
API routes
Business logic
Database access
completely separated for scalability and maintainability.

📄 License
This project is currently for educational and portfolio purposes.
License can be added later.

⭐ Final Words

SpendlyAI is not just an expense tracker —
it’s a smart AI agent that listens, understands, and manages your expenses automatically.
