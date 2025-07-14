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

## 🌦️ Weather Alerts (Auto Notifications)

The system includes a background scheduler that checks the weather every 60 minutes using the **Google Weather API**, and sends FCM notifications to all **pilgrim users**.

### 🔄 How It Works:

- Coordinates: Medina, Saudi Arabia (24.470901°N, 39.612236°E)
- API Used: `https://weather.googleapis.com/v1/currentConditions:lookup`
- Weather data includes:
  - Current weather condition (e.g., rain, clear, dust)
  - Temperature in Celsius
- FCM notification is sent to all pilgrims who have a valid `fcm_token`.

### 🛠️ Implementation Highlights:

- Uses `apscheduler.schedulers.background.BackgroundScheduler` to run every hour.
- Triggers `fetch_weather_and_notify()` from `global_services.googleMap.forecastApi`.
- Integrated inside Django's `AppConfig.ready()` method for automatic startup.

---

## 🛠️ Tech Stack

| Component         | Technology                            |
|------------------|----------------------------------------|
| Backend          | Django, Django REST Framework          |
| Auth             | Email-based + verification code        |
| Notifications    | Firebase Cloud Messaging (FCM)         |
| Weather Alerts   | Google Weather API                     |
| Scheduling       | APScheduler (hourly weather jobs)      |
| DB               | Mysql                   |

---




## 🛠️ Tech Stack

| Component         | Technology                            |
|------------------|----------------------------------------|
| Backend          | Django, Django REST Framework          |
| Auth             | Email-based + verification code        |
| Notifications    | Firebase Cloud Messaging (FCM)         |
| Weather Alerts   | Google Weather API                     |
| Scheduling       | APScheduler (hourly weather jobs)      |
| DB               | Mysql                   |

---
