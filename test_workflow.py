import asyncio
import httpx
from app.main import app

async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("=== 1. Logging in as Admin (Password: Mann309) ===")
        login_res = await client.post("/auth/user/login", json={
            "email": "admin@vitstudent.ac.in",
            "password": "Mann309"
        })
        assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
        admin_token = login_res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("Admin login successful!")

        print("\n=== 2. Admin Creates Team 1 and Team 2 (@vitstudent.ac.in emails & RegNo passwords) ===")
        team1_res = await client.post("/admin/team/create-with-members", headers=admin_headers, json={
            "team_name": "Team Alpha",
            "track_id": 1,
            "problem_statement_id": 1,
            "members": [
                {
                    "name": "Alpha Leader",
                    "email": "leader.alpha@vitstudent.ac.in",
                    "registration_number": "24BCE0001",
                    "hostel_block": "MH-A",
                    "is_leader": True
                },
                {
                    "name": "Alpha Member",
                    "email": "member.alpha@vitstudent.ac.in",
                    "registration_number": "24BCE0002",
                    "hostel_block": "MH-A",
                    "is_leader": False
                }
            ]
        })
        assert team1_res.status_code == 201, f"Team 1 create failed: {team1_res.text}"
        team1_id = team1_res.json()["team"]["team_id"]
        print(f"Team 1 created with ID: {team1_id}")

        team2_res = await client.post("/admin/team/create-with-members", headers=admin_headers, json={
            "team_name": "Team Beta",
            "track_id": 2,
            "problem_statement_id": 3,
            "members": [
                {
                    "name": "Beta Leader",
                    "email": "leader.beta@vitstudent.ac.in",
                    "registration_number": "24BCE0003",
                    "is_leader": True
                }
            ]
        })
        assert team2_res.status_code == 201, f"Team 2 create failed: {team2_res.text}"
        team2_id = team2_res.json()["team"]["team_id"]
        print(f"Team 2 created with ID: {team2_id}")

        print("\n=== 3. Review 0: Track and Problem Statement (ID) Lock ===")
        # Admin sets phase to Review 0
        phase_res = await client.post("/admin/timeline/phase", headers=admin_headers, json={"phase": "Review 0"})
        assert phase_res.status_code == 200
        assert phase_res.json()["windows"]["review0"] is True

        # Team 1 Leader logs in with Registration Number (24BCE0001)
        t1_login = await client.post("/auth/user/login", json={"email": "leader.alpha@vitstudent.ac.in", "password": "24BCE0001"})
        assert t1_login.status_code == 200, f"Participant login with RegNo failed: {t1_login.text}"
        t1_token = t1_login.json()["access_token"]
        t1_headers = {"Authorization": f"Bearer {t1_token}"}
        print("Team 1 Leader logged in using Registration Number as password!")

        # Team 1 selects track 1 and problem statement 2 in Review 0
        r0_res = await client.post("/users/review0", headers=t1_headers, json={
            "track_id": 1,
            "problem_statement_id": 2
        })
        assert r0_res.status_code == 200 or r0_res.status_code == 201, f"Review 0 submit failed: {r0_res.text}"
        print("Team 1 Review 0 (track_id=1, problem_statement_id=2) locked successfully!")

        # Check Team 1 Dashboard
        dash_res = await client.get("/users/home", headers=t1_headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["team"]["problem_statement_id"] == 2
        assert dash_data["team"]["problem_statement"]["title"] == "Industrial IoT Predictive Maintenance System"
        assert dash_data["team"]["track_id"] == 1
        print("Team 1 Dashboard verified!")

        print("\n=== 4. Review 1: Submitting GitHub (Mandatory) and Optional PPT links ===")
        # Admin sets phase to Review 1
        phase_res = await client.post("/admin/timeline/phase", headers=admin_headers, json={"phase": "Review 1"})
        assert phase_res.status_code == 200
        assert phase_res.json()["windows"]["review1"] is True
        assert phase_res.json()["windows"]["review0"] is False

        # Team 1 submits Review 1 with mandatory github and optional ppt
        r1_res = await client.post("/users/review1", headers=t1_headers, json={
            "github_link": "https://github.com/teamalpha/smart-attest",
            "ppt_link": "https://canva.com/design/teamalpha_presentation",
            "demo_link": "https://youtu.be/demo_video",
            "title": "Alpha IoT Attestation v1.0",
            "description": "Initial architecture and proto demo."
        })
        assert r1_res.status_code == 201, f"Review 1 submit failed: {r1_res.text}"
        t1_r1_submission_id = r1_res.json()["submission_id"]
        assert r1_res.json()["links"]["github"] == "https://github.com/teamalpha/smart-attest"
        assert r1_res.json()["links"]["ppt"] == "https://canva.com/design/teamalpha_presentation"
        print(f"Team 1 Review 1 submission created with ID: {t1_r1_submission_id}")

        print("\n=== 5. Dynamic Multi-Panel Evaluation & 6-Criteria Scoring ===")
        # Panel 1 Judge logs in with Panel 1 Password (BhaiYeKyaHoRahaHai)
        j1_login = await client.post("/auth/user/login", json={"email": "judge1@vitstudent.ac.in", "password": "BhaiYeKyaHoRahaHai"})
        assert j1_login.status_code == 200, f"Judge 1 login failed: {j1_login.text}"
        j1_token = j1_login.json()["access_token"]
        j1_headers = {"Authorization": f"Bearer {j1_token}"}
        print("Panel 1 Judge logged in with password 'BhaiYeKyaHoRahaHai'!")

        # Panel 1 Judge lists teams in hackathon
        panel_teams_res = await client.get("/panels/1/teams", headers=j1_headers)
        assert panel_teams_res.status_code == 200
        assert len(panel_teams_res.json()["teams"]) >= 2
        print(f"Panel 1 can evaluate all {len(panel_teams_res.json()['teams'])} hackathon teams.")

        # Panel 1 Judge views Team 1 evaluation details
        eval_view_res = await client.get(f"/panels/1/team/{team1_id}", headers=j1_headers)
        assert eval_view_res.status_code == 200
        team_eval_data = eval_view_res.json()
        assert team_eval_data["team"]["team_name"] == "Team Alpha"
        assert team_eval_data["team"]["problem_statement"]["id"] == 2
        assert len(team_eval_data["submissions"]) >= 1
        print("Panel evaluation team view loaded successfully!")

        # Panel 1 Judge scores Team 1 on all 6 categories
        score_res = await client.post(f"/reviews/submission/{t1_r1_submission_id}", headers=j1_headers, json={
            "innovation_score": 18.5,
            "technical_complexity_score": 19.0,
            "feasibility_score": 17.5,
            "ui_ux_score": 16.0,
            "presentation_score": 18.0,
            "progress_score": 19.0,
            "comments": "Great IoT security protocol implementation with clear demo!"
        })
        assert score_res.status_code == 200, f"Judge review failed: {score_res.text}"
        assert score_res.json()["total_score"] == 108.0
        print("Judge 6-category evaluation stored with total_score: 108.0!")

        print("\n=== 6. Review 1 Elimination Workflow ===")
        # Admin eliminates Team 2 and shortlists Team 1
        batch_res = await client.post("/admin/teams/batch-status", headers=admin_headers, json={
            "team_ids": [team1_id],
            "status": "shortlisted"
        })
        assert batch_res.status_code == 200

        elim_res = await client.post("/admin/teams/batch-status", headers=admin_headers, json={
            "team_ids": [team2_id],
            "status": "rejected"
        })
        assert elim_res.status_code == 200
        print("Team 1 shortlisted, Team 2 eliminated.")

        print("\n=== 7. Review 2 (Final Review: Mandatory GitHub, Optional PPT & Live URL) ===")
        # Admin transitions to Review 2
        phase_res = await client.post("/admin/timeline/phase", headers=admin_headers, json={"phase": "Review 2"})
        assert phase_res.status_code == 200
        assert phase_res.json()["windows"]["review2"] is True

        # Eliminated Team 2 tries to submit Review 2 -> Expected 403
        t2_login = await client.post("/auth/user/login", json={"email": "leader.beta@vitstudent.ac.in", "password": "24BCE0003"})
        assert t2_login.status_code == 200
        t2_token = t2_login.json()["access_token"]
        t2_headers = {"Authorization": f"Bearer {t2_token}"}
        t2_r2_res = await client.post("/users/review2", headers=t2_headers, json={
            "github_link": "https://github.com/teambeta/final",
            "ppt_link": "https://beta.com/ppt"
        })
        assert t2_r2_res.status_code == 403, f"Eliminated team should be blocked: {t2_r2_res.text}"
        print("Verified: Eliminated team is blocked with 403 Forbidden!")

        # Shortlisted Team 1 submits Review 2 (github mandatory, ppt optional)
        t1_r2_res = await client.post("/users/review2", headers=t1_headers, json={
            "github_link": "https://github.com/teamalpha/smart-attest-final",
            "live_url": "https://alpha-iot-hub.vitstudent.ac.in",
            "ppt_link": "https://canva.com/design/final_deck",
            "video_link": "https://youtube.com/final_pitch"
        })
        assert t1_r2_res.status_code == 201
        print("Team 1 Final Review (Review 2) submitted successfully!")

        print("\n=== 8. Admin Leaderboard & Scorecards ===")
        leaderboard_res = await client.get("/admin/leaderboard", headers=admin_headers)
        assert leaderboard_res.status_code == 200
        leaderboard = leaderboard_res.json()
        assert len(leaderboard) >= 2
        print(f"Leaderboard retrieved with top team: {leaderboard[0]['team_name']} (Score: {leaderboard[0]['total_score']})")
        print("Category Breakdown for Top Team:", leaderboard[0]["scores_breakdown"])

        print("\n=======================================================")
        print("ALL 8 END-TO-END WORKFLOW TESTS PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
