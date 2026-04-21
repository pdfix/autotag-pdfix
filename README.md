# Autotag PDFix

A Docker image that automatically tags a PDF file using layout template PDFix JSON using correct PDFix SDK version.

## Table of Contents

- [Autotag PDFix](#autotag-pdfix)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
  - [Run a Docker Container ](#run-docker-container)
  - [Export Configuration for Integration](#export-configuration-for-integration)
  - [License](#license)
  - [Help \& Support](#help--support)

## Getting Started

To use this Docker application, you'll need to have Docker installed on your system. If Docker is not installed, please follow the instructions on the [official Docker website](https://docs.docker.com/get-docker/) to install it.

## Run a Docker Container

The first run will pull the docker image, which may take some time. Make your own image for more advanced use.  
To run docker container as CLI you should share the folder with PDF to process using `-v` parameter. In this example it's current folder.

```bash
docker run -v $(pwd):/data -w /data --rm pdfix/autotag-pdfix:latest tag --name ${LICENSE_NAME} --key ${LICENSE_KEY} -i /data/input.pdf -t /data/template.json -o /data/output.pdf
```

This action assumes user have `template.json` with older SDK version and needs PDFix SDK of that version to autotag PDF. For this provide `template.json` with input document to action.

These arguments are for an account-based PDFix license.

```bash
--name ${LICENSE_NAME} --key ${LICENSE_KEY}
```

Contact support for more information.

For more detailed information about the available command-line arguments, you can run the following command:

```bash
docker run --rm pdfix/autotag-pdfix:latest --help
```

## Export Configuration for Integration

To export the configuration JSON file, use the following command:

```bash
docker run -v $(pwd):/data -w /data --rm pdfix/autotag-pdfix:latest config -o config.json
```

## License

- [PDFix license](https://pdfix.net/terms)

The trial version of the PDFix SDK may apply a watermark on the page and redact random parts of the PDF including the scanned image in the background. Contact us to get an evaluation or production license.

## Help & Support

To obtain a PDFix SDK license or report an issue please contact us at support@pdfix.net.
For more information visit https://pdfix.net
