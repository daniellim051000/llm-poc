import os
from datetime import datetime

from auth_utils import login_required_redirect
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from llm_agent import create_agent
from models import User, db
from settings import settings

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = settings.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Initialize the agent
agent = None


def get_agent():
    global agent
    if agent is None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

        if not all([api_key, endpoint, deployment]):
            raise ValueError("Missing required Azure OpenAI configuration")

        agent = create_agent(api_key, endpoint, deployment, api_version)

    return agent


@app.route("/", methods=["GET"])
@login_required_redirect
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember_me = request.form.get("remember_me")

        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template("login.html", username=username)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=bool(remember_me))
            flash("Logged in successfully!", "success")

            # Redirect to next page if available
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    # Get flashed messages for template
    messages = get_flashed_messages(with_categories=True)
    return render_template("login.html", messages=messages)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "message": "LLM Business Data API is running",
            "endpoints": {
                "/query": "POST - Send natural language queries about business data"
            },
        }
    )


@app.route("/query", methods=["POST"])
@login_required
def query_data():
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        question = data["question"]
        agent = get_agent()
        response = agent.query(question)

        return jsonify({"question": question, "answer": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/examples", methods=["GET"])
def get_examples():
    return jsonify(
        {
            "sample_queries": [
                "What is the purchase/invoice history for Company A?",
                "What model did Company A purchase from Ricoh?",
                "What contracts are currently active?",
                "What is the SLA agreement for Company A?",
                "Show me the service history for customer Company B",
                "What machines does Enterprise B have under contract?",
                "Find all items from Ricoh brand",
                "What is the residual value information for our machines?",
            ]
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
