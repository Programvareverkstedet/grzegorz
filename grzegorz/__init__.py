import asyncio
from . import playlistmanage

async def entry():
    await asyncio.wait([
        playlistmanage.metadatafetch_loop(),
    ])

def main():
    asyncio.get_event_loop().run_until_complete(
        entry()
    )

if __name__ == '__main__':
    main()
