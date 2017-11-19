#!/usr/bin/env python3

from typediff.server import app


if __name__ == "__main__":
    app.run(port=5050, host='0.0.0.0')
