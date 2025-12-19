"""Flask blueprint for PraisonAI."""

from flask import Blueprint, request, jsonify

from flask_praisonai.client import PraisonAIClient


def create_blueprint(
    api_url: str = "http://localhost:8080",
    url_prefix: str = "/praisonai",
) -> Blueprint:
    """Create a Flask blueprint for PraisonAI.

    Args:
        api_url: PraisonAI API server URL.
        url_prefix: URL prefix for the blueprint.

    Returns:
        A configured Flask blueprint.
    """
    bp = Blueprint("praisonai", __name__, url_prefix=url_prefix)
    client = PraisonAIClient(api_url=api_url)

    @bp.route("/query", methods=["POST"])
    def query_praisonai():
        """Send a query to PraisonAI agents."""
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field"}), 400

        query = data["query"]
        agent = data.get("agent")

        try:
            if agent:
                response = client.run_agent(query, agent)
            else:
                response = client.run_workflow(query)
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @bp.route("/agents", methods=["GET"])
    def list_agents():
        """List available PraisonAI agents."""
        try:
            agents = client.list_agents()
            return jsonify({"agents": agents})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return bp
