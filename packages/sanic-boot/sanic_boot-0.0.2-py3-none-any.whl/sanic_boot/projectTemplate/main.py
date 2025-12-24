from sanic_boot import sanicBoot

app = sanicBoot(__name__, docs=True)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        auto_reload=True
    )
