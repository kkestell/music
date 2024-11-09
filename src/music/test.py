from aioslsk.client import SoulSeekClient
from aioslsk.settings import (
    Settings,
    CredentialsSettings,
    NetworkSettings,
    ListeningSettings,
    ServerSettings,
    PeerSettings,
    UpnpSettings,
    NetworkLimitSettings,
    SharesSettings
)
from aioslsk.transfer.state import (
    QueuedState,
    InitializingState,
    DownloadingState,
    CompleteState,
    FailedState,
    AbortedState
)
import asyncio
import os


async def try_download(client, result, shared_item):
    """Attempt to download a file, return True if successful, False if queued/failed"""
    print(f"\nTrying to download from {result.username}: {shared_item.filename}")

    download = await client.transfers.download(
        username=result.username,
        filename=shared_item.filename
    )

    last_progress = -1
    last_state = None
    start_time = asyncio.get_event_loop().time()
    queued_start_time = None  # Time when download entered QueuedState

    while True:
        current_state_name = download.state.__class__.__name__
        if current_state_name != last_state:
            print(f"Download state changed to: {current_state_name}")
            last_state = current_state_name

            # Handle state changes
            if isinstance(download.state, QueuedState):
                # Record the time when we entered QueuedState
                queued_start_time = asyncio.get_event_loop().time()

            elif isinstance(download.state, CompleteState):
                print(f"Download completed: {download.local_path}")
                return True

            elif isinstance(download.state, (FailedState, AbortedState)):
                print("Download failed or aborted")
                return False

            elif isinstance(download.state, (InitializingState, DownloadingState)):
                # Reset queued_start_time if we leave QueuedState
                queued_start_time = None

        # Check if we've been in QueuedState for too long
        if isinstance(download.state, QueuedState) and queued_start_time is not None:
            queued_duration = asyncio.get_event_loop().time() - queued_start_time
            if queued_duration > 5:
                print("Download has been queued for more than 5 seconds, cancelling and trying next result")
                try:
                    await client.transfers.abort(download)
                except Exception as e:
                    print(f"Error aborting download: {e}")
                return False

        # Update progress if available
        if download.filesize and isinstance(download.state, DownloadingState):
            progress = int((download.bytes_transfered / download.filesize) * 100)
            if progress != last_progress:
                print(f"Progress: {progress}%")
                last_progress = progress

        # Check overall timeout (e.g., 30 seconds) for initializing or downloading states
        current_time = asyncio.get_event_loop().time()
        if (current_time - start_time > 30 and
                isinstance(download.state, (InitializingState, DownloadingState))):
            print("Download attempt timed out")
            try:
                await client.transfers.abort(download)
            except Exception as e:
                print(f"Error aborting download: {e}")
            return False

        await asyncio.sleep(0.1)


async def search_and_download():
    download_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_dir, exist_ok=True)

    settings = Settings(
        credentials=CredentialsSettings(
            username='jovianshitbag',
            password='jovianshitbag'
        ),
        network=NetworkSettings(
            listening=ListeningSettings(
                port=50000,
                obfuscated_port=50001
            ),
            server=ServerSettings(
                hostname='server.slsknet.org',
                port=2416
            ),
            peer=PeerSettings(
                obfuscate=False
            ),
            upnp=UpnpSettings(
                enabled=False
            ),
            limits=NetworkLimitSettings(
                upload_speed_kbps=0,
                download_speed_kbps=0
            )
        ),
        shares=SharesSettings(
            download=download_dir
        )
    )

    client = SoulSeekClient(settings=settings)

    try:
        print("Initializing...")
        await client.shares.scan()

        print("Starting client...")
        await client.start()

        print("Logging in...")
        await client.login()

        print("Successfully connected!")

        print("\nSearching for files...")
        search_request = await client.searches.search("cover.jpg")

        await asyncio.sleep(5)

        if search_request.results:
            print(f"\nFound {len(search_request.results)} results")

            # Try each result until we get a successful download
            for i, result in enumerate(search_request.results):
                print(f"\nTrying result {i + 1}/{len(search_request.results)}:")
                print(f"Username: {result.username}")

                if result.shared_items:
                    try:
                        success = await try_download(client, result, result.shared_items[0])
                        if success:
                            print("Successfully downloaded file!")
                            break
                        else:
                            print("Moving to next result...")
                            continue
                    except Exception as e:
                        print(f"Error during download attempt: {e}")
                        print("Moving to next result...")
                        continue

        else:
            print("No results found")

    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nStopping client...")
        await client.stop()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(search_and_download())