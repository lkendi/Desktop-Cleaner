import os
import shutil
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

parent_dir = os.path.expanduser("~/Desktop")
files_dict = {
    "Documents": [".pdf", ".docx", ".doc", ".txt"],
    "Images": [".png", ".jpg", ".jpeg"],
    "Videos": [".mp4", ".gif", ".mkv"],
    "Audio": [".mp3", ".wav"],
    "Archives": [".zip", ".rar"],
    "Data": [".xls", ".csv", ".json", ".xml"],
    "Code": [".py", ".c", ".sql", ".js", ".html", ".css"]
}


def create_directory_if_not_exists(directory):
    """Create a new directory if it does not exist"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Creating {directory} directory...")
    except Exception as e:
        print(f"Error creating directory: {e}")


def move_file(source, destination):
    """Moves a file from the source to destination directory"""
    try:
        print(f"Moving {os.path.basename(source)} to {destination}")
        shutil.move(source, destination)
    except Exception as e:
        print(f"Error moving file: {e}")


def organize_desktop():
    """Organizes files in the desktop by grouping by
    different file extensions"""
    try:
        if os.path.exists(parent_dir):
            files_organized = 0
            for item in os.listdir(parent_dir):
                matched = False
                for dir_name, extensions in files_dict.items():
                    if any(item.lower().endswith(extension)
                           for extension in extensions):
                        dest_dir = os.path.join(parent_dir, dir_name)
                        create_directory_if_not_exists(dest_dir)
                        source_path = os.path.join(parent_dir, item)
                        dest_path = os.path.join(dest_dir, item)
                        move_file(source_path, dest_path)
                        files_organized += 1
                        matched = True
                        break

            if not matched:
                dest_dir = os.path.join(parent_dir, "Other")
                create_directory_if_not_exists(dest_dir)
                source_path = os.path.join(parent_dir, item)
                dest_path = os.path.join(dest_dir, item)
                move_file(source_path, dest_path)
                files_organized += 1

            if files_organized == 0:
                print("No files left to organize.")
            else:
                for dir_name in files_dict.keys():
                    sort_by_keyword(os.path.join(parent_dir, dir_name))
                print("Mission Successful!")

    except Exception as e:
        print(f"An error occurred during organization: {e}")


def extract_keywords(filename):
    """Tokenizes a filename and extracts keywords from the tokens"""
    try:
        base_filename, _ = os.path.splitext(filename)
        if '-' in base_filename:
            base_filename = str(base_filename).replace('-', ' ')
        tokens = word_tokenize(base_filename.lower())
        tagged_tokens = pos_tag(tokens)
        return [token for token, tag in tagged_tokens
                if tag.startswith('N') or tag.startswith('J')
                or tag.startswith('V')]
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []


def sort_by_keyword(directory):
    try:
        keyword_count = {}
        for root, _, files in os.walk(directory):
            for filename in files:
                keywords = extract_keywords(filename)
                for keyword in keywords:
                    if keyword not in keyword_count:
                        keyword_count[keyword] = []
                    keyword_count[keyword].append(os.path.join(root, filename))
                    break

        for keyword, files in keyword_count.items():
            if len(files) > 1:
                keyword_dir = os.path.join(directory, keyword.capitalize())
                create_directory_if_not_exists(keyword_dir)
                for file in files:
                    move_file(file, keyword_dir)
    except Exception as e:
        print(f"An error occurred during sorting: {e}")


if __name__ == "__main__":
    organize_desktop()
