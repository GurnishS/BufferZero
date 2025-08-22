import asyncio
import random
from app.logger import logger
from app.config import COOKIE_PATH
from yt_dlp import YoutubeDL
import functools


class DownloadManager:
    """
    Manages asynchronous downloading of files with concurrency control,
    a work queue, and duplicate prevention.
    """

    def __init__(self, max_workers = 10):
        if max_workers <= 0:
            raise ValueError("max_workers must be a positive integer")

        self.max_workers = max_workers
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(self.max_workers)
        self.active_downloads = set()
        self.workers = []
        self._running = False
        logger.info(f"DownloadManager initialized with {self.max_workers} max workers.")

    async def _download_file(self, task_details):
        """
        Actual YT-DLP downloader, running the blocking call in a thread executor.
        """
        video_id = task_details['video_id']
        url = task_details['url']
        quality = task_details['quality_tag']
        opts = task_details['ydl_opts']
        download_id = f"{video_id}_{quality}"

        logger.info(f"Starting download for: {download_id}")
        logger.debug(f"yt-dlp options for {video_id}: {opts}")
        
        try:
            # Get the current asyncio event loop
            loop = asyncio.get_running_loop()

            # Use functools.partial to prepare the blocking function call
            with YoutubeDL(opts) as ydl:
                blocking_call = functools.partial(ydl.download, [url])
                
                # Run the blocking ydl.download call in a separate thread pool (the default executor)
                # This prevents it from blocking the main asyncio event loop.
                await loop.run_in_executor(None, blocking_call)
            
            logger.info(f"Finished download for: {download_id}")

        except Exception as e:
            logger.error(f"Error downloading {download_id}: {e}")
        finally:
            # This is the "unlock" step.
            if download_id in self.active_downloads:
                self.active_downloads.remove(download_id)
                logger.debug(f"Released lock for: {download_id}")

    async def _worker(self, worker_id):
        logger.info(f"Worker-{worker_id} started.")
        while self._running:
            try:
                task_details = await self.queue.get()
                async with self.semaphore:
                    await self._download_file(task_details)
                self.queue.task_done()
            except asyncio.CancelledError:
                logger.info(f"Worker-{worker_id} is shutting down.")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in Worker-{worker_id}: {e}")

    def start(self):
        if self._running:
            return
        self._running = True
        self.workers = [asyncio.create_task(self._worker(i)) for i in range(self.max_workers)]
        logger.info("DownloadManager started.")

    async def shutdown(self):
        if not self._running:
            return
        logger.info("Shutting down...")
        await self.queue.join()
        self._running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("DownloadManager shut down.")

    def add_download(self, video_id, url, quality_tag, ydl_opts, progress_hook=None):
        if not self._running:
            logger.error("Manager is not running. Call start() first.")
            return False

        download_id = f"{video_id}_{quality_tag}"

        if download_id in self.active_downloads:
            logger.warning(f"Duplicate download ignored: {download_id}")
            return False
        
        self.active_downloads.add(download_id)
        
        if progress_hook:
            ydl_opts.setdefault('progress_hooks', []).append(progress_hook)

        task_details = {
            "video_id": video_id,
            "url": url,
            "quality_tag": quality_tag,
            "ydl_opts": ydl_opts
        }
        
        self.queue.put_nowait(task_details)
        logger.info(f"Queued download: {download_id}")
        return True

# --- Corrected Test Script ---
async def main():
    download_manager = DownloadManager(max_workers=3)
    download_manager.start()

    tasks = [
        {
            "video_id": "BwfjneL67ZU", "url": "https://www.youtube.com/watch?v=BwfjneL67ZU",
            "quality_tag": "1080p", "ydl_opts": {"format": "bestvideo[height<=1080]+bestaudio/best"}
        },
        {
            "video_id": "BwfjneL67ZU", "url": "https://www.youtube.com/watch?v=BwfjneL67ZU",
            "quality_tag": "1080p", "ydl_opts": {"format": "bestvideo[height<=1080]+bestaudio/best"} # This one will now be correctly ignored
        },
        {
            "video_id": "BwfjneL67ZU", "url": "https://www.youtube.com/watch?v=BwfjneL67ZU",
            "quality_tag": "720p", "ydl_opts": {"format": "bestvideo[height<=720]+bestaudio/best"} # This will now be added
        },
        {
            "video_id": "YDDjAE13oKw", "url": "https://www.youtube.com/watch?v=YDDjAE13oKw",
            "quality_tag": "480p", "ydl_opts": {"format": "bestvideo[height<=480]+bestaudio/best"}
        },
        {
            "video_id": "YDDjAE13oKw", "url": "https://www.youtube.com/watch?v=YDDjAE13oKw",
            "quality_tag": "medium", "ydl_opts": {"format": "bestaudio[abr<128]"} # This will also be added
        }
    ]

    for i in tasks:
        download_manager.add_download(
            video_id=i["video_id"],
            url=i["url"],
            quality_tag=i["quality_tag"],
            ydl_opts=i["ydl_opts"]
        )
    
    # Let the manager run until all tasks are complete
    await download_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
