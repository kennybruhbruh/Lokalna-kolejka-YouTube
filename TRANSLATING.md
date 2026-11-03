# Translating YouTube Local Queue

The tweak's interface is written in English and every other language is a plain text file in
`Localization/`. You do not need to write any code or install anything to add a language.

Currently available: **Polski** (`pl.strings`). Anything that is not translated is shown in English.

## Add a language

1. Open `Localization/en.strings` and copy its content.
2. Create a new file `Localization/<language code>.strings` (GitHub: **Add file → Create new file**)
   and paste the content. Examples of codes: `de`, `fr`, `es`, `it`, `pt-BR`, `ru`, `tr`, `zh-Hans`,
   `ja`, `ko`, `uk`, `cs`, `nl`. Use the code of the language YouTube itself runs in.
3. Translate **only the text on the right side** of each `=`.

   ```
   "Auto advance" = "Auto-Weiterspielen";
   ```

4. Open a pull request. A check runs automatically and tells you about mistakes.

You do not have to translate everything. Missing lines simply stay English, and you can come back
later: `en.strings` always lists all current strings.

## Rules

- Keep the **left side** (the key) exactly as it is.
- Keep the placeholders `%@`, `%ld` and `%d` in the translation. Their order must stay the same
  (`"▶ %@ (%ld more)"` takes a title first and a number second). The check fails if they differ.
- Every line ends with `;`. Quotes inside a text are written `\"`, a line break is `\n`.
- Save the file as UTF-8. Emojis and special characters are fine.
- Keep texts short. The toasts and the settings rows are small.

## One special line: `ytlp.native-queue-action-titles`

This one is **not** shown anywhere. The tweak replaces YouTube's own "Add to queue" menu entry, and
it finds that entry by its label. Write the label YouTube shows in your language (lowercase;
several labels separated by `|`):

```
"ytlp.native-queue-action-titles" = "dodaj do kolejki|do kolejki|w kolejce";
```

To find the label, open the "..." menu of any video in YouTube set to your language. If this line
is missing the tweak still knows the labels of many languages, but yours may not be among them.

## Language selection

The tweak uses the language YouTube runs in (on iOS: **Settings → YouTube → Language**, or the
system language), then the system language list. `pt-BR` falls back to `pt`, `zh-Hans-CN` to
`zh-Hans` and then `zh`. English devices always get English.

To force a language for testing, set the defaults key `ytlp_language` (for example `de`).

## Checking your file

If you have Python 3:

```
python3 tools/translations.py check
```

reports syntax errors, placeholder mistakes and untranslated lines for every language file.

## For developers

- UI text in code is written `YTLPLocalizedString(@"English text")`. The English text is the key.
- After adding or changing such a string, run `python3 tools/translations.py extract` to refresh
  `Localization/en.strings`, then update the language files.
- At build time `tools/translations.py generate` embeds all `Localization/*.strings` into the
  dylib (via the generated `YTLPTranslations.generated.h`). A sideloaded tweak is a single dylib
  without a resource bundle, so the translations have to live inside it.
