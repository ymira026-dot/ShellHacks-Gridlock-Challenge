# GridSync

GridSync is a utility coordination intelligence platform for finding construction projects from different utilities that are close in distance and timing.

## Current MVP

The current implementation includes:

- A normalized Pydantic project schema.
- Clearly labeled demo data for two utilities.
- Deterministic Haversine distance calculations.
- Inclusive schedule-overlap and nearby-start calculations.
- Transparent project compatibility and HIGH/MEDIUM/LOW priority rules.
- FastAPI endpoints for projects, utilities, opportunities, and configurable analysis.
- A React/Vite dashboard with a Leaflet/OpenStreetMap project map.
- Opportunity lines, priority indicators, source URLs, and plain-English explanations.

The demo records are intentionally marked as demo records. Public utility adapters will be added before presenting real-source results.

## Run Locally

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The development proxy forwards `/api` requests to the FastAPI server.

## Tests

```bash
cd backend
python -m pytest -q
```

## Architecture

```text
Public or demo utility data
	-> ingestion adapter
	-> normalized Project schema
	-> deterministic analysis engine
	-> FastAPI
	-> React dashboard
```

The analysis engine never uses an LLM for distance or date calculations. AI enrichment can be added later for messy descriptions, resource suggestions, and explanations without changing the core detection rules.