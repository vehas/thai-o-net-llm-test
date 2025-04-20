from pickle import EXT1
#!/usr/bin/env python3
"""
Script to prepare database: decompress snapshot.br, convert JSONL to Parquet and DuckDB, and fetch first rows from Huggingface.
"""
import brotli
import duckdb
import json
import requests
import re
import pandas as pd
from pathlib import Path

# Base and external directories
BASE_DIR = Path(__file__).parent
EXTERNAL_DIR = BASE_DIR / "external"
EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)

def expand():
    brotli_file = EXTERNAL_DIR / "snapshot.jsonl.br"
    output_file = EXTERNAL_DIR / "snapshot.jsonl"
    print("Reading compressed snapshot file...")
    try:
        compressed_data = brotli_file.read_bytes()
        decompressed_data = brotli.decompress(compressed_data)
        output_file.write_bytes(decompressed_data)
        print("Successfully extracted snapshot.jsonl.br to snapshot.jsonl")
    except Exception as e:
        print("Error extracting snapshot file:", e)
        raise

def add_answer_jsonl_to_duckdb():
    input_path = EXTERNAL_DIR / "snapshot.jsonl"
    try:
        records = []
        with input_path.open('r') as f:
            for line in f:
                rec = json.loads(line)
                result = rec.get('result', {})
                usage = result.get('usage', {})
                parts = rec.get('_id', '').split(':')
                model_name = parts[0] if len(parts) > 0 else None
                test_name = parts[1] if len(parts) > 1 else None
                raw_test_set = parts[2] if len(parts) > 2 else None
                if raw_test_set:
                    p = Path(raw_test_set)
                    dataset = p.parent.as_posix()
                    stem = p.stem
                    ext = p.suffix
                    splits = stem.split('_')
                    if len(splits) >= 3:
                        exam_name, exam_level = splits[0], splits[1]
                        subject = '_'.join(splits[2:])
                        test_set = f"{dataset}/{exam_name}_{exam_level}_{subject}{ext}"
                    else:
                        exam_name = exam_level = subject = None
                        test_set = raw_test_set
                else:
                    exam_name = exam_level = subject = None
                    test_set = None
                test_number = int(parts[-1]) if parts and parts[-1].isdigit() else None
                match = re.search(r'"correct_answer_key"\s*:\s*"([^\"]+)"', result.get('text', ''))
                correct_key = match.group(1) if match else None
                records.append({
                    '_id': rec.get('_id'),
                    'model_name': model_name,
                    'test_name': test_name,
                    'test_set': test_set,
                    'exam_name': exam_name,
                    'exam_level': exam_level,
                    'subject': subject,
                    'test_number': test_number,
                    'attempts': rec.get('attempts'),
                    'state': rec.get('state'),
                    'lease_expires_at': rec.get('leaseExpiresAt'),
                    'updated_at': rec.get('updatedAt'),
                    'input_messages': result.get('inputMessages'),
                    'temperature': result.get('temperature'),
                    'finish_reason': result.get('finishReason'),
                    'reasoning_details': result.get('reasoningDetails'),
                    'sources': result.get('sources'),
                    'text': result.get('text'),
                    'time': result.get('time'),
                    'prompt_tokens': usage.get('promptTokens'),
                    'completion_tokens': usage.get('completionTokens'),
                    'total_tokens': usage.get('totalTokens'),
                    'warnings': result.get('warnings'),
                    'correct_answer_key': correct_key,
                })
        df = pd.DataFrame.from_records(records)

        print("Saving to a permanent DuckDB file...")
        db_file = EXTERNAL_DIR / "snapshot.duckdb"
        # Remove old DB file if present to avoid lock conflicts
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception as e:
                print(f"Warning: cannot remove existing DB file {db_file}: {e}")
        con = duckdb.connect(database=str(db_file))
        # Add question_txt to DataFrame before registering with DuckDB
        df['question_txt'] = df['input_messages'].apply(
            lambda msgs: msgs[2]['content'] if isinstance(msgs, list) and len(msgs) > 2 and isinstance(msgs[2], dict) and 'content' in msgs[2] else None
        )
        con.register('df', df)
        con.execute("CREATE TABLE IF NOT EXISTS answer_snapshot AS SELECT * FROM df")
        print(f"inserted {len(df)} rows into answer_snapshot table")
        con.close()
        print(f"✅ Database saved to {db_file}")
    except Exception as e:
        print("Error processing data:", e)
        raise

def add_question_jsonl_to_duckdb():
    """
    Reads all questions from onet_test.jsonl, tgat_test.jsonl, tpat1_test.jsonl;
    Adds a subject_index (per subject, starting from 0 in order of appearance);
    Inserts all questions into a DuckDB table named 'question'.
    """
    import duckdb
    import json
    import pandas as pd
    from pathlib import Path

    DATA_FILES = [
        EXTERNAL_DIR / "openthaigpt_eval/onet_m6_english.jsonl",
        EXTERNAL_DIR / "openthaigpt_eval/onet_m6_math.jsonl",
        EXTERNAL_DIR / "openthaigpt_eval/onet_m6_science.jsonl",
        EXTERNAL_DIR / "openthaigpt_eval/onet_m6_social.jsonl",
        EXTERNAL_DIR / "openthaigpt_eval/onet_m6_thai.jsonl",

        EXTERNAL_DIR / "thai_exam/data/tgat/tgat_test.jsonl",
        EXTERNAL_DIR / "thai_exam/data/tpat1/tpat1_test.jsonl",
    ]
    questions = []
    for file in DATA_FILES:
        if not file.exists():
            print(f"Warning: {file} does not exist.")
            continue
        # Extract exam_name from file name (e.g., tpat1 from tpat1_test.jsonl)
        exam_name = file.stem.split('_')[0] if '_' in file.stem else file.stem
        with file.open('r', encoding='utf-8') as f:
            for line in f:
                question = json.loads(line)
                question['exam_name'] = exam_name
                questions.append(question)
    # Sort questions by subject and then by 'no' (convert to float for sorting)
    def _no_as_float(q):
        try:
            return float(q.get('no', 0))
        except Exception:
            return 0
    questions.sort(key=lambda q: (q.get('subject', ''), _no_as_float(q)))
    # Assign subject_index per subject
    from collections import defaultdict
    subject_indices = defaultdict(int)
    for q in questions:
        subj = q.get('subject', 'unknown')
        q['subject_index'] = subject_indices[subj]
        subject_indices[subj] += 1
    # Save to DuckDB
    db_file = EXTERNAL_DIR / "snapshot.duckdb"
    con = duckdb.connect(database=str(db_file))
    df = pd.DataFrame(questions)
    # Create table with appropriate schema
    con.execute("""
        CREATE TABLE IF NOT EXISTS question AS SELECT * FROM df
    """)
    # If table already exists, insert new data (replace all for idempotency)
    con.execute("DELETE FROM question")
    con.register('df', df)
    con.execute("INSERT INTO question SELECT * FROM df")
    con.close()
    print(f"✅ Inserted {len(df)} questions into DuckDB table 'question'.")

def add_model_price_icon_to_duckdb():
    """
    Reads model_price_icon.csv and inserts its contents into a DuckDB table named 'model_price_icon'.
    """
    import duckdb
    import pandas as pd
    from pathlib import Path

    BASE_DIR = Path(__file__).parent
    csv_path = BASE_DIR / "model_price_icon.csv"
    db_file = BASE_DIR / "external" / "snapshot.duckdb"
    if not csv_path.exists():
        print(f"❌ {csv_path} does not exist.")
        return
    if not db_file.exists():
        print(f"❌ {db_file} does not exist. Run the other DB prep steps first.")
        return
    df = pd.read_csv(csv_path)
    con = duckdb.connect(database=str(db_file))
    # Create table with appropriate schema (matching CSV columns)
    con.execute("""
        CREATE TABLE IF NOT EXISTS model_price_icon (
            model_name VARCHAR,
            input_token_price DOUBLE,
            output_token_price DOUBLE,
            icon VARCHAR
        )
    """)
    # Replace all data for idempotency
    con.execute("DELETE FROM model_price_icon")
    con.register('df', df)
    con.execute("INSERT INTO model_price_icon SELECT * FROM df")
    con.close()
    print(f"✅ Inserted {len(df)} rows into DuckDB table 'model_price_icon'.")

def main():
    expand()
    add_answer_jsonl_to_duckdb()
    add_question_jsonl_to_duckdb()
    add_model_price_icon_to_duckdb()
    # fetch_first_rows()

if __name__ == "__main__":
    main()
