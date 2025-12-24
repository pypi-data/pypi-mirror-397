from pyjokes import get_joke, get_jokes, forever

class PyJokes:
  def __init__(self) -> None:
    self.CATEGORIES: list[str] = ['all', 'chuck', 'neutral']
    self.LANGUAGES: list[str] = [
      'cs', 'de', 'en', 'es', 'eu', 'fr', 'gl', 'hu', 'it', 'lt', 'pl', 'ru', 'sv'
    ]
    self.__DEFAULT_LANGUAGE: str = self.LANGUAGES[2]
    self.__DEFAULT_CATEGORY: str = self.CATEGORIES[-1]

  @property
  def DEFAULT_CATEGORY(self) -> str:
    return self.__DEFAULT_CATEGORY

  @DEFAULT_CATEGORY.setter
  def DEFAULT_CATEGORY(self, category: str) -> None:
    self.__DEFAULT_CATEGORY = category

  @property
  def DEFAULT_LANGUAGE(self) -> str:
    return self.__DEFAULT_LANGUAGE

  @DEFAULT_LANGUAGE.setter
  def DEFAULT_LANGUAGE(self, language: str) -> None:
    self.__DEFAULT_LANGUAGE = language

  def menu(self) -> None:
    # Displaying supported categories
    print("\nSupported Categories!")
    for (idx, category) in enumerate(self.CATEGORIES, start=1):
      print(f"\t{idx}. {category} {'(Default!)' if category == 'neutral' else ''}")

    # Displaying supported languages
    print("\nSupported Languages!")
    for (idx, language) in enumerate(self.LANGUAGES, start=1):
      print(f"\t{idx}. {language} {'(Default!)' if language == 'en' else ''}")

    print("\n", end="")

  def getJoke(self) -> str: return get_joke()
  def getJokeByCategory(self, category: str) -> str: return get_joke(category=category)
  def getJokeByLanguage(self, language: str) -> str: return get_joke(language=language)
  def getJokeByCategoryAndLanguage(language: str, category: str) -> str:
    return get_joke(language=language, category=category)

  def getJokes(self) -> list[str]: return get_jokes()
  def getJokesByCategory(self, category: str) -> list[str]: return get_jokes(category=category)
  def getJokesByLanguage(self, language: str) -> list[str]: return get_jokes(language=language)
  def getJokesByCategoryAndLanguage(language: str, category: str) -> list[str]:
    return get_jokes(language=language, category=category)

  def getJokesForever(self): return forever()
  def getJokesForeverByCategory(self, category: str): return forever(category=category)
  def getJokesForeverByLanguage(self, language: str): return forever(language=language)
  def getJokesForeverByCategoryAndLanguage(language: str, category: str):
    return forever(language=language, category=category)
