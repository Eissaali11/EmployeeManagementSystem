import traceback
import os
import sys

def check_file(filepath):
    """فحص الملف لوجود استدعاء pdfkit"""
    if not os.path.isfile(filepath) or not filepath.endswith('.py'):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'pdfkit' in content:
                return True
    except Exception as e:
        print(f"Error reading {filepath}: {str(e)}")
    
    return False

try:
    # البحث في جميع الملفات لاستدعاء pdfkit
    print("Searching for files that mention pdfkit...")
    found_files = []
    
    # جميع المسارات
    directories = [
        '/home/runner/workspace'
    ]
    
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if check_file(filepath):
                    found_files.append(filepath)
    
    print("\nFiles that mention pdfkit:")
    if found_files:
        for file in found_files:
            print(f"- {file}")
            
            # عرض محتوى الملف الذي يحتوي على pdfkit
            print("\nContent snippets containing 'pdfkit':")
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if 'pdfkit' in line:
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        print(f"\nLine {i+1}:")
                        for j in range(start, end):
                            if j == i:
                                print(f">>> {lines[j].strip()}")
                            else:
                                print(f"    {lines[j].strip()}")
    else:
        print("No files found that mention pdfkit.")
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc()