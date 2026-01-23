import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_markdown_files():
    """모든 .md 파일을 찾아서 카테고리별로 분류"""
    files_by_category = defaultdict(list)

    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in ['.git', '.github', 'scripts']]

        for file in files:
            if file.endswith('.md') and file != 'README.md':
                file_path = os.path.join(root, file)
                category = Path(root).parts[1] if len(Path(root).parts) > 1 else 'Uncategorized'

                # 파일의 첫 줄을 제목으로 사용
                title = file.replace('.md', '').replace('_', ' ').replace('-', ' ')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            title = first_line.lstrip('#').strip()
                except:
                    pass

                files_by_category[category].append({
                    'title': title,
                    'path': file_path.replace('\\', '/').lstrip('./'),
                    'modified': os.path.getmtime(file_path)
                })

    return files_by_category

def generate_readme():
    """README.md 생성"""
    files_by_category = get_markdown_files()

    readme_content = f"""# TIL (Today I Learned)

> 매일 배운 내용을 기록합니다.

[![Auto-update README](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'username/repo')}/actions/workflows/update-readme.yml/badge.svg)](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'username/repo')}/actions/workflows/update-readme.yml)

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 목차

"""

    # 카테고리별 목차 생성
    for category in sorted(files_by_category.keys()):
        readme_content += f"\n### {category}\n\n"
        files = sorted(files_by_category[category], key=lambda x: x['modified'], reverse=True)

        for file_info in files:
            readme_content += f"- [{file_info['title']}]({file_info['path']})\n"

    # 최근 업데이트 파일 목록 추가
    readme_content += "\n---\n\n## 📝 최근 업데이트\n\n"
    all_files = []
    for files in files_by_category.values():
        all_files.extend(files)

    recent_files = sorted(all_files, key=lambda x: x['modified'], reverse=True)[:10]
    for file_info in recent_files:
        modified_date = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d')
        readme_content += f"- **{modified_date}** - [{file_info['title']}]({file_info['path']})\n"

    readme_content += f"\n---\n\n**Total**: {len(all_files)} TILs\n"

    # README.md 파일 쓰기
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✅ README.md가 성공적으로 업데이트되었습니다!")

if __name__ == '__main__':
    generate_readme()
