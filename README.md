# 🕋 Nugheeth – Hajj Emergency Management System (Backend)

**Nugheeth** is a backend system developed using Django to support emergency response and management during Hajj. It connects pilgrims, emergency responders, administrators, and families through real-time communication and intelligent services like weather alerts and emergency tracking.

> 📌 This repository includes only the **Django backend**. The mobile app (Flutter) and real-time notifications (Firebase) are in separate modules.

---

## 🎯 Project Objectives

- Provide real-time emergency reporting for pilgrims during Hajj.
- Enable Hajj authorities to track and respond to incidents efficiently.
- Allow families to track their relatives and stay updated on emergencies.
- Send automatic alerts during critical weather conditions.

---

## 👥 User Roles & Permissions

| Role                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| **Pilgrim**           | Can report emergencies, receive alerts, and share location with family.     |
| **Emergency Responder** | Receives incidents, confirms status, and updates response. Requires admin approval. |
| **Family Member**     | Monitors pilgrim status, receives location updates.                          |
| **Hajj Administrator** | Views global dashboards, manages users and approvals.                       |
| **Normal User**       | Can browse general safety information or register as pilgrim/family.        |

---

## 🛠️ Tech Stack

| Component      | Technology             |
|----------------|-------------------------|
| Backend        | Django, Django REST Framework |
| Auth           | Email-based + verification code |
| Notifications  | Firebase (FCM)          |
| DB             | Mysql    |
| Scheduling     |  |

---

