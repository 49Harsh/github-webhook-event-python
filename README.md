# GitHub Webhook Assignment: End-to-End Setup

## 1. Prerequisites

- Python 3.x
- MongoDB (local instance running on default port 27017)
- GitHub account

## 2. Setup `webhook-repo`

```
cd webhook-repo
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

Start MongoDB if not already running.

## 3. Run the Flask App

```
python app.py
```

The app will be available at http://localhost:5000

## 4. Setup `action-repo`

- Create a new repository on GitHub (e.g., `action-repo`).
- Make some commits, open pull requests, and merge PRs to generate webhook events.

## 5. Configure GitHub Webhook

- Go to your `action-repo` on GitHub.
- Settings > Webhooks > Add webhook
  - **Payload URL:** `http://<your-ip>:5000/webhook` (use your public IP if testing from GitHub, or use [ngrok](https://ngrok.com/) for local development)
  - **Content type:** `application/json`
  - **Events:** Select "Just the push event" and "Pull requests"
  - Save

## 6. View Events

- Open http://localhost:5000 in your browser.
- The UI will update every 15 seconds with new events from MongoDB.

---

## MongoDB Schema

```
{
  _id: ObjectId,
  request_id: string, // Git commit hash or PR ID
  author: string,     // GitHub user name
  action: string,     // Enum: "PUSH", "PULL_REQUEST", "MERGE"
  from_branch: string,
  to_branch: string,
  timestamp: string   // UTC ISO format
}
```

---

## Notes

- For public webhook delivery, use [ngrok](https://ngrok.com/) to tunnel your local Flask server.
- The UI is plain HTML/JS for simplicity.
- You can extend the schema or UI as needed.
