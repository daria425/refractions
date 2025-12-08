# Refractions

## Overview

Refractions is an multi-agent image generation system built on Bria's FIBO text-to-image model. It transforms simple designs into full editorial photoshoots using **deterministic JSON control** and **AI-powered parameter generation**.

Unlike traditional prompt-based workflows, Refractions uses structured JSON prompts and intelligent agents to generate, critique, and refine images—delivering consistent, reproducible results for professional creative workflows.

**Tech Stack:**

- **Backend:** Python (FastAPI), Gemini (multi-agent orchestration)
- **Frontend:** React + TypeScript (Vite)
- **Image Generation:** Bria AI FIBO (JSON-native text-to-image model)
- **Storage:** Google Cloud Storage, MongoDB

---

## 🏆 Competition Category

**Best JSON-Native or Agentic Workflow**

Refractions showcases FIBO's JSON capabilities through:

1. **Deterministic JSON Control** – Every parameter (camera angle, FOV, lighting, color palette) is structured and reproducible
2. **Multi-Agent Pipeline** – AI agents plan variants, critique outputs, and auto-refine prompts based on visual analysis
3. **Interactive JSON Editing** – Real-time structured prompt editing with diff visualization and one-click regeneration

---

## ✨ Key Features

### 🎯 Core Workflow

- **Upload & Generate** – Provide a product image + style brief → generate 4 editorial shots (hero, detail, flatlay, environment)
- **AI Critique & Auto-Refine** – Agent analyzes generated images, suggests improvements, and regenerates with refined JSON prompts
- **Dynamic Variants** – One-click generation of lighting, camera, or composition variants with deterministic seed control
- **JSON Comparison Viewer** – Side-by-side diff highlighting to track prompt changes across edits

### 🤖 Agentic Intelligence

- **Variant Planner** – Analyzes shot type and suggests relevant parameter variants
- **Visual Critic** – Evaluates generated images against brand guidelines and composition rules
- **Prompt Refiner** – Rewrites structured prompts based on critique feedback

---

## 🚀 Setup Instructions

### Prerequisites

- **Docker** (for backend)
- **Node.js 18+** (for frontend)
- **Google Cloud credentials** (for storage & Gemini)
- **Bria API token** (get from [bria.ai](https://bria.ai))

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/daria425/refractions.git
   cd refractions/api
   ```

2. **Configure environment variables**
   Create a `.env` file in the `api/` directory:

   ```bash
   BRIA_API_TOKEN=your_bria_token
   STORAGE_SERVICE_ACCOUNT_KEY_PATH=./credentials/storage_service_key.json
   VERTEXAI_SERVICE_ACCOUNT_KEY_PATH=./credentials/vertexai_service_key.json
   MONGO_URI=your_mongodb_connection_string
   MONGO_DB_NAME=refractions
   ```

3. **Add Google Cloud credentials**
   Place your service account JSON files in `api/credentials/`:

   - `storage_service_key.json` (for GCS)
   - `vertexai_service_key.json` (for Gemini)

4. **Build and run with Docker**

   ```bash
   chmod +x build.sh clean_rebuild.sh
   ./clean_rebuild.sh
   ```

   The API will start on `http://localhost:8000`

   - Docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Configure environment**
   Create a `.env` file:

   ```bash
   VITE_API_URL=http://localhost:8000
   ```

4. **Start dev server**

   ```bash
   npm run dev
   ```

   Frontend runs on `http://localhost:5173`

---

## Usage

### Basic Workflow

1. **Upload** a product image and enter a style brief (e.g., "minimalist studio shot, soft shadows")
2. **Generate** initial editorial shots (hero, detail, flatlay, environment)
3. **Select** an image and click "Improve with AI" for auto-critique and refinement
4. **Edit** structured prompts directly or use Auto-Edit to generate variants
5. **Compare** JSON diffs to see exactly what changed between versions

### Advanced Features

- **JSON Editor**: Click "Advanced JSON Editor" → modify camera, lighting, color parameters → Apply
- **Auto-Variants**: Click "Auto-Edit" → select variant group (e.g., "lighting_contrast") → Generate All
- **Compare JSON**: Click "Compare JSON" to view side-by-side structured prompt diffs with change highlighting

---

## Architecture

```
User Input (image + brief)
    ↓
[Planning Agent] → Generate structured prompts for 4 shot types
    ↓
[FIBO Generator] → Render images from JSON prompts
    ↓
[Critique Agent] → Analyze outputs, suggest improvements
    ↓
[Refiner Agent] → Rewrite prompts with fixes
    ↓
[FIBO Regenerator] → Produce refined images
```

## License

MIT

---
