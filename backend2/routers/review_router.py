from fastapi import APIRouter, BackgroundTasks

from services.review_service import process_single_review


router = APIRouter()


# =========================
# 接收評論 AI 處理請求
# =========================

@router.post("/internal/process_review/{review_id}")
def process_review(
    review_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
):
    """
    接收 Backend1 傳來的新評論，
    並交由 BackgroundTasks 在背景執行 AI 分析。

    注意：
    API 不等待 AI 完成，
    收到請求後立即回覆。
    """

    content = payload.get(
        "content",
        ""
    )

    background_tasks.add_task(
        process_single_review,
        review_id,
        content,
    )

    return {
        "message": "已接收，背景處理中"
    }