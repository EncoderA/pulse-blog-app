from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db

router = APIRouter(prefix="/scrapper-analytics", tags=["Scrapper Analytics"])


@router.get("/")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT source, total_articles, total_images FROM scraper_analytics")
    )
    return [
        {"source": row[0], "articles": row[1], "images": row[2]}
        for row in result.fetchall()
    ]


@router.post("/refresh")
async def refresh_analytics(db: AsyncSession = Depends(get_db)):
    # 1. INSERT INTO HISTORY (no overwrite)
    await db.execute(text("""
        INSERT INTO scraper_analytics_history (source, total_articles, total_images, snapshot_time)
        SELECT 
            a.source,
            COUNT(DISTINCT a.article_id),
            COUNT(i.article_id),
            NOW()
        FROM articles a
        LEFT JOIN article_images i 
            ON a.article_id = i.article_id
        GROUP BY a.source
    """))

    # 2. UPDATE LATEST TABLE (overwrite)
    await db.execute(text("""
        INSERT INTO scraper_analytics (source, total_articles, total_images, updated_at)
        SELECT 
            a.source,
            COUNT(DISTINCT a.article_id),
            COUNT(i.article_id),
            NOW()
        FROM articles a
        LEFT JOIN article_images i 
            ON a.article_id = i.article_id
        GROUP BY a.source
        ON CONFLICT (source)
        DO UPDATE SET
            total_articles = EXCLUDED.total_articles,
            total_images = EXCLUDED.total_images,
            updated_at = NOW()
    """))

    await db.commit()
    return {"message": "Analytics updated + history stored"}


@router.get("/trend")
async def trend(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        WITH latest_per_day AS (
            SELECT
                source,
                DATE(snapshot_time) AS date,
                total_articles,
                ROW_NUMBER() OVER (PARTITION BY source, DATE(snapshot_time) ORDER BY snapshot_time DESC) AS rn
            FROM scraper_analytics_history
        )
        SELECT date, SUM(total_articles) AS total_articles
        FROM latest_per_day
        WHERE rn = 1
        GROUP BY date
        ORDER BY date
    """))

    return [{"date": str(row[0]), "articles": row[1]} for row in result.fetchall()]



@router.get("/comparison")
async def comparison(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT 
            source,
            DATE(snapshot_time) as date,
            total_articles
        FROM scraper_analytics_history
        ORDER BY source, date;
    """))

    data = result.fetchall()

    return [
        {
            "source": row[0],
            "date": str(row[1]),
            "articles": row[2]
        }
        for row in data
    ]


@router.get("/growth")
async def growth(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        WITH ranked AS (
            SELECT
                source,
                total_articles,
                total_articles - LAG(total_articles) OVER (
                    PARTITION BY source ORDER BY snapshot_time
                ) AS growth,
                ROW_NUMBER() OVER (PARTITION BY source ORDER BY snapshot_time DESC) AS rn
            FROM scraper_analytics_history
        )
        SELECT source, total_articles, growth
        FROM ranked
        WHERE rn = 1
        ORDER BY source
    """))

    data = result.fetchall()

    return [
        {"source": row[0], "articles": row[1], "growth": row[2] or 0}
        for row in data
    ]

