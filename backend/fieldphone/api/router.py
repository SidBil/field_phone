from fastapi import APIRouter

from fieldphone.api import audit, classifier, ingestion, query, speakers, tone, transcription

api_router = APIRouter()
api_router.include_router(speakers.router, prefix="/speakers", tags=["speakers"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(classifier.router, prefix="/classifier", tags=["classifier"])
api_router.include_router(transcription.router, prefix="/transcription", tags=["transcription"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(tone.router, prefix="/tone", tags=["tone"])
