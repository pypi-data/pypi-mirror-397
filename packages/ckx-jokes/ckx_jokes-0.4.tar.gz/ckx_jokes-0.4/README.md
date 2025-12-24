# CKX-Jokes API

A Flask-based REST API for retrieving jokes with support for multiple categories and languages.

## Features

- **Multiple Categories**: Support for various joke categories
- **Multi-language Support**: Retrieve jokes in different languages
- **Configurable Defaults**: Set default category and language preferences
- **Single & Multiple Jokes**: Get one joke or a collection of jokes
- **Infinite Joke Generator**: Stream jokes indefinitely with the "forever" endpoints
- **Flexible Filtering**: Combine category and language parameters for targeted results

## API Endpoints

### Home & Configuration

- `GET /` - Homepage with available categories and languages
- `GET /defaults` - Get current default category and language
- `GET /categories` - List all available categories
- `GET /languages` - List all available languages

### Default Settings

- `GET /get-default/category` - Get default category
- `GET /get-default/language` - Get default language
- `GET /set-default/category/<category>` - Set default category
- `GET /set-default/language/<language>` - Set default language

### Single Joke Endpoints

- `GET /joke` - Get a random joke using defaults
- `GET /joke/<category>` - Get joke by category
- `GET /joke/<language>` - Get joke by language
- `GET /joke/<category>/<language>` - Get joke by category and language

### Multiple Jokes Endpoints

- `GET /jokes` - Get all jokes using defaults
- `GET /jokes/<category>` - Get jokes by category
- `GET /jokes/<language>` - Get jokes by language
- `GET /jokes/<category>/<language>` - Get jokes by category and language

### Infinite Joke Stream Endpoints

- `GET /jokes/forever` - Stream jokes indefinitely
- `GET /jokes/forever/<category>` - Stream jokes by category
- `GET /jokes/forever/<language>` - Stream jokes by language
- `GET /jokes/forever/<category>/<language>` - Stream jokes by category and language

## Installation

1. Install package from `pypi.org`:

    ```bash
    pip install ckx-jokes
    ```

2. Once installed, anyone can interact with the package using:

    ```python
    # save the file as "main.py"
    from ckx-jokes install jokes_server

    # Configure HOST, PORT & DEBUG modes
    HOST, PORT, DEBUG = (
      "127.0.0.1", 8080, True
    )

    # Initialize server object
    server = jokes_server()

    if __name__ == "__main__":
      server.run(
        host=HOST, port=PORT, debug=DEBUG
      )
    ```

3. Start the application service in the terminal:

    ```bash
    python main.py
    ```

## License

See [LICENSE](LICENSE) for license information.

## Useful Links

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools documentation](https://setuptools.readthedocs.io/)
- [wheel documentation](https://wheel.readthedocs.io/)
- [twine documentation](https://twine.readthedocs.io/)
- [PyPI](https://pypi.org/)
