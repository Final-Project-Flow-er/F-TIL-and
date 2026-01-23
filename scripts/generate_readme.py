import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_markdown_files():
    """모든 .md 파일을 찾아서 기술/작성자 구조로 분류"""
    structure = defaultdict(lambda: defaultdict(list))
    all_files = []

    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in ['.git', '.github', 'scripts', 'node_modules', '.idea']]

        for file in files:
            if file.endswith('.md') and file != 'README.md':
                file_path = os.path.join(root, file)
                path_parts = Path(root).parts

                # 폴더 구조: ./기술/작성자/파일.md
                if len(path_parts) >= 3:
                    tech_category = path_parts[1]  # 첫 번째 폴더 = 기술 (JPA, Spring, Redis 등)
                    author = path_parts[2]         # 두 번째 폴더 = 작성자
                elif len(path_parts) == 2:
                    tech_category = path_parts[1]
                    author = None
                else:
                    tech_category = 'Uncategorized'
                    author = None

                # 파일의 첫 줄을 제목으로 사용
                title = file.replace('.md', '').replace('_', ' ').replace('-', ' ')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            title = first_line.lstrip('#').strip()
                except:
                    pass

                file_info = {
                    'title': title,
                    'path': file_path.replace('\\', '/').lstrip('./'),
                    'modified': os.path.getmtime(file_path),
                    'author': author
                }

                if author:
                    structure[tech_category][author].append(file_info)
                else:
                    structure[tech_category]['_no_author'].append(file_info)

                all_files.append(file_info)

    return structure, all_files

def generate_readme():
    """README.md 생성"""
    structure, all_files = get_markdown_files()

    readme_content = f"""# 📚 TIL (Today I Learned)

> 팀원들이 매일 배운 내용을 기록합니다.

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📖 목차

"""

    # 기술 카테고리별로 정리 (알파벳순)
    for tech_category in sorted(structure.keys()):
        # 기술 카테고리 헤더 출력 (여기가 중요!)
        readme_content += f"\n### {tech_category}\n"

        authors_dict = structure[tech_category]

        # 작성자별로 정리 (가나다순)
        for author in sorted([a for a in authors_dict.keys() if a != '_no_author']):
            readme_content += f"\n**👤 {author}**\n\n"
            files = sorted(authors_dict[author], key=lambda x: x['modified'], reverse=True)
            for file_info in files:
                readme_content += f"- [{file_info['title']}]({file_info['path']})\n"

        # 작성자 폴더 없는 파일들
        if '_no_author' in authors_dict:
            files = sorted(authors_dict['_no_author'], key=lambda x: x['modified'], reverse=True)
            for file_info in files:
                readme_content += f"- [{file_info['title']}]({file_info['path']})\n"

        readme_content += "\n"

    # 최근 업데이트
    readme_content += "---\n\n## 📝 최근 업데이트\n\n"

    recent_files = sorted(all_files, key=lambda x: x['modified'], reverse=True)[:10]
    for file_info in recent_files:
        modified_date = datetime.fromtimestamp(file_info['modified']).strftime('%Y-%m-%d')
        author_info = f" - {file_info['author']}" if file_info['author'] else ""
        readme_content += f"- **{modified_date}** - [{file_info['title']}]({file_info['path']}){author_info}\n"

    readme_content += f"\n---\n\n**Total**: {len(all_files)} TILs\n"

    # README.md 쓰기
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ README.md 업데이트 완료!")
    print(f"📂 기술 카테고리: {', '.join(sorted(structure.keys()))}")
    print(f"📊 총 {len(all_files)}개 TIL")

if __name__ == '__main__':
    generate_readme()
