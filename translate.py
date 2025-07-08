import csv
import os
from pathlib import Path
from model_utils import get_model_response

SOURCE_DIR = "prompts_en/questions"
TARGET_DIR = "prompts_es/questions"

TRANSLATION_PROMPT = "Please translate the following from english to spanish: {to_translate}. Output only a single translation, and nothing else."


def translate_csv_files(source_dir=SOURCE_DIR, target_dir=TARGET_DIR, 
                       source_lang="english", target_lang="spanish"):
    """
    Translate all CSV files from source directory to target directory.
    """
    # Create target directory if it doesn't exist
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    
    # Get all CSV files in source directory
    source_path = Path(source_dir)
    csv_files = list(source_path.glob("*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {source_dir}")
        return
    
    for csv_file in csv_files:
        print(f"Processing: {csv_file.name}")
        
        # Read the source CSV
        with open(csv_file, 'r', encoding='utf-8', newline='') as source_file:
            reader = csv.reader(source_file)
            
            # Prepare the output file path
            output_path = Path(target_dir) / csv_file.name
            
            # Open the target CSV for writing
            with open(output_path, 'w', encoding='utf-8', newline='') as target_file:
                writer = csv.writer(target_file)
                
                # Process each row
                for row_num, row in enumerate(reader, 1):
                    if row_num == 1:
                        # First row is headers - write as-is without translation
                        writer.writerow(row)
                        continue
                    
                    translated_row = []
                    
                    # Translate each field in the row
                    for field_num, field_value in enumerate(row, 1):
                        if field_value.strip():  # Only translate non-empty fields
                            prompt = TRANSLATION_PROMPT.format(to_translate=field_value)
                            try:
                                response = get_model_response(prompt=prompt, model="anthropic/claude-sonnet-4")
                                translated_row.append(response)
                            except Exception as e:
                                print(f"Error translating row {row_num}, field {field_num}: {e}")
                                # Keep original value if translation fails
                                translated_row.append(field_value)
                        else:
                            # Keep empty fields as is
                            translated_row.append(field_value)
                    
                    # Write the translated row
                    writer.writerow(translated_row)
        
        print(f"Completed: {csv_file.name} -> {output_path}")
    
    print(f"\nTranslation complete. {len(csv_files)} files processed.")

if __name__ == "__main__":
    translate_csv_files()