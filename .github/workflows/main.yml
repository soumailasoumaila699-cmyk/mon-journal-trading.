name: Build-APK
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Flet
        run: |
          pip install --upgrade pip
          pip install flet

      - name: Build APK
        run: |
          flet build apk

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: MonAppTrading
          path: build/apk/*.apk
