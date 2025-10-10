from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import logging

from app import crud

router = APIRouter()

@router.post("/sync", response_model=Dict[str, Any])
async def sync_database(force: bool = Body(False, description="Whether to clear the database before syncing")):
    """
    Synchronize the database with external data.
    If force=True, clears the database before syncing.
    """
    try:
        if force:
            logging.info("Force clearing database before sync")
            crud.clear_database()
            
        return {"status": "success", "message": "Database ready for synchronization"}
    except Exception as e:
        logging.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync database: {str(e)}")
