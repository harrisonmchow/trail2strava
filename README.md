# AllTrails to Strava

I currently don't have Strava premium or a Garmin to automatically log my hikes/trail runs but I currently use AllTrails Pro membership for trail navigation. 

Strava doesn't have an AllTrails integration, so there's no way to automatically sync your hikes. This app bridges that gap — upload a GPX file exported from AllTrails and it gets pushed to Strava as a fully detailed activity with GPS track, map, elevation, and auto-calculated splits.

## User Flow

1. Connect your Strava account via OAuth
2. Download a GPX file from AllTrails (Activity > ... > Download Route > GPX Track)
3. Drag & drop the GPX file into the app
4. Preview stats and edit the title if needed
5. Click "Sync to Strava" — the activity appears in Strava with the full GPS track, map, and splits

## Tech Stack

- **Frontend:** Next.js (React 19), Tailwind CSS, Framer Motion
- **Backend:** FastAPI (Python), Uvicorn
- **Strava Integration:** OAuth 2.0 auth flow, Strava API for activity upload
- **GPX Parsing:** Server-side parsing to extract GPS tracks and metadata

## Running Locally

### Prerequisites

- Node.js
- Python 3
- A [Strava API application](https://www.strava.com/settings/api) (you'll need the Client ID and Client Secret)

### 1. Clone the repo

```sh
git clone https://github.com/harrisonmchow/trail2strava.git
cd AllTrailsToStrava
```

### 2. Set up environment variables

Create `backend/.env`:

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
SESSION_SECRET=some-random-secret
```

### 3. Install dependencies

```sh
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

Or use the Makefile:

```sh
make install
```

### 4. Start the dev servers

```sh
make dev
```

This runs the frontend (http://localhost:3000) and backend (http://localhost:8000) concurrently.
