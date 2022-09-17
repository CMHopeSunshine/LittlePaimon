from pathlib import Path
import time
import git
from nonebot.utils import run_sync
from git.exc import GitCommandError, InvalidGitRepositoryError
from LittlePaimon import __version__, NICKNAME


def time_str(timestamp: int) -> str:
    time_local = time.localtime(timestamp)
    return time.strftime("%m-%d %H:%M:%S", time_local)


@run_sync
def check_update():
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git检查更新'
    local_commit = repo.head.commit
    remote_commit = []
    for commit in repo.iter_commits(max_count=15):
        if local_commit == commit:
            break
        remote_commit.append(commit)
    if not remote_commit:
        return f'当前已是最新版本：{__version__}'
    i = 1
    result = '检查到更新，日志如下：\n'
    for commit in remote_commit:
        if isinstance(commit.message, str):
            result += f'{i}.{time_str(commit.committed_date)}\n' + commit.message.replace(':bug:', '🐛').replace(
                ':sparkles:', '✨').replace(':memo:', '📝') + '\n'
            i += 1
    return result


@run_sync
def update():
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git更新'
    origin = repo.remotes.origin
    repo.git.stash()
    try:
        origin.pull()
    except GitCommandError as e:
        return f'更新失败，错误信息：{e}，请手动进行更新'
    finally:
        repo.git.stash('pop')
    return f'更新完成，版本：{__version__}\n可使用命令[@bot 重启]重启{NICKNAME}'
