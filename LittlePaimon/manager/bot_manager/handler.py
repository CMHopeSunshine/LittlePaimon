from pathlib import Path
import time
import git
from nonebot.utils import run_sync
from git.exc import GitCommandError, InvalidGitRepositoryError
from LittlePaimon import __version__, NICKNAME
from LittlePaimon.utils import aiorequests


async def check_update():
    resp = await aiorequests.get('https://api.github.com/repos/CMHopeSunshine/LittlePaimon/commits')
    data = resp.json()
    if not isinstance(data, list):
        return '检查更新失败，可能是网络问题，请稍后再试'
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git检查更新'
    local_commit = repo.head.commit
    remote_commit = []
    for commit in data:
        if local_commit.binsha == commit['sha']:
            break
        remote_commit.append(commit)
    if not remote_commit:
        return f'当前已是最新版本：{__version__}'
    result = '检查到更新，日志如下：\n'
    for i, commit in enumerate(remote_commit, start=1):
        result += f'{i}.{commit["commit"]["committer"]["date"].replace("T", " ").replace("Z", "")}\n' + commit['commit']['message'].replace(':bug:', '🐛').replace(
            ':sparkles:', '✨').replace(':memo:', '📝') + '\n'
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
