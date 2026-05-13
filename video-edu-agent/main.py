from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import Session, Project
from llm import generate_scenes
from tts import generate_audio
from slide import create_slide
from subtitle import generate_srt
from video import render_video
import uuid, json, os

app = FastAPI(
    title="Video Edu Agent",
    description="Generate educational videos automatically using AI — 100% Free",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("outputs", exist_ok=True)


class Brief(BaseModel):
    topic        : str
    audience     : str = "pelajar SMA"
    duration_sec : int = 60
    language     : str = "id"


def process_video(project_id: str, brief: Brief):
    """Background task: generate scenes → audio → slides → video."""
    db = Session()
    project = db.query(Project).filter(Project.id == project_id).first()

    try:
        # 2. Generate script via Gemini
        scenes = generate_scenes(brief.topic, brief.audience,
                                 brief.duration_sec, brief.language)
        project.scenes_json = json.dumps(scenes)
        project.status = "rendering"
        db.commit()

        # 3. Buat folder per project
        folder = f"outputs/{project_id}"
        os.makedirs(f"{folder}/audio",  exist_ok=True)
        os.makedirs(f"{folder}/slides", exist_ok=True)

        # 4. Generate audio + slide per scene
        for scene in scenes:
            sid = scene["scene_id"]
            generate_audio(scene["narration"],
                           f"{folder}/audio/scene_{sid}.mp3",
                           brief.language)
            create_slide(scene["visual"], sid,
                         f"{folder}/slides/scene_{sid}.png")

        # 5. Generate subtitle .srt
        generate_srt(scenes, f"{folder}/subtitle.srt")

        # 6. Render video final
        video_path = f"{folder}/final.mp4"
        render_video(scenes, f"{folder}/audio", f"{folder}/slides", video_path)

        project.video_path = video_path
        project.status     = "completed"
        db.commit()

    except Exception as e:
        project.status    = "failed"
        project.error_msg = str(e)
        db.commit()
        raise

    finally:
        db.close()


@app.post("/create-video", summary="Buat video edukasi baru (async)")
def create_video(brief: Brief, background_tasks: BackgroundTasks):
    """
    Kirim brief → video diproses di background.
    Gunakan GET /status/{project_id} untuk cek progres.
    """
    project_id = str(uuid.uuid4())[:8]
    db = Session()
    try:
        project = Project(
            id=project_id,
            topic=brief.topic,
            audience=brief.audience,
            duration_sec=brief.duration_sec,
            language=brief.language,
            status="planning"
        )
        db.add(project)
        db.commit()
    finally:
        db.close()

    background_tasks.add_task(process_video, project_id, brief)

    return {
        "project_id": project_id,
        "status":     "planning",
        "message":    "Video sedang diproses. Cek status di /status/" + project_id,
        "status_url": f"/status/{project_id}",
        "download":   f"/download/{project_id}"
    }


@app.get("/status/{project_id}", summary="Cek status project")
def get_status(project_id: str):
    db = Session()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    if not project:
        raise HTTPException(404, "Project tidak ditemukan")
    return {
        "project_id":  project_id,
        "status":      project.status,
        "topic":       project.topic,
        "audience":    project.audience,
        "duration_sec": project.duration_sec,
        "language":    project.language,
        "created_at":  str(project.created_at),
        "error":       project.error_msg,
        "download":    f"/download/{project_id}" if project.status == "completed" else None,
    }


@app.get("/download/{project_id}", summary="Download video final (.mp4)")
def download_video(project_id: str):
    db = Session()
    project = db.query(Project).filter(Project.id == project_id).first()
    db.close()
    if not project:
        raise HTTPException(404, "Project tidak ditemukan")
    if project.status != "completed" or not project.video_path:
        raise HTTPException(400, f"Video belum tersedia. Status: {project.status}")
    return FileResponse(
        project.video_path,
        media_type="video/mp4",
        filename=f"video_{project_id}.mp4"
    )


@app.get("/projects", summary="List semua project")
def list_projects():
    db = Session()
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    db.close()
    return [
        {
            "project_id":  p.id,
            "topic":       p.topic,
            "status":      p.status,
            "created_at":  str(p.created_at),
        }
        for p in projects
    ]


@app.get("/", summary="Health check")
def root():
    return {
        "service": "Video Edu Agent",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs"
    }
