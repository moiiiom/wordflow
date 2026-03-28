#!/usr/bin/env python3
"""
Enrich words.csv with importance scores (1-5) and improved notes.
Runs once offline; output replaces data/words.csv.

Usage:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key
  python enrich_words.py
"""

import anthropic
import csv
import json
import re
import sys
import time
from io import StringIO

INPUT_CSV = "data/words.csv"
OUTPUT_CSV = "data/words.csv"
BATCH_SIZE = 10  # words per API call

SYSTEM_PROMPT = """You are an English vocabulary assistant. For each word/phrase provided, return a JSON array.
Each element must have:
- "word": the exact word/phrase as given
- "importance": integer 1-5 reflecting frequency and usefulness for a professional non-native English speaker
  (5=essential daily/work vocabulary, 1=rare or very niche)
- "notes": plain text notes in English/Chinese. Preserve existing notes if good. For missing notes, add:
  Chinese meaning, 1-2 example sentences or collocations, related word forms if relevant.
  Max 200 words. No HTML, no markdown.

Return ONLY a valid JSON array, no other text."""


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text)


def read_csv(path: str) -> list[dict]:
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Normalize: ensure Importance column exists
    for row in rows:
        if 'Importance' not in row:
            row['Importance'] = ''
    return rows


def write_csv(path: str, rows: list[dict]):
    fieldnames = ['Vocabulary', 'Notes', 'Importance']
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                'Vocabulary': row.get('Vocabulary', ''),
                'Notes': row.get('Notes', ''),
                'Importance': row.get('Importance', ''),
            })


def enrich_batch(client: anthropic.Anthropic, batch: list[dict]) -> list[dict]:
    """Send a batch of words to Claude and return enriched data. Falls back word-by-word on block."""
    def call_api(subset):
        prompt = json.dumps([
            {"word": r['Vocabulary'], "existing_notes": strip_html(r.get('Notes', '') or '')}
            for r in subset
        ], ensure_ascii=False)
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON array found: {text[:200]}")
        return json.loads(match.group())

    try:
        return call_api(batch)
    except Exception as e:
        err = str(e).lower()
        if not any(k in err for k in ('block', 'harmful', 'policy', 'safety')):
            raise
        # Batch blocked — fall back to individual calls
        print(f"(batch blocked, retrying word-by-word)", end=' ', flush=True)
        results = []
        for row in batch:
            try:
                items = call_api([row])
                results.extend(items)
            except Exception:
                results.append({
                    'word': row['Vocabulary'],
                    'importance': 1,
                    'notes': strip_html(row.get('Notes', '') or '')
                })
            time.sleep(0.5)
        return results


def main():
    client = anthropic.Anthropic()
    rows = read_csv(INPUT_CSV)
    total = len(rows)
    print(f"Loaded {total} words from {INPUT_CSV}")

    # Build lookup map for updating rows
    row_by_word = {r['Vocabulary']: r for r in rows}

    # Process in batches
    for start in range(0, total, BATCH_SIZE):
        # Skip already-enriched batches
        batch = rows[start:start + BATCH_SIZE]
        already_done = all(r.get('Importance', '').strip() for r in batch)
        if already_done:
            print(f"Skipping {start+1}-{min(start+BATCH_SIZE,total)}/{total} (already enriched)")
            continue

        end = min(start + BATCH_SIZE, total)
        print(f"Processing {start+1}-{end}/{total}...", end=' ', flush=True)

        try:
            enriched = enrich_batch(client, batch)
            for item in enriched:
                word = item.get('word', '')
                if word in row_by_word:
                    row_by_word[word]['Notes'] = item.get('notes', row_by_word[word].get('Notes', ''))
                    row_by_word[word]['Importance'] = str(item.get('importance', ''))
            print(f"OK ({len(enriched)} enriched)")
        except Exception as e:
            print(f"ERROR: {e}")

        # Save after every batch so progress is not lost
        write_csv(OUTPUT_CSV, rows)
        time.sleep(1)


if __name__ == '__main__':
    main()
