#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
# ]
# ///
"""
Vocabulary.com Audio Downloader

Downloads pronunciation audio files from vocabulary.com for given words or phrases.
"""

import re
import sys
import argparse
import requests
from pathlib import Path
from urllib.parse import quote

DEFAULT_OUTPUT_DIR = str(Path.home() / "Library/Application Support/Anki2/User 1/collection.media")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive',
}


def get_audio_token(query):
    """
    Fetch the audio token from vocabulary.com for the given query.
    
    Args:
        query (str): The word or phrase to look up
        
    Returns:
        str: The audio token (e.g., 'C/BNUT8S5S2HDK') or None if not found
    """
    # URL encode the query for the request
    encoded_query = quote(query.strip())
    url = f"https://www.vocabulary.com/dictionary/{encoded_query}"
    
    try:
        response = requests.get(url, timeout=10, headers=HEADERS)
        response.raise_for_status()
        
        # Use regex to find the audio token pattern
        # Looking for data-audio="X/XXXXXXXX" pattern
        pattern = r'"([A-Z]/[A-Z0-9]+)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        else:
            print(f"No audio token found for '{query}'")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page for '{query}': {e}")
        return None


def download_audio(token, query, output_dir="."):
    """
    Download the audio file using the token.
    
    Args:
        token (str): The audio token (e.g., 'C/BNUT8S5S2HDK')
        query (str): The original query for naming the file
        output_dir (str): Directory to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    audio_url = f"https://audio.vocabulary.com/1.0/us/{token}.mp3"
    
    # Clean the query for filename (remove special characters)
    safe_filename = re.sub(r'[^\w\s-]', '', query.strip())
    safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
    filename = f"{safe_filename}.mp3"
    
    output_path = Path(output_dir) / filename
    
    try:
        print(f"Downloading audio for '{query}'...")
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Successfully saved: {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download pronunciation audio from vocabulary.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vocab_audio.py Capricorn
  python vocab_audio.py "machine learning" -o ./audio_files
  python vocab_audio.py pronunciation --output-dir ~/Downloads
        """
    )
    
    parser.add_argument(
        'query',
        help='Word or phrase to download audio for'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default=DEFAULT_OUTPUT_DIR,
        help='Output directory for downloaded files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Get the audio token
    token = get_audio_token(args.query)
    if not token:
        sys.exit(1)
    
    print(f"Found audio token: {token}")
    
    # Download the audio file
    success = download_audio(token, args.query, args.output_dir)
    if not success:
        sys.exit(1)
    
    print("Done!")


if __name__ == "__main__":
    main()
