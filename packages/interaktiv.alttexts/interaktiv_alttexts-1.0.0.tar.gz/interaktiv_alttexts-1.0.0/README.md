# interaktiv.alttexts

[![Code checks](https://github.com/interaktivgmbh/interaktiv.alttexts/actions/workflows/ci.yml/badge.svg)](https://github.com/interaktivgmbh/interaktiv.alttexts/actions/workflows/ci.yml)

Add alternative texts for images.

This add-on enables editors to provide meaningful alt texts for images,
improving both accessibility and SEO.

Tested for Plone `6.0.15`.

## Features

This add-on extends the Image content type with the alt_text field and renders
it in the Image view and fullscreen view.

There is also the [volto-interaktiv-alttexts](https://github.com/interaktivgmbh/volto-interaktiv-alttexts)
Volto add-on, that adds this feature to your Volto frontend.

## Adding this add-on to your project

Install the add-on using `pip`:

```shell
pip install interaktiv.alttexts
```

or if you're using uv:

```shell
uv pip install interaktiv.alttexts
```

### Install from source

In your `mx.ini` file, add:

```ini
[interaktiv.alttexts]
url = git@github.com:interaktivgmbh/interaktiv.alttexts.git
branch = v1.0.0
extras = test
```

Or using https:

```ini
[interaktiv.alttexts]
url = https://github.com/interaktivgmbh/interaktiv.alttexts.git
branch = v1.0.0
extras = test
```

## Contribute

- [Issue tracker](https://github.com/interaktivgmbh/interaktiv.alttexts/issues)
- [Source code](https://github.com/interaktivgmbh/interaktiv.alttexts/)

## License

The project is licensed under GPLv2.

## Credits and acknowledgements

Generated using [Cookieplone (0.9.10)](https://github.com/plone/cookieplone) and [cookieplone-templates (c0b5a93)](https://github.com/plone/cookieplone-templates/commit/c0b5a93e16bc7da0fb36f37242a5dcf7f792323f) on 2025-11-14 08:18:01.173490. A special thanks to all contributors and supporters!
