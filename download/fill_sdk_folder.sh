#!/bin/bash

# Default values
ARCHITECTURE=""
FOLDER="sdk"
GITHUB_TOKEN=""
TOKEN_FILE="../data/github_token.txt"

if [ -f "$TOKEN_FILE" ]; then
    GITHUB_TOKEN=`cat $TOKEN_FILE`
fi

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -a|--architecture)
            shift
            ARCHITECTURE="$1"
            shift
            ;;
        -f|--folder)
            shift
            FOLDER="$1"
            shift
            ;;
        -g|--github-token)
            shift
            GITHUB_TOKEN="$1"
            shift
            ;;
        *)
            echo "❌ Unexpected argument: $1" >&2
            exit 1
            ;;
    esac
done

if [ -z "$FOLDER" ]; then
    echo "❌ Folder is required" >&2
    exit 2
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GitHub token is required" >&2
    exit 2
fi

if [ "$ARCHITECTURE" != "linux_aarch64" ] && [ "$ARCHITECTURE" != "linux_x86_64" ] && [ "$ARCHITECTURE" != "macos_arm64" ]; then
    echo "❌ Invalid architecture: '$ARCHITECTURE'" >&2
    exit 3
fi

# Run python to download SDKs
python3 -m venv venv-sdk;
source venv-sdk/bin/activate
python3 -m pip install --quiet --disable-pip-version-check --no-color -r requirements.txt
python3 fill_sdk_folder.py --architecture $ARCHITECTURE --folder $FOLDER --github-token $GITHUB_TOKEN

# Clean up
deactivate
rm -rf venv-sdk
