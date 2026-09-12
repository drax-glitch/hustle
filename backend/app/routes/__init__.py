from app.routes.auth import auth_bp
from app.routes.quests import quests_bp
from app.routes.character import character_bp
from app.routes.achievements import achievements_bp
from app.routes.shop import shop_bp
from app.routes.progress import progress_bp
from app.routes.settings import settings_bp
from app.routes.dashboard import dashboard_bp
from app.routes.skills import skills_bp
from app.routes.world import world_bp, bosses_bp
from app.routes.game_master import game_master_bp
from app.routes.chronicle import chronicle_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(quests_bp)
    app.register_blueprint(character_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(world_bp)
    app.register_blueprint(bosses_bp)
    app.register_blueprint(game_master_bp)
    app.register_blueprint(chronicle_bp)
