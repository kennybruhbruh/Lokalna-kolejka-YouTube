# Lokalna kolejka YouTube

Tweak do YouTube, który tworzy lokalną kolejkę filmów i działa także w LiveContainer oraz w IPA z wstrzykniętym dylibem.

## Funkcje

- Dodawanie filmów do lokalnej kolejki z menu kontekstowego (akcja „Dodaj do kolejki”)
- Automatyczne przechodzenie do następnego filmu po zakończeniu bieżącego
- Odtwarzanie w tle bez wybudzania ekranu
- Obsługa przycisku „następny” na ekranie blokady i w Centrum Sterowania
- Zarządzanie kolejką: podgląd, zmiana kolejności, usuwanie
- Ustawienia w ustawieniach YouTube (sekcja „Lokalna kolejka”)

## Jak to działa

Tweak nie używa Cydia Substrate. Opiera się wyłącznie na swizzlingu metod w runtime Objective-C, dzięki czemu można go ładować w środowiskach bez jailbreaka.

### Dodawanie do kolejki

Tweak podmienia handler natywnej akcji „Dodaj do kolejki” (dawniej „Odtwórz jako następny w kolejce”), wyciąga identyfikator filmu z klikniętego elementu i zapisuje go w lokalnej kolejce. Nazwy akcji są dopasowywane do listy tytułów w wielu językach.

### Automatyczne przechodzenie

Tweak przechwytuje natywny mechanizm autonav/autoplay YouTube:

1. Hooki na `nextEndpointForAutonav`, `nextEndpointForAutoplay`, `autonavEndpoint` i `autoplayEndpoint` zwracają następny film z kolejki zamiast rekomendacji.
2. Hooki na `playNext`, `playAutonav` i `playAutoplay` zdejmują element z kolejki przy przejściu.
3. Natywne przejście działa także w tle, bez wybudzania ekranu.
4. Przewinięcie na koniec filmu również przesuwa kolejkę.

## Budowanie

Wymagane są nagłówki YouTube w katalogu `Headers/YouTubeHeader` (repozytorium PoomSmart/YouTubeHeader). Workflow w `.github/workflows` pobiera je automatycznie.

```bash
make package THEOS_PACKAGE_SCHEME=rootless
```

## Użycie

1. Zbuduj dylib albo pobierz go z artefaktów GitHub Actions.
2. Wczytaj go w LiveContainer (folder Tweaks) lub wstrzyknij do IPA.
3. Ustawienia znajdziesz w Ustawienia YouTube → Lokalna kolejka.

## Ustawienia

- **Automatyczne przechodzenie dalej**: po zakończeniu filmu odtwarza następny z kolejki
- **Pokaż przycisk następnego filmu** / **Pokaż przycisk kolejki**: przyciski w nakładce odtwarzacza
- **Otwórz lokalną kolejkę**: podgląd i zarządzanie kolejką
- **Wyczyść lokalną kolejkę**: usuwa wszystkie elementy

## Historia zmian

### 0.0.2
- Naprawa: „Dodaj do kolejki” otwierało reklamę YouTube Premium, bo nowy YouTube zmienił nazwę natywnej akcji.
- Naprawa: crash przy zmianie ustawień, spowodowany błędną sygnaturą hooka `sendActionsForControlEvents:`.
- Hooki `setHidden:` i `setRelatedVideosVisible:` instalują się tylko raz i tylko wtedy, gdy klasa sama implementuje metodę.
- Interfejs przetłumaczony na polski.

## Znane problemy

- Przejście do następnego filmu może nie działać we wszystkich scenariuszach.
- Wykrywanie końca filmu bywa zawodne w niektórych przypadkach brzegowych.

## Licencja

MIT
