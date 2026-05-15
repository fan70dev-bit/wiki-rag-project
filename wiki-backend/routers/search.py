from fastapi import APIRouter, Query
from database.manager import wiki_manager

router = APIRouter(prefix="/api/search", tags=["搜索服务"])

@router.get("")
async def unified_search(
    q: str = Query(..., description="搜索词"),
    mode: str = Query("title", description="搜索模式"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50)
):
    if mode == "title":
        data, total = wiki_manager.search_by_title(q, page, size)
    else:
        data, total = wiki_manager.search_by_vector(q, page, size)
        
    return {
        "status": "success", 
        "page": page, 
        "size": size, 
        "total": total, # 让前端知道总共有多少条
        "data": data
    }

@router.get("/detail/{article_id}")
async def get_detail(article_id: str):
    article = wiki_manager.get_full_article(article_id)
    if not article: return {"status": "error", "message": "文章不存在"}
    return {"status": "success", "data": article}
