import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from llm_agent import create_agent

load_dotenv()

app = Flask(__name__)

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
def index():
    return render_template("index.html")


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
