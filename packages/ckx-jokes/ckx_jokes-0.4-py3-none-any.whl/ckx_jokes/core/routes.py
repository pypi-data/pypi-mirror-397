from .jokes import PyJokes
from http import HTTPStatus
from ascii_magic import AsciiArt
from typing import Union, Literal
from flask import Blueprint, redirect, url_for

pjk = PyJokes()
# favicon = AsciiArt.from_image("./images/pyjokes.png")
# favicon.to_terminal()

core: Blueprint = Blueprint("core", __name__)

def useResponse(state, status_code: int = HTTPStatus.OK.value):
  return state, status_code

def setDefault(
  state: Union[Literal["category"], Literal["language"]],
  default: str
):
  match state:
    case "category":
      pjk.DEFAULT_CATEGORY = default.casefold() if default.casefold() in pjk.CATEGORIES \
        else pjk.DEFAULT_CATEGORY
    case "language":
      pjk.DEFAULT_LANGUAGE = default.casefold() if default.casefold() in pjk.LANGUAGES \
        else pjk.DEFAULT_LANGUAGE

  return redirect(url_for(
    f"core.get_default_{state}", code=HTTPStatus.TEMPORARY_REDIRECT.value
  ))

def jokeResponse(keys, values): useResponse(dict(zip(keys, values)))

# Homepage
@core.get("/")
def index():
  return useResponse({"categories": pjk.CATEGORIES, "language": pjk.LANGUAGES})

# Default Category & Language
@core.get("/defaults")
def defaults():
  return useResponse({"category": pjk.DEFAULT_CATEGORY, "language": pjk.DEFAULT_LANGUAGE})

# Get Default Category
@core.get("/get-default/category")
def get_default_category(): return useResponse({"default-category": pjk.DEFAULT_CATEGORY})

# Get Default Language
@core.get("/get-default/language")
def get_default_language(): return useResponse({"default-language": pjk.DEFAULT_LANGUAGE})

# Set Default Category
@core.get("/set-default/category/<category>")
def set_default_category(category: str): return setDefault("category", category)

# Set Default Language
@core.get("/set-default/language/<language>")
def set_default_language(language: str): return setDefault("language", language)

# All Categories
@core.get("/categories")
def categories(): return useResponse({"categories": pjk.CATEGORIES})

# All Languages
@core.get("/languages")
def languages(): return useResponse({"languages": pjk.LANGUAGES})

# Get Joke
@core.get("/joke")
def get_joke(): return useResponse(pjk.getJoke())

# Get Joke By Category
@core.get("/joke/<category>")
def get_joke_by_category(category: str = pjk.DEFAULT_CATEGORY):
  return jokeResponse(["category", "joke"], [category, pjk.getJokeByCategory(category)])

# Get Joke By Language
@core.get("/joke/<language>")
def get_joke_by_language(language: str = pjk.DEFAULT_LANGUAGE):
  return jokeResponse(["language", "joke"], [language, pjk.getJokeByLanguage(language)])

# Get Joke By Category & Language
@core.get("/joke/<category>/<language>")
def get_joke_by_category_and_language(
  category: str = pjk.DEFAULT_CATEGORY,
  language: str = pjk.DEFAULT_LANGUAGE
):
  return jokeResponse(
    ["category", "language", "joke"],
    [category, language, pjk.getJokeByCategoryAndLanguage(language, category)]
  )

# Get Jokes
@core.get("/jokes")
def get_jokes(): return useResponse(pjk.getJokes())

# Get Jokes By Category
@core.get("/jokes/<category>")
def get_jokes_by_category(category: str = pjk.DEFAULT_CATEGORY):
  return jokeResponse(["category", "jokes"], [category, pjk.getJokesByCategory(category)])

# Get Jokes By Language
@core.get("/jokes/<language>")
def get_jokes_by_language(language: str = pjk.DEFAULT_LANGUAGE):
  return jokeResponse(["language", "jokes"], [language, pjk.getJokesByLanguage(language)])

# Get Jokes By Category & Language
@core.get("/jokes/<category>/<language>")
def get_jokes_by_category_and_language(
  category: str = pjk.DEFAULT_CATEGORY,
  language: str = pjk.DEFAULT_LANGUAGE
):
  return jokeResponse(
    ["category", "language", "jokes"],
    [category, language, pjk.getJokesByCategoryAndLanguage(language, category)]
  )

# Get Jokes Forever
@core.get("/jokes/forever")
def get_jokes_forever(): return next(pjk.getJokesForever())

# Get Jokes Forever By Category
@core.get("/jokes/forever/<category>")
def get_jokes_forever_by_category(category: str = pjk.DEFAULT_CATEGORY):
  return jokeResponse(["category", "joke"], [category, next(pjk.getJokesForeverByCategory(category))])

# Get Jokes Forever By Language
@core.get("/jokes/forever/<language>")
def get_jokes_forever_by_language(language: str = pjk.DEFAULT_LANGUAGE):
  return jokeResponse(["language", "joke"], [language, next(pjk.getJokesForeverByLanguage(language))])

# Get Jokes Forever By Category & Language
@core.get("/jokes/forever/<category>/<language>")
def get_jokes_forever_by_category_and_language(
  category: str = pjk.DEFAULT_CATEGORY,
  language: str = pjk.DEFAULT_LANGUAGE
):
  return jokeResponse(
    ["category", "language", "joke"],
    [category, language, next(pjk.getJokesForeverByCategoryAndLanguage(language, category))]
  )
