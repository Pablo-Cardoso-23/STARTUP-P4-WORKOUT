from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def listar_treinos():
    return {"message": "Treinos"}
