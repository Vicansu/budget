from flask import Flask, request, redirect, url_for, render_template_string
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Required for session handling if used in future

# Gemini model configuration
genai.configure(api_key="AIzaSyAss5oPg-dCYc0UW6Yryk2weH0WQSOiPGg")
model = genai.GenerativeModel("gemini-1.5-flash")

# Store user data
user_data = {
    'income': 0.0,
    'expenses': {},
    'total_expenses': 0.0,
    'savings': 0.0,
    'advice': '',
    'user_response': ''  # ✅ NEW: Store user feedback
}

def get_ai_advice(income, total_expenses, expenses):
    prompt = (
        f"You are a financial advisor. Provide simple and practical advice "
        f"on how to increase savings. Monthly income: ${income:.2f}, "
        f"Total expenses: ${total_expenses:.2f}, My expenses are: {expenses}. "
        f"Present it in a simple and friendly manner."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to get advice: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            income = float(request.form['income'])
        except ValueError:
            return "Invalid income input", 400
        user_data['income'] = income
        return redirect(url_for('expenses'))
    return render_template_string(""" 
    <!-- Income Page -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enter Income</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #f9f9f9; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .container { background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 350px; text-align: center; }
            input, button { padding: 0.6rem; margin-top: 1rem; width: 100%; border-radius: 6px; border: 1px solid #ccc; }
            button { background-color: #4CAF50; color: white; font-weight: bold; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💰 Smart Budget Calculator</h1>
            <form method="POST">
                <label>Enter Monthly Income: $</label><br>
                <input type="number" name="income" step="0.01" required><br>
                <button type="submit">Continue</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        name = request.form['name']
        try:
            amount = float(request.form['amount'])
        except ValueError:
            return "Invalid expense amount", 400
        if name in user_data['expenses']:
            user_data['expenses'][name] += amount
        else:
            user_data['expenses'][name] = amount
        user_data['total_expenses'] += amount
        return redirect(url_for('expenses'))

    return render_template_string("""
    <!-- Expenses Page -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enter Expenses</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #eef2f7; padding: 2rem; }
            .container { max-width: 600px; margin: auto; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            form { display: flex; flex-direction: column; gap: 1rem; }
            input, button { padding: 0.5rem; border-radius: 6px; border: 1px solid #ccc; }
            button { background: #007bff; color: white; border: none; cursor: pointer; }
            ul { padding-left: 1rem; }
            a { margin-right: 1rem; color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧾 Add Your Expenses</h1>
            <form method="POST">
                <label>Expense Name:</label>
                <input type="text" name="name" required>
                <label>Amount ($):</label>
                <input type="number" name="amount" step="0.01" required>
                <button type="submit">Add Expense</button>
            </form>

            <h2>📋 Current Expenses:</h2>
            <ul>
                {% for name, amount in expenses.items() %}
                    <li>{{ name }}: ${{ '%.2f' | format(amount) }}</li>
                {% endfor %}
            </ul>

            <div style="margin-top: 1rem;">
                <a href="{{ url_for('summary') }}">View Summary</a> |
                <a href="{{ url_for('reset') }}">Reset</a>
            </div>
        </div>
    </body>
    </html>
    """, expenses=user_data['expenses'])

@app.route('/summary', methods=['GET', 'POST'])  # ✅ ALLOW POST
def summary():
    income = user_data['income']
    total_expenses = user_data['total_expenses']
    savings = income - total_expenses
    user_data['savings'] = savings

    if savings < 0.046 * income and not user_data['advice']:
        user_data['advice'] = get_ai_advice(income, total_expenses, user_data['expenses'])

    # ✅ NEW: Save user response
    if request.method == 'POST':
        user_data['user_response'] = request.form.get('response', '')

    return render_template_string("""
    <!-- Summary Page -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>Summary</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #f1f4f9; padding: 2rem; }
            .container { max-width: 700px; margin: auto; background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            h1, h2 { color: #333; }
            ul { padding-left: 1.2rem; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .budget-box li { margin-bottom: 0.5rem; }
            .highlight-box {
                background: #fef3c7;
                border-left: 6px solid #f59e0b;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            button {
                margin-top: 1rem;
                padding: 0.7rem 1rem;
                background-color: #ffa500;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Budget Summary</h1>
            <p><strong>Total Income:</strong> ${{ '%.2f' | format(income) }}</p>
            <p><strong>Total Expenses:</strong> ${{ '%.2f' | format(total_expenses) }}</p>
            <p><strong>Savings:</strong> ${{ '%.2f' | format(savings) }}</p>

            {% if advice %}
            <div class="highlight-box">
                <h2>💡 Personalized AI Advice</h2>
                <p style="font-size: 1.1rem; color: #333;">{{ advice }}</p>
                
                {% if not user_response %}
                <form method="POST" style="margin-top: 1rem;">
                    <label for="response" style="font-weight: 600;">Your Response:</label><br>
                    <textarea name="response" rows="3" style="width: 100%; padding: 0.6rem; border-radius: 6px; border: 1px solid #ccc;" placeholder="What do you think about the advice?" required></textarea>
                    <button type="submit">Submit Response</button>
                </form>
                {% else %}
                <div style="margin-top: 1rem; background-color: #e6ffed; padding: 1rem; border-left: 6px solid #10b981; border-radius: 8px;">
                    <strong>🗣️ Your Response:</strong>
                    <p>{{ user_response }}</p>
                </div>
                {% endif %}
            </div>
            {% endif %}

            <a href="{{ url_for('get_advice') }}">
                <button>💬 Get AI Recommendation</button>
            </a>

            <h2>Expense Breakdown:</h2>
            <ul>
                {% for name, amount in expenses.items() %}
                    <li>{{ name }}: ${{ '%.2f' | format(amount) }}</li>
                {% endfor %}
            </ul>

            <h2>Recommended Budget (50/30/20 Rule):</h2>
            <ul class="budget-box">
                <li>Needs (50%): ${{ '%.2f' | format(income * 0.5) }}</li>
                <li>Wants (30%): ${{ '%.2f' | format(income * 0.3) }}</li>
                <li>Savings (20%): ${{ '%.2f' | format(income * 0.2) }}</li>
            </ul>

            <div style="margin-top: 1rem;">
                <a href="{{ url_for('reset') }}">🔄 Start Over</a>
            </div>
        </div>
    </body>
    </html>
    """, income=income, total_expenses=total_expenses,
           savings=savings, advice=user_data['advice'], expenses=user_data['expenses'],
           user_response=user_data['user_response'])

@app.route('/get_advice')
def get_advice():
    income = user_data['income']
    total_expenses = user_data['total_expenses']
    user_data['advice'] = get_ai_advice(income, total_expenses, user_data['expenses'])
    return redirect(url_for('summary'))

@app.route('/reset')
def reset():
    user_data['income'] = 0.0
    user_data['expenses'] = {}
    user_data['total_expenses'] = 0.0
    user_data['savings'] = 0.0
    user_data['advice'] = ''
    user_data['user_response'] = ''  # ✅ Clear response too
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

