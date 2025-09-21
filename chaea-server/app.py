from flask import Flask
from flask_cors import CORS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Importar blueprints
from routes.chaea_profile import chaea_bp
from routes.consent import consent_bp
from routes.adaptive_eval import adaptive_bp

# Registrar blueprints
app.register_blueprint(chaea_bp, url_prefix='/chaea')
app.register_blueprint(consent_bp, url_prefix='/consent')
app.register_blueprint(adaptive_bp, url_prefix='/adaptive')

@app.route('/health')
def health_check():
    return {
        "status": "CHAEA Server Running", 
        "version": "1.0.0",
        "endpoints": {
            "consent": "/consent/grant, /consent/check/<user_id>/<course_id>",
            "chaea": "/chaea/submit-responses, /chaea/profile/<user_id>/<course_id>",
            "adaptive": "/adaptive/generate-evaluation, /adaptive/get-user-variant/<user_id>/<evaluation_id>"
        }
    }

if __name__ == '__main__':
    app.run(debug=True, port=5010)