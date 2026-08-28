import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.track import Track
from app.models.panel import Panel
from app.models.user import User, UserRole
from app.models.team import Team, TeamStatus
from app.models.event_config import EventConfig

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Seeding tracks...")
        tracks_data = [
            {"name": "AI / ML", "description": "Artificial Intelligence & Machine Learning Track"},
            {"name": "Cybersecurity / IoT", "description": "Hardware, IoT & Zero-Trust Security"},
            {"name": "Fintech / Web3", "description": "DeFi, Fraud Detection & Banking Solutions"},
            {"name": "Open Innovation", "description": "General Software & Creative Solutions"}
        ]
        
        seeded_tracks = []
        for t in tracks_data:
            res = await session.execute(select(Track).where(Track.name == t["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                track = Track(name=t["name"], description=t["description"])
                session.add(track)
                seeded_tracks.append(track)
            else:
                seeded_tracks.append(existing)
        
        await session.flush()

        print("Seeding panels...")
        panel_names = ["Panel 1", "Panel 2", "Panel 3", "Panel 4"]
        seeded_panels = []
        for i, name in enumerate(panel_names):
            res = await session.execute(select(Panel).where(Panel.name == name))
            existing = res.scalar_one_or_none()
            if not existing:
                panel = Panel(name=name, track_id=seeded_tracks[i % len(seeded_tracks)].track_id)
                session.add(panel)
                seeded_panels.append(panel)
            else:
                seeded_panels.append(existing)

        await session.flush()

        print("Seeding Admin user...")
        admin_res = await session.execute(select(User).where(User.email == "admin@vitstudent.ac.in"))
        if not admin_res.scalar_one_or_none():
            admin = User(
                name="Admin User",
                email="admin@vitstudent.ac.in",
                password_hash="24ADM1234",
                role=UserRole.ADMIN
            )
            session.add(admin)

        print("Seeding initial event config...")
        config_res = await session.execute(select(EventConfig).where(EventConfig.id == 1))
        if not config_res.scalar_one_or_none():
            config = EventConfig(
                id=1,
                current_phase="Participants reach",
                active_windows={"review1": False, "review2": False, "final": False}
            )
            session.add(config)

        await session.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
