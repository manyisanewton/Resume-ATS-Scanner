from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger


db = SQLAlchemy()
migrate = Migrate()
swagger = Swagger(template={
    "info": {
        "title": "Resume ATS Scanner API",
        "description": "Internal API for JD and resume matching workflow.",
        "version": "0.1.0",
    },
    "components": {
        "schemas": {
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"}
                }
            }
        }
    }
})
