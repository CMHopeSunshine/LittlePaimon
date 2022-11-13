import datetime
from pathlib import Path

import git
from git.exc import GitCommandError, InvalidGitRepositoryError
from nonebot.utils import run_sync

from . import __version__, NICKNAME
from .requests import aiorequests


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
        if str(local_commit) == commit['sha']:
            break
        remote_commit.append(commit)
    if not remote_commit:
        return f'当前已是最新版本：{__version__}'
    result = '检查到更新，日志如下：\n'
    for i, commit in enumerate(remote_commit, start=1):
        time_str = (datetime.datetime.strptime(commit['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        result += f'{i}.{time_str}\n' + commit['commit']['message'].replace(':bug:', '🐛').replace(
            ':sparkles:', '✨').replace(':memo:', '📝') + '\n'
    return result


@run_sync
def update():
    try:
        repo = git.Repo(Path().absolute())
    except InvalidGitRepositoryError:
        return '没有发现git仓库，无法通过git更新'
    origin = repo.remotes.origin
    # repo.git.stash()
    try:
        origin.pull()
    except GitCommandError as e:
        return f'更新失败，错误信息：{e}，请手动进行更新'
    # finally:
    #     repo.git.stash('pop')
    return f'更新完成，版本：{__version__}\n最新更新日志为：\n{repo.head.commit.message.replace(":bug:", "🐛").replace(":sparkles:", "✨").replace(":memo:", "📝")}\n可使用命令[@bot 重启]重启{NICKNAME}'
