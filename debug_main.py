import app_factory

global child_pid

app = app_factory.create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8989', debug=True)

    del app.interface
