# Compiling Tailwind CSS

## Prerequisites

-   Node.js
-   npm

## Installation

If this is the first time you are using this project, you need to install the dependencies. You can do this by running the following command in the root of the project:

```bash
npm install
```

## Usage

To compile the Tailwind CSS, you can run the following command in the root of the project:

```bash
npx tailwindcss -i ./website/static/css/tailwind_input.css -o ./website/static/css/tailwind.css
```

This will compile the Tailwind CSS and output it to the `tailwind.css` file specified in the `-o` flag, `website/static/css`.

To watch for changes and automatically compile the Tailwind CSS, add the `--watch` flag to the command:

```bash
npx tailwindcss -i ./website/static/css/tailwind_input.css -o ./website/static/css/tailwind.css --watch
```

## Considerations

-   Only `html` documents in the `website` directory are considered for the Tailwind CSS compilation. Modify the `tailwind.config.js` file to change this behavior.
-   The `tailwind.css` file should be minified before being used in production. You can use a tool like django-compressor to minify the CSS file.
-   If you are using a different input file or output directory, modify the `npx tailwindcss` command accordingly.
-   The `tailwind_input.css` file is the input file for the Tailwind CSS. You can modify this file to include the Tailwind CSS classes you want to use, or include global styles that you want to apply.
-   See the [Tailwind CSS documentation](https://tailwindcss.com/docs) for more information on how to use Tailwind CSS.
-   Add extra color classes to the `tailwind.config.js` file to use custom colors in the CSS. Currently supported are: `['primary','primary-light', text','text-light', 'text-dark', 'accent', 'accent-light', 'accent-dark']`
