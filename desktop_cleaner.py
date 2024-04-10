import os
import shutil
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

parent_dir = os.path.expanduser("~/Desktop")
files_dict = {
    "Documents": [".pdf", ".docx", ".doc", ".txt",".pptx", ".xls"],
    "Images": [".png", ".jpg", ".jpeg"],
    "Videos": [".mp4", ".gif", ".mkv"],
    "Audio": [".mp3", ".wav"],
    "Archives": [".zip", ".rar"],
    "Data": [".xls", ".csv", ".json", ".xml", ".sql", ".json"],
    "Code": [".py", ".c", ".js", ".html", ".css", ".dart", ".h"],
    "Font": [".ttf", ".otf"],
    "Other": []
}


def create_directory_if_not_exists(directory):
    """Create a new directory if it does not exist"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Creating {os.path.basename(directory)} directory...")
    except Exception as e:
        print(f"Error creating directory: {e}")


def move_file(source, destination):
    """Moves a file from the source to destination directory"""
    try:
        if os.path.isfile(source):
            if not os.path.exists(destination):
                shutil.move(source, destination)
                print(f"Moving {os.path.basename(source)} to {destination}...")
            else:
                pass
    except Exception as e:
        print(f"Error moving file: {e}")


def organize_desktop():
    """Organizes files in the desktop by grouping by
    different file extensions"""
    try:
        if os.path.exists(parent_dir):
            files_moved = False
            for root, _, files in os.walk(parent_dir):
                for item in files:
                    matched = False
                    for dir_name, extensions in files_dict.items():
                        if any(item.lower().endswith(extension)
                            for extension in extensions):
                            dest_dir = os.path.join(parent_dir, dir_name)
                            create_directory_if_not_exists(dest_dir)
                            source_path = os.path.join(root, item)
                            dest_path = os.path.join(dest_dir, item)
                            if not os.path.exists(dest_path):
                                move_file(source_path, dest_path)
                                matched = True
                            sort_by_keyword(dest_dir)
                            break

                    if not matched:
                        dest_dir = os.path.join(parent_dir, "Other")
                        create_directory_if_not_exists(dest_dir)
                        source_path = os.path.join(parent_dir, item)
                        dest_path = os.path.join(dest_dir, item)
                        if not os.path.exists(dest_path):
                            move_file(source_path, dest_path)
                        sort_by_keyword(dest_dir)
                if not files_moved:
                    print("Your desktop appears to be organized already.")
                    break
                else:
                    print("Organization complete!")
    except Exception as e:
        print(f"An error occurred during organization: {e}")

def sort_by_keyword(directory):
    """Sorts files by repeated keywords in their filenames"""
    try:
        keyword_count = {}
        for root, _, files in os.walk(directory):
            for filename in files:
                dest_path = os.path.join(root, filename)
                keywords = extract_keywords(filename)
                for keyword in keywords:
                    if keyword not in keyword_count:
                        keyword_count[keyword] = []
                    keyword_count[keyword].append(dest_path)
                    break

        for keyword, files in keyword_count.items():
            if len(files) > 1:
                keyword_dir = os.path.join(directory, keyword.capitalize())
                create_directory_if_not_exists(keyword_dir)
                for file in files:
                    source_path = file
                    dest_path = os.path.join(keyword_dir, os.path.basename(file))
                    move_file(source_path, dest_path)
    except Exception as e:
        print(f"An error occurred during sorting: {e}")


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




if __name__ == "__main__":
    """Entry point"""
    organize_desktop()
