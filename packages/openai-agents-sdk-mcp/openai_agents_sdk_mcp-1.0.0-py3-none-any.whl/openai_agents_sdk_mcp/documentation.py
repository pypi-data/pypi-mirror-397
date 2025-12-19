#!/usr/bin/env python3
"""
Script to parse the OpenAI Agents SDK documentation webpage
and extract the index/navigation links into a structured map.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Constants
DOCS_INDEX_FILE = "docs_index.json"
INDEX_MAX_AGE_DAYS = 1


def fetch_documentation_index(url: str = "https://openai.github.io/openai-agents-python/") -> Dict[str, str]:
    """
    Fetch and parse the OpenAI Agents SDK documentation page.
    
    Returns a dictionary mapping topic/feature names to their URLs.
    """
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Dictionary to store the documentation map
    doc_map = {}
    
    # Find navigation links - typically in nav elements or sidebar
    # This will look for all links in the navigation/menu structure
    nav_elements = soup.find_all(['nav', 'aside', 'div'], class_=lambda x: x and ('nav' in x.lower() or 'menu' in x.lower() or 'sidebar' in x.lower() or 'toc' in x.lower()))
    
    # If no specific nav elements found, fall back to all links
    if not nav_elements:
        nav_elements = [soup]
    
    for nav in nav_elements:
        links = nav.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text(strip=True)
            
            # Skip empty links or anchor-only links
            if not text or not href:
                continue
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = f"https://openai.github.io{href}"
            elif href.startswith('#'):
                full_url = f"{url}{href}"
            elif not href.startswith('http'):
                full_url = f"{url.rstrip('/')}/{href.lstrip('/')}"
            else:
                full_url = href
            
            # Skip external links (GitHub, language switches, etc.) unless they're docs
            if 'github.com' in full_url and 'openai-agents-python' not in full_url:
                continue
            if '/openai-agents-python/' not in full_url:
                continue
                
            # Add to map, avoiding duplicates by preferring the first occurrence
            if text not in doc_map:
                doc_map[text] = full_url
    
    return doc_map


def clean_and_organize_map(doc_map: Dict[str, str]) -> Dict[str, str]:
    """
    Clean and organize the documentation map by removing duplicates
    and organizing by category.
    """
    # Remove common navigation items that aren't documentation pages
    exclude_terms = {'OpenAI Agents SDK', 'Go to repository', 'Skip to content', 
                     'English', '日本語', '한국어', '简体中文'}
    
    cleaned_map = {k: v for k, v in doc_map.items() if k not in exclude_terms}
    
    # Sort by key for better readability
    return dict(sorted(cleaned_map.items()))


def is_index_stale() -> bool:
    """
    Check if the docs_index.json file is missing or older than INDEX_MAX_AGE_DAYS.
    
    Returns:
        True if the index needs to be refreshed, False otherwise
    """
    index_path = Path(DOCS_INDEX_FILE)
    
    # Check if file exists
    if not index_path.exists():
        print(f"Index file '{DOCS_INDEX_FILE}' not found.")
        return True
    
    # Check file age
    file_mtime = datetime.fromtimestamp(index_path.stat().st_mtime)
    age = datetime.now() - file_mtime
    
    if age > timedelta(days=INDEX_MAX_AGE_DAYS):
        print(f"Index file is {age.days} days old (max age: {INDEX_MAX_AGE_DAYS} days).")
        return True
    
    return False


def verify_links(doc_map: Dict[str, str]) -> Tuple[bool, list]:
    """
    Verify that links in the documentation map are working.
    
    Args:
        doc_map: Dictionary of topic names to URLs
        
    Returns:
        Tuple of (all_valid, broken_links) where broken_links is a list of (topic, url) tuples
    """
    broken_links = []
    
    print("Verifying documentation links...")
    for topic, url in doc_map.items():
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code >= 400:
                broken_links.append((topic, url))
                print(f"  ✗ Broken: {topic} ({url}) - Status: {response.status_code}")
        except Exception as e:
            broken_links.append((topic, url))
            print(f"  ✗ Error checking {topic} ({url}): {e}")
    
    if not broken_links:
        print("  ✓ All links are valid")
    
    return len(broken_links) == 0, broken_links


def load_or_refresh_index(force_refresh: bool = False) -> Dict[str, str]:
    """
    Load the documentation index from file, or refresh it if needed.
    
    Args:
        force_refresh: If True, always refresh the index regardless of age
        
    Returns:
        Dictionary mapping topic names to URLs
    """
    should_refresh = force_refresh or is_index_stale()
    
    # Try to load existing index first
    doc_map = None
    if not force_refresh and Path(DOCS_INDEX_FILE).exists():
        try:
            with open(DOCS_INDEX_FILE, 'r', encoding='utf-8') as f:
                doc_map = json.load(f)
            print(f"Loaded existing index with {len(doc_map)} topics.")
            
            # Verify links if index is not stale
            if not should_refresh:
                all_valid, broken_links = verify_links(doc_map)
                if not all_valid:
                    print(f"Found {len(broken_links)} broken links. Refreshing index...")
                    should_refresh = True
                    
        except Exception as e:
            print(f"Error loading existing index: {e}")
            should_refresh = True
    
    # Refresh if needed
    if should_refresh:
        print("Fetching fresh documentation index...")
        doc_map = fetch_documentation_index()
        doc_map = clean_and_organize_map(doc_map)
        
        # Save to file
        with open(DOCS_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(doc_map, f, indent=2, ensure_ascii=False)
        
        print(f"Index refreshed with {len(doc_map)} topics and saved to '{DOCS_INDEX_FILE}'.")
    
    return doc_map


def get_documentation_for_feature(feature_name: str, doc_map: Optional[Dict[str, str]] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Use LLM to find the closest matching documentation link for a given feature name.
    
    Args:
        feature_name: The name of the feature/module to find documentation for
        doc_map: Optional pre-loaded documentation map. If None, will load/refresh from file
    
    Returns:
        A tuple of (matched_topic, url) if found, otherwise (None, None)
    """
    # Load or refresh the documentation map if not provided
    if doc_map is None:
        doc_map = load_or_refresh_index()
    
    if not doc_map:
        print("Error: Documentation map is empty.")
        return None, None
    
    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        return None, None
    
    client = OpenAI(api_key=api_key)
    
    # Create a list of available topics
    available_topics = list(doc_map.keys())
    
    # Use LLM to find the best match
    prompt = f"""Given a user's query for a feature/module name and a list of available documentation topics, 
identify the MOST relevant topic that best matches the user's query.

User's query: "{feature_name}"

Available topics:
{json.dumps(available_topics, indent=2)}

Respond with ONLY the exact topic name from the list above that best matches the query.
If no good match exists, respond with "NO_MATCH".
Do not include any explanation or additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that matches user queries to documentation topics. Respond only with the exact topic name or 'NO_MATCH'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        
        matched_topic = response.choices[0].message.content.strip()
        
        # Remove any quotes that might be added
        matched_topic = matched_topic.strip('"').strip("'")
        
        if matched_topic == "NO_MATCH":
            return None, None
        
        # Verify the matched topic exists in the map
        if matched_topic in doc_map:
            return matched_topic, doc_map[matched_topic]
        else:
            # If exact match not found, do a case-insensitive search
            for topic in doc_map:
                if topic.lower() == matched_topic.lower():
                    return topic, doc_map[topic]
            
            print(f"Warning: LLM returned '{matched_topic}' but it's not in the documentation map.")
            return None, None
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None, None


def fetch_documentation_content(url: str) -> str:
    """
    Fetch the content of a documentation page.
    
    Args:
        url: The URL of the documentation page
        
    Returns:
        The text content of the page
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        print(f"Error fetching documentation content: {e}")
        return ""


def main():
    """Main function to fetch and display the documentation index."""
    print("Fetching OpenAI Agents SDK documentation index...")
    
    try:
        # Use the load_or_refresh_index function which handles staleness checking
        cleaned_map = load_or_refresh_index(force_refresh=True)
        
        print(f"\nFound {len(cleaned_map)} documentation topics/features:\n")
        print("=" * 80)
        
        # Display the map
        for topic, url in cleaned_map.items():
            print(f"{topic}")
            print(f"  → {url}")
            print()
        
        print("=" * 80)
        print(f"\nDocumentation index saved to: {DOCS_INDEX_FILE}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def cli():
    """CLI entry point for the documentation tool."""
    import sys
    
    # If a feature name is provided as command-line argument, search for it
    if len(sys.argv) > 1:
        feature_query = " ".join(sys.argv[1:])
        print(f"Searching for documentation on: {feature_query}\n")
        
        topic, url = get_documentation_for_feature(feature_query)
        
        if topic and url:
            print(f"✓ Found matching topic: {topic}")
            print(f"  URL: {url}\n")
            
            # Optionally fetch and display a preview of the content
            print("Fetching documentation content...\n")
            content = fetch_documentation_content(url)
            if content:
                # Display first 1000 characters as preview
                preview = content[:1000]
                print("=" * 80)
                print(preview)
                if len(content) > 1000:
                    print("\n... (content truncated)")
                print("=" * 80)
        else:
            print(f"✗ No matching documentation found for '{feature_query}'")
            print("\nTry one of these available topics:")
            # Show a few suggestions
            doc_map = load_or_refresh_index()
            for i, topic in enumerate(list(doc_map.keys())[:10]):
                print(f"  - {topic}")
            if len(doc_map) > 10:
                print(f"  ... and {len(doc_map) - 10} more")
    else:
        # Run the normal index parsing
        sys.exit(main())


if __name__ == "__main__":
    cli()
