from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text
from backend.database import AsyncSessionLocal


async def update_analytics():
    async with AsyncSessionLocal() as db:
        await db.execute(text("""
            INSERT INTO scraper_analytics_history (source, total_articles, total_images, snapshot_time)
            SELECT
                a.source,
                COUNT(DISTINCT a.article_id),
                COUNT(i.article_id),
                NOW()
            FROM articles a
            LEFT JOIN article_images i ON a.article_id = i.article_id
            GROUP BY a.source
        """))

        await db.execute(text("""
            INSERT INTO scraper_analytics (source, total_articles, total_images, updated_at)
            SELECT
                a.source,
                COUNT(DISTINCT a.article_id),
                COUNT(i.article_id),
                NOW()
            FROM articles a
            LEFT JOIN article_images i ON a.article_id = i.article_id
            GROUP BY a.source
            ON CONFLICT (source)
            DO UPDATE SET
                total_articles = EXCLUDED.total_articles,
                total_images = EXCLUDED.total_images,
                updated_at = NOW()
        """))

        await db.commit()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_analytics, "interval", minutes=5)
    scheduler.start()
