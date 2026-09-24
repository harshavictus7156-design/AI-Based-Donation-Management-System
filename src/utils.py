"""
Utility helpers for UI styling, status badges, formatting, and file processing.
"""

import os
import io
import base64
from datetime import datetime
from PIL import Image
import streamlit as st


def format_date(dt) -> str:
    """Formats a datetime or date object into a human-readable string."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt
    return dt.strftime("%b %d, %Y")


def format_datetime(dt) -> str:
    """Formats a datetime object into a human-readable string with time."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            return dt
    return dt.strftime("%b %d, %Y • %I:%M %p")


def get_status_badge(status: str) -> str:
    """Generates an HTML styled badge for different status types."""
    status_lower = str(status).strip().lower()
    
    color_map = {
        "pending": ("#f59e0b", "rgba(245, 158, 11, 0.15)"),
        "approved": ("#10b981", "rgba(16, 185, 129, 0.15)"),
        "accepted": ("#10b981", "rgba(16, 185, 129, 0.15)"),
        "rejected": ("#ef4444", "rgba(239, 68, 68, 0.15)"),
        "collected": ("#8b5cf6", "rgba(139, 92, 246, 0.15)"),
        "confirmed": ("#3b82f6", "rgba(59, 130, 246, 0.15)"),
        "dispatched": ("#06b6d4", "rgba(6, 182, 212, 0.15)"),
        "delivered": ("#10b981", "rgba(16, 185, 129, 0.15)"),
        "cancelled": ("#64748b", "rgba(100, 116, 139, 0.15)"),
        "urgent": ("#ef4444", "rgba(239, 68, 68, 0.15)"),
        "high": ("#f97316", "rgba(249, 115, 22, 0.15)"),
        "medium": ("#3b82f6", "rgba(59, 130, 246, 0.15)"),
        "low": ("#10b981", "rgba(16, 185, 129, 0.15)"),
    }
    
    text_color, bg_color = color_map.get(status_lower, ("#94a3b8", "rgba(148, 163, 184, 0.15)"))
    
    return f"""
    <span style="
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.025em;
        text-transform: uppercase;
        color: {text_color};
        background: {bg_color};
        border: 1px solid {text_color}40;
    ">
        {status}
    </span>
    """


def get_rank_badge(rank: int) -> tuple[str, str, str]:
    """Returns (Tier Name, Badge Color, Icon) for donor rankings."""
    if rank == 1:
        return "Champion Gold", "#f59e0b", "👑"
    elif rank == 2:
        return "Master Silver", "#94a3b8", "🥈"
    elif rank == 3:
        return "Leader Bronze", "#d97706", "🥉"
    elif rank <= 10:
        return "Top Philanthropist", "#8b5cf6", "⭐"
    else:
        return "Community Contributor", "#3b82f6", "❤️"


def save_uploaded_file(uploaded_file, destination_folder: str) -> str:
    """Saves a Streamlit UploadedFile to local media directory and returns relative path."""
    if not uploaded_file:
        return ""
    
    os.makedirs(destination_folder, exist_ok=True)
    file_extension = os.path.splitext(uploaded_file.name)[1]
    import uuid
    unique_filename = f"{uuid.uuid4().hex[:12]}_{uploaded_file.name}"
    file_path = os.path.join(destination_folder, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return file_path


def image_to_base64(image_input) -> str:
    """Converts a PIL Image or image file path to a base64 string."""
    try:
        if isinstance(image_input, str):
            with open(image_input, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        elif isinstance(image_input, Image.Image):
            buffered = io.BytesIO()
            image_input.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception:
        return ""
    return ""
