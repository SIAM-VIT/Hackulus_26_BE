import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
import app.models  # Ensure all models are registered in Base.metadata
from app.models.event_config import EventConfig
from app.models.user import User, UserRole
from app.models.panel import Panel
from app.models.track import Track
from app.routes import auth, users, teams, submissions, reviews, admin, panels

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create all tables in PostgreSQL on startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/verified successfully on startup.")

        async with AsyncSessionLocal() as session:
            # 1. Ensure default EventConfig row exists
            res = await session.execute(select(EventConfig).where(EventConfig.id == 1))
            config = res.scalar_one_or_none()
            if not config:
                config = EventConfig(
                    id=1,
                    current_phase="Participants reach",
                    active_windows={"review0": False, "review1": False, "review2": False}
                )
                session.add(config)
                print("✅ Default EventConfig row initialized.")

            # 2. Ensure default Tracks exist
            default_tracks = [
                {"name": "IOT", "description": "Internet of Things & Connected Devices Track"},
                {"name": "Creative Tech", "description": "Interactive Media, Generative Design & AR/VR Track"},
                {"name": "FinTech", "description": "Micro-Transactions, Financial Inclusion & Security Track"},
                {"name": "Cybersecurity", "description": "Zero-Trust, Threat Detection & Privacy Track"},
                {"name": "VIT Centric", "description": "Campus Student Experience & Safety Solutions Track"},
                {"name": "Environments Sustainability", "description": "Green Tech, Circular Economy & Carbon Footprint Track"}
            ]
            for t in default_tracks:
                t_res = await session.execute(select(Track).where(Track.name == t["name"]))
                if not t_res.scalar_one_or_none():
                    session.add(Track(name=t["name"], description=t["description"]))

            # 3. Ensure 5 Evaluation Panels exist
            seeded_panels = {}
            for i in range(1, 6):
                pname = f"Panel {i}"
                p_res = await session.execute(select(Panel).where(Panel.name == pname))
                panel_obj = p_res.scalar_one_or_none()
                if not panel_obj:
                    panel_obj = Panel(name=pname, description=f"Hackathon Evaluation {pname}")
                    session.add(panel_obj)
                    await session.flush()
                seeded_panels[i] = panel_obj

            # 4. Ensure Admin user exists
            admin_email = "admin@vitstudent.ac.in"
            admin_res = await session.execute(select(User).where(User.email == admin_email))
            existing_admin = admin_res.scalar_one_or_none()
            if not existing_admin:
                session.add(User(
                    name="Admin User",
                    email=admin_email,
                    password_hash="Mann309",
                    role=UserRole.ADMIN
                ))
                print("✅ Admin user created (admin@vitstudent.ac.in).")
            else:
                existing_admin.password_hash = "Mann309"
                existing_admin.role = UserRole.ADMIN

            # 5. Ensure 5 Judge users exist
            judge_passwords = {
                1: "BhaiYeKyaHoRahaHai",
                2: "MoneyFollowsMyBrother",
                3: "PaisaHiPaisaHoga",
                4: "YeDukhKaheNhiKhatmHotaBhai",
                5: "BeteMojKarDi"
            }
            for i in range(1, 6):
                j_email = f"judge{i}@vitstudent.ac.in"
                j_res = await session.execute(select(User).where(User.email == j_email))
                existing_judge = j_res.scalar_one_or_none()
                panel_id = seeded_panels.get(i).panel_id if seeded_panels.get(i) else None
                if not existing_judge:
                    session.add(User(
                        name=f"Judge Panel {i}",
                        email=j_email,
                        password_hash=judge_passwords[i],
                        role=UserRole.JUDGE,
                        panel_id=panel_id
                    ))
                else:
                    existing_judge.password_hash = judge_passwords[i]
                    existing_judge.role = UserRole.JUDGE
                    existing_judge.panel_id = panel_id

            await session.commit()
            print("✅ Default Admin, Judges (1-5), Panels (1-5), and Tracks initialized.")
    except Exception as e:
        print(f"❌ Warning: Could not initialize database seed on startup: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend for Hackulus Hackathon Management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload dir exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(submissions.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(panels.router)

@app.get("/")
async def root():
    return {
        "message": "Hackulus 2026 FastAPI Backend is running!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="Health check / Keep-alive ping endpoint")
@app.get("/ping", summary="Health check / Keep-alive ping endpoint")
async def health_check():
    return {
        "status": "ok",
        "alive": True
    }
