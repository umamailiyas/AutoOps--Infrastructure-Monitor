from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app import models, schemas
from app.tasks import remediate_incident


Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoOps Infra Monitor")

@app.get("/")
def root():
    return {"message": "AutoOps is running"}

@app.post("/services", response_model=schemas.ServiceResponse)
def register_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Service).filter(models.Service.name == service.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Service already registered")
    new_service = models.Service(name=service.name, status="unknown")
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@app.get("/services", response_model=list[schemas.ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.post("/health-check")
def report_health(check: schemas.HealthCheckIn, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.name == check.service_name).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.status = check.status
    db.commit()

    if check.status == "unhealthy":
        incident = models.Incident(
            service_name=check.service_name,
            issue=check.issue or "Unspecified issue",
            action_taken="pending"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        remediate_incident.delay(incident.id)
        return {"message": "Incident logged, remediation triggered"}
    

@app.get("/incidents", response_model=list[schemas.IncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()