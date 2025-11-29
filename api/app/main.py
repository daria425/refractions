from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from app.db.db_collections import GeneratedImagesCollection
from app.models.image_data import ImageEditRequestBody
from app.image_orchestrator import ImageGenOrchestrator
from app.image_gen_client import get_image_gen_client
from app.db.db_connection import DatabaseConnection
from app.utils.logger import logger


def lifespan(app: FastAPI):
    db_connection = DatabaseConnection.get_instance()
    db_connection.initialize_mongo_client()
    yield
    db_connection.close_connection()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
@app.post("/generate")
async def generate_initial_image(
    method: Literal["structured_prompt_to_image", "image_to_image", "text_to_image"] = Query(
        ..., 
        description="The image generation method to use",
        enum=["structured_prompt_to_image", "image_to_image", "text_to_image"]  # initial gen runs with text to image because that is the method under the hood
    ),
    vision: str = Form(...), 
    image_file: UploadFile = File(...),
    images_collection: GeneratedImagesCollection = Depends(GeneratedImagesCollection)
):
    """Generate initial campaign images from CAD design + vision."""
    # CHANGE: validate inputs early
    if not vision.strip():
        raise HTTPException(status_code=400, detail="Vision text cannot be empty")
    
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    
    try:
        image_bytes = await image_file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded image is empty")
        
        orchestrator = ImageGenOrchestrator(vision=vision, uploaded_image=image_bytes)
        image_gen_client = get_image_gen_client()
        
        if method != "text_to_image":
            raise HTTPException(status_code=400, detail=f"Unsupported generation method: {method}") # i dont have that yet :(
        results = await orchestrator.run_initial_gen(
            image_gen_client=image_gen_client,
            images_collection=images_collection,
            wait_time=0,
            max_concurrency=4,
            per_request_timeout=120
        )
        
        successes = [r for r in results if r.get("status") == "ok"]
        failures = [r for r in results if r.get("status") == "error"]
        
        return {
            "status": "completed",
            "total": len(results),
            "successful": len(successes),
            "failed": len(failures),
            "results": results,
            "message": f"Generated {len(successes)}/{len(results)} shots successfully"
        }
        
    except HTTPException:
        raise  #
    except Exception as e:
        logger.error(f"Generation failed: {e}") 
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )
    

@app.post("/edit")
async def edit_endpoint(
    request_body: ImageEditRequestBody, images_collection: GeneratedImagesCollection=Depends(GeneratedImagesCollection),     method: Literal["from_structured_prompt"] = Query(
        ..., 
        description="The image generation method to use",
        enum=["from_structured_prompt"]  # just the one for now
    ),
):
    try: 
        orchestrator=ImageGenOrchestrator()
        image_gen_client=get_image_gen_client()
        user_structured_prompt=request_body.user_structured_prompt
        if not user_structured_prompt:
            raise HTTPException(status_code=400, detail="user_structured_prompt is required for this method")
        result=await orchestrator.run_json_edit(image_gen_client, 
                                                images_collection,
                                                request_id=request_body.request_id, 
                                                shot_type=request_body.shot_type, 
                                                user_structured_prompt=request_body.user_structured_prompt)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}") 
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )