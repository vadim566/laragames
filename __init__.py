from lara_games_app import init_app
import lara_games_routes.lara_games_routes as routes

def create_app():
    app =init_app()
    app.register_blueprint(routes.app)

    app.run(threaded=True)


if __name__=='__main__':
    create_app()

