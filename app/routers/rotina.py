from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_rotinas():
    return {"message": "Rotinas"}
