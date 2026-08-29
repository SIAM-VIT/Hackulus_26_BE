import asyncio
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.track import Track
from app.models.problem_statement import ProblemStatement
from app.models.user import User, UserRole
from app.models.team import Team, TeamStatus
from app.models.event_config import EventConfig

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Seeding tracks...")
        tracks_data = [
            {"name": "IOT", "description": "Internet of Things & Connected Devices Track"},
            {"name": "Creative Tech", "description": "Interactive Media, Generative Design & AR/VR Track"},
            {"name": "FinTech", "description": "Micro-Transactions, Financial Inclusion & Security Track"},
            {"name": "Cybersecurity", "description": "Zero-Trust, Threat Detection & Privacy Track"},
            {"name": "VIT Centric", "description": "Campus Student Experience & Safety Solutions Track"},
            {"name": "Environments Sustainability", "description": "Green Tech, Circular Economy & Carbon Footprint Track"}
        ]
        
        seeded_tracks = {}
        for t in tracks_data:
            res = await session.execute(select(Track).where(Track.name == t["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                track = Track(name=t["name"], description=t["description"])
                session.add(track)
                await session.flush()
                seeded_tracks[t["name"]] = track
            else:
                seeded_tracks[t["name"]] = existing

        print("Seeding problem statements...")
        sample_ps = [
            # IOT
            {
                "track_name": "IOT",
                "title": "Zero-Touch Smart Home Device Attestation",
                "description": "Develop a lightweight authentication protocol ensuring IoT devices joining smart home networks are automatically authenticated and tamper-proof."
            },
            {
                "track_name": "IOT",
                "title": "Industrial IoT Predictive Maintenance System",
                "description": "Build an IoT sensor telemetry monitoring framework to predict hardware failures in industrial equipment before downtime occurs."
            },
            # Creative Tech
            {
                "track_name": "Creative Tech",
                "title": "Generative AI Interactive Storytelling Engine",
                "description": "Create an AI-driven digital art and interactive narrative generator empowering game creators and visual storytellers."
            },
            {
                "track_name": "Creative Tech",
                "title": "Spatial Audio & AR Campus Navigation",
                "description": "Design an augmented reality campus experience featuring spatial audio guidance and interactive 3D overlays."
            },
            # FinTech
            {
                "track_name": "FinTech",
                "title": "Real-Time Micro-Transaction Fraud Detection",
                "description": "Develop a fraud prediction engine using behavioral biometrics and metadata to detect micro-transaction anomalies."
            },
            {
                "track_name": "FinTech",
                "title": "Gamified Financial Literacy for Youth",
                "description": "Build an interactive platform teaching budgeting, saving, and investing using gamified real-life scenarios."
            },
            # Cybersecurity
            {
                "track_name": "Cybersecurity",
                "title": "Real-Time Live Video Deepfake Detection",
                "description": "Construct an ultra-low-latency detection system analyzing video streams for deepfake manipulations."
            },
            {
                "track_name": "Cybersecurity",
                "title": "Automated API Vulnerability & Secret Scanner",
                "description": "Create a security tool that scans public and private API endpoints for token leaks, CORS misconfigurations, and auth flaws."
            },
            # VIT Centric
            {
                "track_name": "VIT Centric",
                "title": "Smart Campus Lost & Found Recovery System",
                "description": "Design a secure geotagged recovery platform matching lost student items with verified found reports."
            },
            {
                "track_name": "VIT Centric",
                "title": "VIT Student Skill & Project Matchmaker",
                "description": "Build an automated dashboard connecting students with complementary skill sets for hackathons, research projects, and clubs."
            },
            # Environments Sustainability
            {
                "track_name": "Environments Sustainability",
                "title": "Micro-Logistics Network for Surplus Food",
                "description": "Design a logistics platform connecting food producers/restaurants with NGOs to eliminate food waste."
            },
            {
                "track_name": "Environments Sustainability",
                "title": "Hyper-Local Carbon Footprint & Waste Tracker",
                "description": "Develop a real-time carbon emission tracking application offering hyper-local sustainable lifestyle swaps."
            }
        ]

        for ps in sample_ps:
            tk = seeded_tracks.get(ps["track_name"])
            if tk:
                res = await session.execute(
                    select(ProblemStatement).where(
                        ProblemStatement.title == ps["title"],
                        ProblemStatement.track_id == tk.track_id
                    )
                )
                if not res.scalar_one_or_none():
                    new_ps = ProblemStatement(
                        title=ps["title"],
                        description=ps["description"],
                        track_id=tk.track_id
                    )
                    session.add(new_ps)

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
