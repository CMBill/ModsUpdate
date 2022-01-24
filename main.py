import requests
import pandas as pd

headers = {
    'Accept': 'application/json',
    'x-api-key': '$2a$10$LhtoxmW9RQT3gXvSQDgXZuTRAwXKzZMlzcY0CKj5LNVC7o61en7ga'
}


# 获取某一mod所有的文件列表并以数据框返回
def get_files(modid):
    url = 'https://api.curseforge.com/v1/mods/' + modid + '/files'
    r = requests.get(url, headers=headers)
    r_meta = r.json()

    files_meta = pd.DataFrame(columns=['fileID', 'fileDate', 'modloader', 'MCVersions', 'downloadUrl'])
    for i in range(len(r_meta['data'])):
        gameVersions = r_meta['data'][i]['gameVersions']
        MCVers = []
        modloader = 'Forge'  # 认为modloader默认为Forge，待进一步确定
        for j in range(len(gameVersions)):
            if gameVersions[j] == 'Fabric':
                modloader = 'Fabric'
            elif gameVersions[j] == 'Forge':
                modloader = 'Forge'
            else:
                MCVers.append(gameVersions[j])

        meta_i = pd.DataFrame({'fileID': r_meta['data'][i]['id'],
                               'fileDate': r_meta['data'][i]['fileDate'],
                               'modloader': modloader,
                               'MCVersions': MCVers,
                               'downloadUrl': r_meta['data'][i]['downloadUrl']})
        files_meta = files_meta.append(meta_i)

    return files_meta


# 根据需求从数据框中返回下载Url
def get_url(files_meta):

    return download_url
