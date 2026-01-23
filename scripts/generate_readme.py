import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_markdown_files():
    """모든 .md 파일을 찾아서 계층 구조로 분류"""
    structure = defaultdict(lambda: defaultdict(list))
    all_files = []

    for root, dirs, files in os.walk('.'):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in ['.git', '.github', 'scripts', 'node_modules', '.idea']]

        for file in files:
            if file.endswith('.md') and file != 'README.md':
                file_path = os.path.join(root, file)
                path_parts = Path(root).parts

                # 폴더 구조 파악: 기술/작성자/파일
                if len(path_parts) >= 3:  # ./기술/작성자
                    tech_category = path_parts[1]  # JPA, Spring, Redis 등
                    author = path_parts[2]  # 김채우, 조윤호 등
                elif len(path_parts) == 2:  # ./기술
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
                    'filename': file,
                    'path': file_path.replace('\\', '/').lstrip('./'),
                    'modified': os.path.getmtime(file_path)
                }

                if author:
                    structure[tech_category][author].append(file_info)
                else:
                    structure[tech_category]['_root'].append(file_info)

                all_files.append(file_info)

    return structure, all_files

def generate_readme():
    """README.md 생성"""
    structure, all_files = get_markdown_files()

    readme_content = f"""# TIL (Today I Learned)

> 팀원들이 매일 배운 내용을 기록합니다.

[![Auto-update README](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'username/repo')}/actions/workflows/update-readme.yml/badge.svg)](https://github.com/{os.getenv('GITHUB_REPOSITORY', 'username/repo')}/actions/workflows/update-readme.yml)

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📚 목차

"""

    # 기술 카테고리별로 정리
    for tech_category in sorted(structure.keys()):
        readme_content += f"\n### {tech_category}\n\n"

        authors = structure[tech_category]

        # 작성자별로 정리
        for author in sorted(authors.keys()):
            if author == '_root':
                # 작성자 폴더 없이 바로 있는 파일들
                files = sorted(authors[author], key=lambda x: x['modified'], reverse=True)
                for file_info in files:
                    readme_content += f"- [{file_info['title']}]({file_info['path']})\n"
            else:
                readme_content += f"\n**👤 {author}**\n\n"
                files = sorted(authors[author], key=lambda x: x['modified'], reverse=True)
                for file_info in files:
                    readme_content += f"- [{file_info['title']}]({file_info['path']})\n"
                readme_content += "\n"

    # 최근 업데이트 파일 목록 추가
    readme_content += "\n---\n\n## 📝 최근 업데이트\n\n"

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
