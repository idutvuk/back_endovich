from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import SqlQuery, SqlResult
from app.views.deps import get_session

router = APIRouter(prefix="/sql", tags=["sql"])

ROW_LIMIT = 200  # чтобы SELECT * с миллионом строк не уронил ответ


@router.post("", response_model_exclude_none=True)
def execute(data: SqlQuery, session: Session = Depends(get_session)) -> SqlResult:
    try:
        result = session.execute(text(data.query))
        if result.returns_rows:
            rows = result.fetchmany(ROW_LIMIT)
            return SqlResult(
                columns=list(result.keys()),
                rows=[list(row) for row in rows],
            )
        session.commit()
        return SqlResult(rowcount=result.rowcount)
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=str(getattr(exc, "orig", exc))
        )
