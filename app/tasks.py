import time
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models

@celery_app.task(name="remediate_incident")
def remediate_incident(incident_id: int):
    """
    Simulates an automated remediation action for an unhealthy service.
    In a real system, this might restart a container, scale a service, etc.
    """
    db = SessionLocal()
    try:
        incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
        if not incident:
            return {"error": "Incident not found"}

        # Simulate the time a real remediation action would take
        time.sleep(5)

        incident.action_taken = "restarted"
        db.commit()

        return {"incident_id": incident_id, "action_taken": "restarted"}
    finally:
        db.close()