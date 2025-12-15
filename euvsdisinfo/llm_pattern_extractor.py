#!/usr/bin/env python3
"""
LLM-Powered Propaganda Pattern Extractor

Sends original source texts and analyses to a local LLM (via LM Studio) 
to automatically identify and extract propaganda patterns, then updates
the propaganda_patterns_data.json file.
"""

import json
import requests
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

class LLMPropagandaExtractor:
    """Extract propaganda patterns using local LLM analysis."""
    
    def __init__(self, 
                 lm_studio_url: str = "http://localhost:1234/v1/chat/completions",
                 model_name: str = "local-model",
                 data_file: str = "propaganda_patterns_data.json"):
        self.lm_studio_url = lm_studio_url
        self.model_name = model_name
        self.data_file = Path(data_file)
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """Load existing propaganda patterns data or create new structure."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Validate structure and repair if needed
                if not isinstance(data, dict):
                    print(f"Warning: Invalid JSON structure in {self.data_file}, creating new structure")
                    return self._create_new_structure()
                
                # Ensure required keys exist
                if "entries" not in data:
                    print("Warning: Missing 'entries' key, adding it")
                    data["entries"] = []
                
                if "metadata" not in data:
                    print("Warning: Missing 'metadata' key, adding it")
                    data["metadata"] = {
                        "created": datetime.datetime.now().isoformat(),
                        "extraction_method": "LLM-powered"
                    }
                
                # Ensure entries is a list
                if not isinstance(data["entries"], list):
                    print("Warning: 'entries' is not a list, converting")
                    data["entries"] = []
                
                return data
                
            except json.JSONDecodeError as e:
                print(f"Error: Corrupted JSON in {self.data_file}: {e}")
                print("Creating backup and starting fresh...")
                
                # Create backup of corrupted file
                backup_path = self.data_file.with_suffix('.corrupted.bak')
                import shutil
                shutil.copy2(self.data_file, backup_path)
                print(f"Corrupted file backed up to: {backup_path}")
                
                return self._create_new_structure()
                
            except Exception as e:
                print(f"Unexpected error loading {self.data_file}: {e}")
                return self._create_new_structure()
        else:
            return self._create_new_structure()
    
    def _create_new_structure(self) -> Dict:
        """Create a new, properly structured data dictionary."""
        return {
            "metadata": {
                "created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "total_entries": 0,
                "extraction_method": "LLM-powered"
            },
            "entries": []
        }
    
    def save_data(self):
        """Save updated data back to JSON file with robust error handling."""
        self.data["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
        self.data["metadata"]["total_entries"] = len(self.data["entries"])
        
        try:
            # Clean data before saving to prevent JSON issues
            cleaned_data = self._clean_json_data(self.data)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Updated {self.data_file} with {len(self.data['entries'])} entries")
            
        except (TypeError, ValueError, UnicodeEncodeError) as e:
            print(f"⚠️  JSON serialization error: {e}")
            print("Creating backup and attempting to save sanitized version...")
            
            # Create backup of current in-memory data
            backup_path = self.data_file.with_suffix('.error_backup.json')
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    # Try to save as much as possible, even if malformed
                    f.write(str(self.data))
                print(f"Backup saved to: {backup_path}")
            except:
                print("Could not create backup")
            
            # Sanitize and save
            sanitized_data = self._sanitize_json_data(self.data)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(sanitized_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved sanitized version with {len(sanitized_data['entries'])} entries")
    
    def _clean_json_data(self, data):
        """Recursively clean data to ensure JSON compatibility."""
        if isinstance(data, dict):
            return {key: self._clean_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_json_data(item) for item in data]
        elif isinstance(data, str):
            # Remove problematic characters and fix common issues
            cleaned = data.replace('\x00', '')  # Remove null bytes
            cleaned = cleaned.replace('"', '\\"')  # Escape quotes properly
            cleaned = cleaned.replace('\b', '\\b')  # Escape backspace
            cleaned = cleaned.replace('\f', '\\f')  # Escape form feed
            cleaned = cleaned.replace('\t', '\\t')  # Escape tabs
            return cleaned
        else:
            return data
    
    def _sanitize_json_data(self, data):
        """More aggressive sanitization for problematic data."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                try:
                    sanitized[key] = self._sanitize_json_data(value)
                except:
                    sanitized[key] = "[SANITIZED: Could not serialize]"
            return sanitized
        elif isinstance(data, list):
            sanitized = []
            for item in data:
                try:
                    sanitized.append(self._sanitize_json_data(item))
                except:
                    sanitized.append("[SANITIZED: Could not serialize]")
            return sanitized
        elif isinstance(data, str):
            # Very aggressive cleaning
            try:
                # Remove all non-printable characters except common whitespace
                cleaned = ''.join(char for char in data if char.isprintable() or char in '\n\r\t ')
                # Escape quotes
                cleaned = cleaned.replace('"', '\\"')
                return cleaned
            except:
                return "[SANITIZED: String could not be cleaned]"
        else:
            try:
                json.dumps(data)  # Test if it's JSON serializable
                return data
            except:
                return str(data) if data is not None else None
    
    def create_analysis_prompt(self, original_text: str, human_analysis: str, 
                              source_language: str = "unknown") -> str:
        """Create the prompt for LLM analysis."""
        
        prompt = f"""You are an expert analyst of Russian propaganda and disinformation techniques. Analyze the provided text and human analysis to identify specific propaganda patterns.

ORIGINAL SOURCE TEXT ({source_language}):
```
{original_text}
```

HUMAN ANALYSIS:
```
{human_analysis}
```

Please identify and extract:

1. **TRANSLATION** (if original text is not in English):
   - Provide accurate English translation of the original text
   - If original is already in English, set to null

2. **PRIMARY NARRATIVE FRAMEWORK** (choose one):
   - ENCIRCLEMENT_NARRATIVE (Russia surrounded by enemies)
   - NATO_EXPANSION_EXISTENTIAL_THREAT (NATO as existential threat)  
   - WESTERN_HYPOCRISY_FRAMING (Western double standards)
   - BOTH_SIDES_FALSE_EQUIVALENCY (false moral equivalencies)
   - US_DECLINE_DEGENERACY (Western moral decline)
   - TRADITIONAL_VALUES_DEFENSE (Russia defending values)
   - MULTIPOLAR_WORLD_ORDER (challenging US hegemony)
   - ILLEGITIMATE_SECURITY_CONCERNS (framing aggression as defense)
   - HISTORICAL_GRIEVANCES (invoking past injustices)
   - OTHER (specify)

2. **PROPAGANDA TECHNIQUES** (list all that apply):
   - WHATABOUTISM (deflecting with "what about...")
   - UKRAINE_CORRUPTION_NARRATIVE (emphasizing Ukrainian corruption)
   - SANCTIONS_COUNTER_NARRATIVE (sanctions as harmful/ineffective)
   - False_Equivalency (both sides are the same)
   - Emotional_Manipulation (fear, anger, pride appeals)
   - Historical_Revisionism (distorting historical facts)
   - Victim_Blaming (portraying aggressor as victim)
   - Deflection (avoiding direct responses)
   - OTHER (specify)

3. **KEY PROPAGANDA PHRASES** (exact quotes from source):
   - List 5-10 specific phrases that carry propaganda messaging

4. **EMOTIONAL APPEALS** (what emotions are targeted):
   - Fear, Anger, Pride, Victimhood, Righteousness, etc.

5. **TARGET AUDIENCE**:
   - Who is this propaganda designed to influence?

6. **SCORING** (0-5 scale):
   - Russian_Alignment: How closely does this match Russian state messaging?
   - Sophistication: How well-crafted and subtle is the propaganda?
   - Effectiveness: How persuasive would this be to target audience?

Note: Provide accurate translation even if source language detection is uncertain.

Respond in this exact JSON format:
```json
{{
  "translation": "English translation of original text (null if already English)",
  "primary_narrative": "NARRATIVE_NAME",
  "techniques": ["TECHNIQUE1", "TECHNIQUE2"],
  "key_phrases": ["phrase1", "phrase2", "phrase3"],
  "emotional_appeals": ["emotion1", "emotion2"],
  "target_audience": "description of intended audience",
  "scores": {{
    "russian_alignment": 0,
    "sophistication": 0, 
    "effectiveness": 0
  }},
  "analysis_notes": "Brief explanation of why these patterns were identified"
}}
```"""
        
        return prompt
    
    def query_llm(self, prompt: str) -> Optional[Dict]:
        """Send prompt to LM Studio and get structured response."""
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert analyst of propaganda and disinformation. Always respond with valid JSON in the exact format requested."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.1,  # Low temperature for consistency
                "max_tokens": 2500,  # Increased for detailed analysis
                "stream": False
            }
            
            response = requests.post(
                self.lm_studio_url, 
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            # Extract content from response
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            
            # Extract JSON from response (handle multiple formats)
            print(f"DEBUG: Raw LLM response length: {len(content)} chars")
            
            # Try multiple JSON extraction patterns
            json_str = None
            
            # Pattern 1: JSON wrapped in ```json blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                print("DEBUG: Found JSON in code block")
            else:
                # Pattern 2: Look for JSON object boundaries
                brace_match = re.search(r'\{.*\}', content, re.DOTALL)
                if brace_match:
                    json_str = brace_match.group(0)
                    print("DEBUG: Found JSON object")
                else:
                    # Pattern 3: Use entire content
                    json_str = content
                    print("DEBUG: Using entire response as JSON")
            
            print(f"DEBUG: Extracted JSON length: {len(json_str)} chars")
            
            # Parse JSON response with enhanced error handling
            try:
                parsed_json = json.loads(json_str)
                print("DEBUG: JSON parsed successfully")
                # Validate and clean the parsed JSON
                return self._validate_and_clean_llm_response(parsed_json)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Error at position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
                print(f"Problematic JSON (first 300 chars): {json_str[:300]}...")
                print(f"Problematic JSON (last 300 chars): ...{json_str[-300:]}")
                
                # Try to fix common JSON issues
                try:
                    print("DEBUG: Attempting JSON repair...")
                    fixed_json = self._fix_json_string(json_str)
                    parsed_json = json.loads(fixed_json)
                    print("DEBUG: JSON repair successful")
                    return self._validate_and_clean_llm_response(parsed_json)
                except Exception as repair_error:
                    print(f"JSON repair failed: {repair_error}")
                    print(f"Raw response (first 500 chars): {content[:500]}...")
                    return None
                
        except requests.RequestException as e:
            print(f"Error communicating with LM Studio: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def _fix_json_string(self, json_str: str) -> str:
        """Attempt to fix common JSON formatting issues."""
        import re
        
        # Clean up basic formatting
        json_str = json_str.strip()
        
        # Remove extra quotes around the entire JSON
        if json_str.startswith('\"') and json_str.endswith('\"'):
            json_str = json_str[1:-1]
        
        # Check if JSON is truncated (doesn't end with })
        if not json_str.rstrip().endswith('}'):
            print("DEBUG: JSON appears truncated, attempting to close...")
            
            # Find the last complete field
            lines = json_str.split('\\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not line.endswith((',', '{', '}')):
                    # This might be an incomplete line
                    if ':' in line and not line.endswith(('\"', ']')):
                        # Try to close incomplete string or array
                        if '\"' in line and line.count('\"') % 2 == 1:
                            line += '\"'
                        elif '[' in line and ']' not in line:
                            line += ']'
                    
                cleaned_lines.append(line)
            
            json_str = '\\n'.join(cleaned_lines)
            
            # Ensure proper closing
            if not json_str.rstrip().endswith('}'):
                # Find last complete field and close properly
                brace_count = json_str.count('{') - json_str.count('}')
                json_str = json_str.rstrip()
                if json_str.endswith(','):
                    json_str = json_str[:-1]  # Remove trailing comma
                json_str += '}' * brace_count
        
        # Fix common quote escaping issues
        # Escape unescaped quotes in string values
        def fix_quotes_in_strings(match):
            key = match.group(1)
            content = match.group(2)
            # Escape quotes that aren't already escaped
            fixed_content = re.sub(r'(?<!\\\\)"', '\\\\"', content)
            return f'"{key}": "{fixed_content}"'
        
        # Apply to key-value pairs
        json_str = re.sub(r'"([^"]+)":\\s*"([^"]*(?:\\\\"[^"]*)*)"', fix_quotes_in_strings, json_str)
        
        return json_str
    
    def _validate_and_clean_llm_response(self, response: Dict) -> Dict:
        """Validate and clean LLM response to ensure it's safe for JSON storage."""
        cleaned_response = {}
        
        # Required fields with defaults
        required_fields = {
            "translation": None,
            "primary_narrative": "UNKNOWN",
            "techniques": [],
            "key_phrases": [],
            "emotional_appeals": [],
            "target_audience": "Unknown",
            "scores": {"russian_alignment": 0, "sophistication": 0, "effectiveness": 0},
            "analysis_notes": ""
        }
        
        for field, default in required_fields.items():
            if field in response:
                cleaned_value = self._clean_json_data(response[field])
                cleaned_response[field] = cleaned_value
            else:
                cleaned_response[field] = default
        
        # Ensure scores is properly structured
        if not isinstance(cleaned_response["scores"], dict):
            cleaned_response["scores"] = {"russian_alignment": 0, "sophistication": 0, "effectiveness": 0}
        
        # Ensure lists are actually lists
        for list_field in ["techniques", "key_phrases", "emotional_appeals"]:
            if not isinstance(cleaned_response[list_field], list):
                cleaned_response[list_field] = []
        
        return cleaned_response
    
    def process_article(self, 
                       original_text: str,
                       human_analysis: str,
                       title: str = "",
                       source_url: str = "",
                       source_language: str = "unknown") -> bool:
        """Process a single article through LLM analysis - CREATES EXACTLY ONE ENTRY."""
        
        print(f"🔍 Processing: {title[:50] if title else 'Untitled'}...")
        
        # Safety check - warn if this looks like a duplicate
        if self._looks_like_duplicate(original_text, title, source_url):
            print("⚠️  WARNING: This article appears similar to an existing entry!")
            proceed = input("Continue anyway? (y/N): ").strip().lower()
            if proceed != 'y':
                print("❌ Processing cancelled")
                return False
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt(original_text, human_analysis, source_language)
        
        # Get LLM analysis
        llm_result = self.query_llm(prompt)
        
        if not llm_result:
            print("✗ Failed to get valid LLM response")
            return False
        
        # DEBUG: Check current entry count before adding
        entries_before = len(self.data["entries"])
        print(f"📊 Entries before processing: {entries_before}")
        
        # Create entry for data file - THIS SHOULD CREATE ONLY ONE ENTRY
        entry = {
            "id": entries_before + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "title": title,
            "source_url": source_url,
            "source_language": source_language,
            "original_text": original_text,
            "human_analysis": human_analysis,
            "llm_analysis": llm_result  # ALL analysis including translation goes here
        }
        
        # Add to data - THIS IS THE ONLY PLACE AN ENTRY SHOULD BE ADDED
        self.data["entries"].append(entry)
        entries_after = len(self.data["entries"])
        
        print(f"✓ Created entry #{entry['id']}")
        print(f"📊 Entries after processing: {entries_after}")
        print(f"✓ Primary narrative: {llm_result.get('primary_narrative', 'None')}")
        print(f"✓ Techniques: {', '.join(llm_result.get('techniques', []))}")
        print(f"✓ Russian Alignment: {llm_result.get('scores', {}).get('russian_alignment', 0)}/5")
        
        # Verify translation is included
        if llm_result.get('translation'):
            print("✓ Translation included in analysis")
        else:
            print("⚠️  No translation found in LLM response")
        
        return True
    
    def _looks_like_duplicate(self, original_text: str, title: str, source_url: str) -> bool:
        """Check if article might be a duplicate (for warning purposes only)."""
        if not self.data["entries"]:
            return False
            
        for entry in self.data["entries"]:
            # Check URL match
            if source_url and entry.get("source_url") == source_url:
                return True
            
            # Check title match
            if title and entry.get("title") == title:
                return True
            
            # Check if first 100 chars of text are very similar
            if original_text and entry.get("original_text"):
                entry_start = entry["original_text"][:100].strip().lower()
                current_start = original_text[:100].strip().lower()
                if entry_start == current_start:
                    return True
        
        return False
    
    def _safe_input(self, prompt: str) -> str:
        """Safe input that clears buffers and handles issues."""
        import sys
        
        # Flush output first
        sys.stdout.flush()
        
        # Try to clear input buffer
        try:
            if sys.stdin.isatty():
                # Windows
                try:
                    import msvcrt
                    while msvcrt.kbhit():
                        msvcrt.getch()
                except ImportError:
                    # Unix-like systems
                    try:
                        import termios
                        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                    except:
                        pass
        except:
            pass
        
        # Get input with error handling
        try:
            result = input(prompt).strip()
            return result
        except (EOFError, KeyboardInterrupt):
            print("\\nExiting...")
            return "quit"
    
    def _clean_web_content(self, content: str) -> str:
        """Clean HTML and web formatting from pasted content."""
        if not content.strip():
            return ""
        
        import re
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up common HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&#8217;': "'",
            '&#8220;': '"',
            '&#8221;': '"',
            '&#8211;': '-',
            '&#8212;': '--'
        }
        
        for entity, replacement in html_entities.items():
            content = content.replace(entity, replacement)
        
        # Clean up excessive whitespace
        content = re.sub(r'\\n\\s*\\n\\s*\\n+', '\\n\\n', content)  # Max 2 newlines
        content = re.sub(r' +', ' ', content)  # Multiple spaces to single
        content = re.sub(r'\\t+', ' ', content)  # Tabs to spaces
        
        # Clean up lines
        lines = content.split('\\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.isspace():
                cleaned_lines.append(line)
        
        return '\\n'.join(cleaned_lines).strip()
    
    def process_batch(self, articles: List[Dict]) -> int:
        """Process multiple articles in batch."""
        successful = 0
        
        print(f"Processing {len(articles)} articles...")
        
        for i, article in enumerate(articles, 1):
            print(f"\\n[{i}/{len(articles)}] ", end="")
            
            if self.process_article(
                original_text=article.get("original_text", ""),
                human_analysis=article.get("human_analysis", ""),
                title=article.get("title", f"Article {i}"),
                source_url=article.get("source_url", ""),
                source_language=article.get("source_language", "unknown")
            ):
                successful += 1
        
        # Save all updates
        self.save_data()
        
        print(f"\\n✓ Successfully processed {successful}/{len(articles)} articles")
        return successful
    
    def interactive_mode(self):
        """Interactive mode for single article processing."""
        print("\\n" + "="*70)
        print("🔍 LLM-POWERED PROPAGANDA PATTERN EXTRACTOR")
        print("="*70)
        print("📝 This tool processes ONE article at a time and creates ONE database entry")
        print("🌐 Non-English articles will be translated automatically")
        print("="*70)
        
        while True:
            print(f"\\n📊 Current database: {len(self.data['entries'])} entries")
            print("\\n" + "─"*50)
            print("📰 NEW ARTICLE INPUT")
            print("─"*50)
            
            # Clear any residual input buffer
            import sys
            if sys.stdin.isatty():
                try:
                    import msvcrt
                    while msvcrt.kbhit():
                        msvcrt.getch()
                except ImportError:
                    # Unix-like system
                    import termios
                    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            
            title = self._safe_input("📰 Article Title (or 'quit' to exit): ")
            if title.lower() in ['quit', 'exit', 'q']:
                print("\\n👋 Goodbye!")
                break
            
            # Debug: Show what was actually entered
            print(f"DEBUG: Title received: '{title[:100]}...' (length: {len(title)})")
                
            source_url = self._safe_input("🔗 Source URL: ")
            print(f"DEBUG: URL received: '{source_url[:100]}...' (length: {len(source_url)})")
            
            source_language = self._safe_input("🌐 Source Language (e.g., polish, russian, english): ") or "unknown"
            print(f"DEBUG: Language received: '{source_language[:100]}...' (length: {len(source_language)})")
            
            print("\\n" + "─"*50)
            print("📄 PASTE ORIGINAL TEXT")
            print("─"*50)
            print("Paste the article content below.")
            print("When finished, press ENTER twice (two empty lines):")
            print()
            
            original_lines = []
            empty_count = 0
            while True:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                original_lines.append(line)
            
            original_text = "\\n".join(original_lines).strip()
            
            print("\\n" + "─"*50)
            print("🧠 HUMAN ANALYSIS (Optional)")
            print("─"*50)
            print("Paste analysis from website (HTML tags OK).")
            print("Press CTRL+D (Unix) or CTRL+Z+ENTER (Windows) when finished.")
            print("Or type 'END' on a line by itself to finish:")
            print()
            
            analysis_lines = []
            print("Paste your content (type END on empty line to finish):")
            
            while True:
                try:
                    line = input()
                    
                    # Check for end markers
                    if line.strip().upper() in ['END', 'DONE', 'FINISH']:
                        print("DEBUG: End marker detected")
                        break
                        
                    analysis_lines.append(line)
                    
                    # Give feedback every 5 lines to show it's working
                    if len(analysis_lines) % 5 == 0:
                        print(f"[{len(analysis_lines)} lines received...]", flush=True)
                        
                except EOFError:
                    print("\\nEOF detected - finishing input")
                    break
                except KeyboardInterrupt:
                    print("\\nSkipping human analysis...")
                    analysis_lines = []
                    break
            
            # Clean up the HTML/web content
            raw_analysis = "\\n".join(analysis_lines)
            human_analysis = self._clean_web_content(raw_analysis)
            
            print(f"DEBUG: Received {len(analysis_lines)} lines")
            print(f"DEBUG: Raw length: {len(raw_analysis)} chars")
            print(f"DEBUG: Cleaned length: {len(human_analysis)} chars")
            print(f"DEBUG: Preview: '{human_analysis[:100]}...'")
            
            if human_analysis:
                print(f"✓ Human analysis captured ({len(human_analysis)} chars)")
            else:
                print("ℹ️  No human analysis provided")
            
            # Show summary
            print("\\n" + "═"*50)
            print("📋 PROCESSING SUMMARY")
            print("═"*50)
            print(f"📰 Title: {title}")
            print(f"🔗 URL: {source_url or 'None'}")
            print(f"🌐 Language: {source_language}")
            print(f"📄 Text length: {len(original_text):,} characters")
            print(f"🧠 Human analysis: {'Yes' if human_analysis else 'None'}")
            
            print("\\n" + "="*50)
            confirm = self._safe_input("🤖 Process with LLM? (Y/n): ").lower()
            if confirm == 'n':
                print("❌ Skipping article...")
                continue
            
            print("\\n" + "🔄"*25)
            print("🤖 PROCESSING WITH LLM...")
            print("🔄"*25)
            
            # THIS IS THE CRITICAL CALL - SHOULD CREATE EXACTLY ONE ENTRY
            success = self.process_article(original_text, human_analysis, title, source_url, source_language)
            
            if success:
                print("\\n💾 Saving to database...")
                self.save_data()
                print("\\n" + "✅"*25)
                print("✅ PROCESSING COMPLETE!")
                print("✅"*25)
                print(f"📊 Total entries now: {len(self.data['entries'])}")
            else:
                print("\\n" + "❌"*25)
                print("❌ PROCESSING FAILED!")
                print("❌"*25)
                print("Article was not saved.")
            
            print("\\n" + "="*50)
            continue_choice = input("Process another article? (Y/n): ").strip().lower()
            if continue_choice == 'n':
                print("\\n👋 Session complete!")
                break
    
    def test_llm_connection(self) -> bool:
        """Test connection to LM Studio."""
        try:
            test_prompt = "Respond with exactly: {'status': 'ok'}"
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": test_prompt}],
                "temperature": 0,
                "max_tokens": 50
            }
            
            response = requests.post(
                self.lm_studio_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            print("✓ LM Studio connection successful")
            return True
            
        except Exception as e:
            print(f"✗ LM Studio connection failed: {e}")
            print("Make sure LM Studio is running on http://localhost:1234")
            return False

def main():
    """Main function with command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM-Powered Propaganda Pattern Extractor')
    parser.add_argument('--test-connection', action='store_true', help='Test LM Studio connection')
    parser.add_argument('--interactive', action='store_true', help='Interactive article entry mode')
    parser.add_argument('--lm-url', default='http://localhost:1234/v1/chat/completions', help='LM Studio URL')
    parser.add_argument('--model', default='local-model', help='Model name')
    parser.add_argument('--data-file', default='propaganda_patterns_data.json', help='Output data file')
    
    args = parser.parse_args()
    
    extractor = LLMPropagandaExtractor(
        lm_studio_url=args.lm_url,
        model_name=args.model,
        data_file=args.data_file
    )
    
    if args.test_connection:
        extractor.test_llm_connection()
    elif args.interactive:
        if extractor.test_llm_connection():
            extractor.interactive_mode()
    else:
        print("Use --interactive to start article processing or --test-connection to verify setup")
        print("Make sure LM Studio is running with a model loaded!")

if __name__ == "__main__":
    main()