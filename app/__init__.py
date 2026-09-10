from flask import Flask, render_template
from config import Config


def create_app():
    Config.init_dirs()

    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_SIZE

    from app.db import init_app as init_db
    init_db(app)

    from app.routes.main import bp as main_bp
    from app.routes.places import bp as places_bp
    from app.routes.items import bp as items_bp
    from app.routes.labels import bp as labels_bp
    from app.routes.scan import bp as scan_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(places_bp, url_prefix="/places")
    app.register_blueprint(items_bp, url_prefix="/items")
    app.register_blueprint(labels_bp, url_prefix="/labels")
    app.register_blueprint(scan_bp, url_prefix="/scan")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404,
                               message="Page not found."), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413,
                               message="File too large (10 MB max)."), 413

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500,
                               message="Something went wrong."), 500

    return app