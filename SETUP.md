# Nikhil Mali GitHub Profile README

## 1. Create the profile repository

Create a **public repository named exactly `nikhilkeshavmali`**. GitHub uses this repository's `README.md` as your profile README.

## 2. Copy all files

Copy this package's contents into the repository root.

## 3. Push

```powershell
git add .
git commit -m "feat: create custom GitHub profile README"
git push origin main
```

## 4. Automatic updates

`.github/workflows/update-profile-assets.yml` regenerates the SVG assets daily and can also be run manually from GitHub Actions.

## 5. Customize

- `README.md` — profile text, projects and links
- `scripts/banner/generate.py` — banner design
- `scripts/generate_radars.py` — radar labels/values
- `scripts/cards.py` — GitHub stats/language card
