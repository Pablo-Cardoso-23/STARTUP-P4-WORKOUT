from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def p4_chat():
    return {"message": "P4 CHAT"}
