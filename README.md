# Medication Reminder App

A simple static web app for reminding older adults to take their medicine.

## Run locally

Open the app in a browser with:

- http://127.0.0.1:8000/

Or from the project folder run:

```bash
python -m http.server 8000
```

## Run as a Windows desktop app

From the project folder run:

```powershell
cd C:\Users\Admin\medication-reminder-app
npm install
npm run start
```

This starts the app in an Electron desktop window.

## Package for Windows (optional)

Install `electron-packager` as a dev dependency, then run:

```powershell
npm install --save-dev electron-packager
npx electron-packager . "Medication Reminder" --platform=win32 --arch=x64 --out=dist --overwrite
```

Then open the generated `dist\Medication Reminder-win32-x64` folder.

## Deploy to GitHub Pages

1. Create a GitHub repository.
2. Push these files to the repository.
3. In GitHub, open Settings > Pages.
4. Select the GitHub Actions deployment source.
5. The workflow in `.github/workflows/deploy.yml` will publish the app.
