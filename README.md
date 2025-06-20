
![Strivo](https://github.com/user-attachments/assets/89062650-bdcd-4f52-a048-b61a2361b2e8)


# 📁 Strivo

**Strivo** is a modern project management system built on the [Frappe Framework](https://frappeframework.com/). It enables teams to collaborate on projects through structured workflows involving tasks, milestones, roles, and permissions.

---

## 🚀 Features

- 🧩 Projects with assigned project managers and team members
- ✅ Tasks with dependencies and comments
- 🎯 Milestones tracked by project managers and visible to teams
- 🔐 Role-based permissions for Project Managers and Team Members
- 📬 RESTful API endpoints for integration and automation

---

## 🛠️ Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app strivo
```

## 🧪 API Testing with Postman

A ready-to-use **Postman Collection** is available to test all Strivo API endpoints.

📁 **Location:**
`/apps/strivo/strivo/documentation/strivo.postman_collection.json`

📌 **Instructions:**

1. Open [Postman](https://www.postman.com/downloads/).
2. Click on **Import**.
3. Select the file `strivo.postman_collection.json` from the path above.
4. Set your environment variables (e.g., `base_url`, authentication tokens).
5. Use the collection to test API features like creating projects, adding tasks, managing milestones, and more.

> This is ideal for developers and testers who want to explore or integrate with the Strivo project via its REST API.

---
