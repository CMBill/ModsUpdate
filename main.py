import requests
import pandas as pd
import json


# 获取某一mod所有的文件列表并以数据框返回
def get_files(modid):
    headers = {
        'Accept': 'application/json',
        'x-api-key': '$2a$10$LhtoxmW9RQT3gXvSQDgXZuTRAwXKzZMlzcY0CKj5LNVC7o61en7ga'
    }
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
            elif gameVersions[j] == 'Rift':
                modloader = 'Rift'
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
def get_url(files_meta, loader, gver):
    meta_select = files_meta.loc[files_meta['modloader'] == loader, ]
    meta_select = meta_select.loc[meta_select['MCVersions'] == gver, ]
    download_url = meta_select.loc[meta_select['fileDate'] == meta_select.loc[:, 'fileDate'].max(), 'downloadUrl'].at[0]
    return download_url


def main():
    with open('./config.json') as config_meta:
        config = json.load(config_meta)

    gamever = config['MC_Version']
    modloader = config['Mod_loader']
    modids = config['ModIDs']
    d_urls = []

    for i in range(len(modids)):
        modid = modids[i]
        files_meta = get_files(modid)
        d_url = get_url(files_meta, modloader, gamever)
        d_urls.append(d_url)
    downloadUrls = json.dumps(d_urls)
    return downloadUrls


if __name__ == '__main__':
    main()
