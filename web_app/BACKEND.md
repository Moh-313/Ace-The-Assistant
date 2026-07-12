# Ace The Assistant — Backend Documentation

## Overview

The Ace backend controls the functional behavior of the web application.

It is responsible for:

- Managing Ace's current state
- Updating Dashboard data
- Recording Terminal activity
- Preparing the application for Raspberry Pi integration
- Coordinating future voice-assistant functionality

The visual design, colors, animations, logo, and styling are handled separately by the frontend.

---

## Backend Structure

```text
backend/
├── assistant.py
├── dashboard_manager.py
├── terminal_manager.py
├── pi_connection.py
└── assistant_state.py